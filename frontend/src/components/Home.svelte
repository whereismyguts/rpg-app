<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { auth } from '../stores/auth.js';
  import { api } from '../api.js';
  import AttributeBar from './ui/AttributeBar.svelte';

  const dispatch = createEventDispatcher();

  let loading = true;
  let error = '';
  let qrBase64 = '';
  let userPerks = [];
  let stats = null;
  let transactions = [];
  let expandedPerk = null;
  let expandedEffect = null;
  let transactionsExpanded = false;
  let statsExpanded = false;
  let showRoleDescription = false;
  let now = Date.now();

  // update timer every second
  import { onDestroy } from 'svelte';
  const timerInterval = setInterval(() => {
    now = Date.now();
  }, 1000);
  onDestroy(() => clearInterval(timerInterval));

  function formatTimeLeft(expiresAt, currentTime) {
    const expires = new Date(expiresAt).getTime();
    const diff = expires - currentTime;
    if (diff <= 0) return 'истёк';
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    if (hours > 0) return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    return `${minutes}:${String(seconds).padStart(2, '0')}`;
  }

  function toggleEffect(idx) {
    expandedEffect = expandedEffect === idx ? null : idx;
  }

  onMount(async () => {
    await refreshData();
  });

  async function refreshData() {
    loading = true;
    error = '';
    try {
      const user = await api.getMe();
      auth.updateBalance(user.balance);
      auth.updateHp(user.hp);

      const [perksResult, statsResult, qrResult, txResult] = await Promise.all([
        api.getMyPerks(),
        api.getStats(),
        api.getQR(),
        api.getMyTransactions(20)
      ]);

      userPerks = perksResult.perks || [];
      stats = statsResult;
      qrBase64 = qrResult.qr_base64;
      transactions = txResult.transactions || [];
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function togglePerk(perkId) {
    if (expandedPerk === perkId) {
      expandedPerk = null;
    } else {
      expandedPerk = perkId;
    }
  }

  function formatTxDate(timestamp) {
    const d = new Date(timestamp);
    return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
  }
</script>

<div class="terminal">
  <div class="terminal-header">
    <h2 class="terminal-title">{$auth.name}</h2>
    {#if stats?.profession}
      <div class="profession-row">
        <p class="profession">{stats.profession}</p>
        {#if stats?.role_description}
          <button class="btn-info" on:click={() => showRoleDescription = true} title="Описание роли">?</button>
        {/if}
      </div>
    {/if}
    {#if stats?.band}
      <p class="text-dim band-info">Группировка: {stats.band}</p>
    {/if}
  </div>

  {#if loading}
    <div class="loading">
      <p>ЗАГРУЗКА<span class="loading-cursor">_</span></p>
    </div>
  {:else}
    <div class="stats-display">
      <div class="stat-item">
        <span class="stat-value hp-value">{$auth.hp}</span>
        <span class="stat-label">HP</span>
      </div>
      <div class="stat-item">
        <span class="stat-value caps-value">{$auth.balance}</span>
        <span class="stat-label">КРЫШЕК</span>
      </div>
    </div>

    <hr class="separator" />

    <button
      class="btn btn-block btn-amber"
      on:click={() => dispatch('scan')}
    >
      [ СКАНИРОВАТЬ QR ]
    </button>

    <div class="button-row">
      <button
        class="btn text-dim"
        on:click={refreshData}
      >
        [ ОБНОВИТЬ ]
      </button>
      <button
        class="btn text-danger"
        on:click={() => dispatch('logout')}
      >
        [ ВЫЙТИ ]
      </button>
    </div>

    {#if error}
      <div class="message message-error">
        ОШИБКА: {error}
      </div>
    {/if}

    <hr class="separator" />

    <div class="transactions-section">
      <button
        class="spoiler-toggle"
        on:click={() => transactionsExpanded = !transactionsExpanded}
      >
        <span class="section-title">ИСТОРИЯ</span>
        <span class="spoiler-arrow">{transactionsExpanded ? '▼' : '▶'}</span>
      </button>
      {#if transactionsExpanded}
        <div class="transactions-list">
          {#if transactions.length === 0}
            <p class="text-dim">Пока пусто</p>
          {:else}
            {#each transactions as tx}
              <div class="tx-item">
                <div class="tx-row">
                  <span class="tx-desc">{tx.description || ''}</span>
                  {#if tx.amount > 0}
                    {#if tx.tx_type === 'heal'}
                      <span class="tx-amount tx-income">+{tx.amount}</span>
                    {:else if tx.tx_type === 'damage'}
                      <span class="tx-amount tx-expense">-{tx.amount}</span>
                    {:else}
                      <span class="tx-amount" class:tx-income={tx.to_id === $auth.uuid} class:tx-expense={tx.from_id === $auth.uuid}>
                        {tx.to_id === $auth.uuid ? '+' : '-'}{tx.amount}
                      </span>
                    {/if}
                  {/if}
                </div>
                <div class="tx-row tx-details">
                  <span class="tx-date">{formatTxDate(tx.timestamp)}</span>
                </div>
              </div>
            {/each}
          {/if}
        </div>
      {/if}
    </div>

    {#if stats?.active_effects?.length > 0}
      <hr class="separator" />
      <div class="effects-section">
        <p class="section-title">ВРЕМЕННЫЕ ЭФФЕКТЫ</p>
        <div class="effects-list">
          {#each stats.active_effects as effect, idx}
            <button
              class="effect-item"
              class:expanded={expandedEffect === idx}
              on:click={() => toggleEffect(idx)}
            >
              <div class="effect-header">
                <span class="effect-name">{effect.item_name}</span>
                <span class="effect-timer">⏱ {formatTimeLeft(effect.expires_at, now)}</span>
              </div>
              {#if expandedEffect === idx}
                <div class="effect-details">
                  <span class="effect-type">{effect.effect_type.replace('attr_', '').toUpperCase()}</span>
                  <span class="effect-value">+{effect.effect_value}</span>
                </div>
              {/if}
            </button>
          {/each}
        </div>
      </div>
    {/if}

    {#if userPerks.length > 0}
      <hr class="separator" />
      <div class="perks-section">
        <p class="section-title">ПЕРКИ</p>
        <div class="perks-list">
          {#each userPerks as perk}
            <button
              class="perk-item"
              class:expanded={expandedPerk === perk.perk_id}
              on:click={() => togglePerk(perk.perk_id)}
            >
              <div class="perk-header">
                {#if perk.image_url}
                  <img src={perk.image_url} alt={perk.name} class="perk-image" />
                {/if}
                <span class="perk-name">{perk.name}</span>
                <span class="perk-arrow">{expandedPerk === perk.perk_id ? '▼' : '▶'}</span>
              </div>
              {#if expandedPerk === perk.perk_id && perk.description}
                <div class="perk-description">
                  {perk.description}
                </div>
              {/if}
            </button>
          {/each}
        </div>
      </div>
    {/if}

    {#if stats && stats.attributes && stats.attributes.length > 0}
      <hr class="separator" />
      <div class="stats-section">
        <button
          class="spoiler-toggle"
          on:click={() => statsExpanded = !statsExpanded}
        >
          <span class="section-title">S.P.E.C.I.A.L.</span>
          <span class="spoiler-arrow">{statsExpanded ? '▼' : '▶'}</span>
        </button>
        {#if statsExpanded}
          <div class="attributes-list">
            {#each stats.attributes as attr}
              <AttributeBar
                name={attr.display_name}
                value={attr.value}
                max={attr.max_value}
                description={attr.description}
                bonus={attr.bonus}
              />
            {/each}
          </div>
        {/if}
      </div>
    {/if}

    {#if qrBase64}
      <hr class="separator" />
      <div class="qr-section">
        <p class="text-dim qr-hint">ВАШ QR ДЛЯ ПОЛУЧЕНИЯ КРЫШЕК</p>
        <img
          class="qr-image"
          src="data:image/png;base64,{qrBase64}"
          alt="QR код игрока"
        />
      </div>
    {/if}
  {/if}
</div>

{#if showRoleDescription && stats?.role_description}
  <div class="modal-overlay" on:click={() => showRoleDescription = false} on:keydown={(e) => e.key === 'Escape' && (showRoleDescription = false)}>
    <div class="modal-content" on:click|stopPropagation>
      <div class="modal-header">
        <h3>Описание роли</h3>
        <button class="modal-close" on:click={() => showRoleDescription = false}>&times;</button>
      </div>
      <div class="modal-body">
        <p class="role-description-text">{stats.role_description}</p>
      </div>
    </div>
  </div>
{/if}

<style>
  .profession-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-top: 4px;
  }

  .profession {
    font-size: 0.85rem;
    color: var(--terminal-green-dim);
    margin: 0;
  }

  .btn-info {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border: 1px solid var(--terminal-green-dim);
    background: transparent;
    color: var(--terminal-green);
    font-size: 0.75rem;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    font-family: inherit;
  }

  .btn-info:hover {
    border-color: var(--terminal-green);
    background: rgba(20, 255, 0, 0.1);
  }

  .band-info {
    font-size: 0.8rem;
    margin-top: 8px;
  }

  .stats-display {
    display: flex;
    justify-content: center;
    gap: 32px;
    padding: 16px;
  }

  .stat-item {
    text-align: center;
  }

  .stat-value {
    font-size: 1.5rem;
    display: block;
  }

  .stat-label {
    font-size: 0.75rem;
    color: var(--terminal-green-dim);
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .hp-value {
    color: var(--error-red);
  }

  .caps-value {
    color: var(--terminal-amber);
  }

  .button-row {
    display: flex;
    gap: 12px;
    margin-top: 12px;
  }

  .button-row .btn {
    flex: 1;
  }

  .section-title {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--terminal-amber);
    margin-bottom: 12px;
    text-align: center;
  }

  .transactions-section {
    margin-top: 16px;
  }

  .spoiler-toggle {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 10px 12px;
    background: transparent;
    border: 1px dashed var(--terminal-green-dim);
    cursor: pointer;
    font-family: inherit;
    color: var(--terminal-green);
  }

  .spoiler-toggle:hover {
    border-color: var(--terminal-green);
  }

  .spoiler-toggle .section-title {
    margin-bottom: 0;
  }

  .spoiler-arrow {
    font-size: 0.8rem;
    color: var(--terminal-green-dim);
  }

  .transactions-list {
    margin-top: 12px;
    max-height: 300px;
    overflow-y: auto;
  }

  .tx-item {
    padding: 8px 10px;
    border-bottom: 1px dashed var(--terminal-green-dim);
  }

  .tx-item:last-child {
    border-bottom: none;
  }

  .tx-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .tx-type {
    font-size: 0.85rem;
    color: var(--terminal-green-dim);
    text-transform: uppercase;
  }

  .tx-amount {
    font-size: 1rem;
    font-weight: bold;
  }

  .tx-income {
    color: var(--terminal-green);
  }

  .tx-expense {
    color: var(--terminal-amber);
  }

  .tx-details {
    margin-top: 4px;
  }

  .tx-desc {
    font-size: 0.8rem;
    color: var(--terminal-green-dim);
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .tx-date {
    font-size: 0.75rem;
    color: var(--terminal-green-dim);
    opacity: 0.7;
  }

  .stats-section {
    margin-top: 16px;
  }

  .attributes-list {
    margin-top: 12px;
  }

  .perks-section {
    margin-top: 16px;
  }

  .perks-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .perk-item {
    display: block;
    width: 100%;
    padding: 10px 12px;
    border: 1px solid var(--terminal-green-dim);
    background: rgba(20, 255, 0, 0.05);
    cursor: pointer;
    text-align: left;
    font-family: 'Courier New', Courier, monospace;
    color: var(--terminal-green);
    transition: all 0.2s ease;
  }

  .perk-item:hover {
    background: rgba(20, 255, 0, 0.1);
    border-color: var(--terminal-green);
  }

  .perk-item.expanded {
    border-color: var(--terminal-amber);
    background: rgba(255, 176, 0, 0.1);
  }

  .perk-header {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .perk-image {
    width: 32px;
    height: 32px;
    object-fit: cover;
    border: 1px solid var(--terminal-green-dim);
  }

  .perk-name {
    flex: 1;
    font-size: 0.95rem;
  }

  .perk-arrow {
    font-size: 0.8rem;
    color: var(--terminal-green-dim);
  }

  .perk-description {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px dashed var(--terminal-green-dim);
    font-size: 0.85rem;
    color: var(--terminal-green-dim);
    line-height: 1.5;
  }

  .qr-section {
    text-align: center;
    padding: 16px 0;
    margin-top: 16px;
  }

  .qr-hint {
    font-size: 0.8rem;
    margin-bottom: 12px;
    letter-spacing: 1px;
  }

  .qr-image {
    max-width: 160px;
    border: 2px solid var(--terminal-green);
  }

  .effects-section {
    margin-top: 16px;
  }

  .effects-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .effect-item {
    display: block;
    width: 100%;
    padding: 10px 12px;
    border: 1px solid var(--terminal-amber);
    background: rgba(255, 176, 0, 0.1);
    cursor: pointer;
    text-align: left;
    font-family: inherit;
    color: var(--terminal-amber);
    transition: all 0.2s ease;
  }

  .effect-item:hover {
    background: rgba(255, 176, 0, 0.2);
  }

  .effect-item.expanded {
    border-width: 2px;
  }

  .effect-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .effect-name {
    font-size: 0.95rem;
  }

  .effect-timer {
    font-size: 0.85rem;
    opacity: 0.8;
  }

  .effect-details {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed var(--terminal-amber);
    display: flex;
    justify-content: space-between;
  }

  .effect-type {
    font-size: 0.8rem;
    opacity: 0.8;
  }

  .effect-value {
    font-size: 1rem;
    font-weight: bold;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 20px;
  }

  .modal-content {
    background: var(--terminal-bg, #0a0a0a);
    border: 2px solid var(--terminal-green);
    max-width: 500px;
    width: 100%;
    max-height: 80vh;
    overflow-y: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    border-bottom: 1px solid var(--terminal-green-dim);
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1rem;
    color: var(--terminal-amber);
  }

  .modal-close {
    background: transparent;
    border: none;
    color: var(--terminal-green);
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    line-height: 1;
  }

  .modal-close:hover {
    color: var(--terminal-amber);
  }

  .modal-body {
    padding: 16px;
  }

  .role-description-text {
    font-size: 0.9rem;
    line-height: 1.6;
    color: var(--terminal-green);
    white-space: pre-wrap;
    margin: 0;
  }
</style>
