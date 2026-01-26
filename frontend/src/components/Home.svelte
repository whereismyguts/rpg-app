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
  let expandedPerk = null;
  let expandedEffect = null;
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

      const [perksResult, statsResult, qrResult] = await Promise.all([
        api.getMyPerks(),
        api.getStats(),
        api.getQR()
      ]);

      userPerks = perksResult.perks || [];
      stats = statsResult;
      qrBase64 = qrResult.qr_base64;
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
</script>

<div class="terminal">
  <div class="terminal-header">
    <h2 class="terminal-title">{$auth.name}</h2>
    {#if stats?.profession}
      <p class="profession">{stats.profession}</p>
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
    <div class="balance-display">
      <p class="balance-value">{$auth.balance} <span class="text-amber">КРЫШЕК</span></p>
    </div>

    <hr class="separator" />

    <button
      class="btn btn-block btn-amber"
      on:click={() => dispatch('scan')}
    >
      [ СКАНИРОВАТЬ QR ]
    </button>

    {#if stats && stats.attributes && stats.attributes.length > 0}
      <hr class="separator" />
      <div class="stats-section">
        <p class="section-title">S.P.E.C.I.A.L.</p>
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

    {#if error}
      <div class="message message-error">
        ОШИБКА: {error}
      </div>
    {/if}

    <button
      class="btn btn-block text-dim"
      style="margin-top: 24px; border-color: var(--terminal-green-dim);"
      on:click={refreshData}
    >
      [ ОБНОВИТЬ ]
    </button>

    <button
      class="btn btn-block text-danger"
      style="margin-top: 12px;"
      on:click={() => dispatch('logout')}
    >
      [ ВЫЙТИ ]
    </button>

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

<style>
  .profession {
    font-size: 0.85rem;
    color: var(--terminal-green-dim);
    margin-top: 4px;
  }

  .band-info {
    font-size: 0.8rem;
    margin-top: 8px;
  }

  .balance-value {
    font-size: 1.5rem;
    text-align: center;
  }

  .section-title {
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--terminal-amber);
    margin-bottom: 12px;
    text-align: center;
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
</style>
