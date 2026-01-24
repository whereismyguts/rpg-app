<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { auth } from '../stores/auth.js';
  import { api } from '../api.js';

  const dispatch = createEventDispatcher();

  let loading = true;
  let error = '';
  let qrBase64 = '';
  let showQR = false;
  let userPerks = [];

  onMount(async () => {
    await refreshData();
  });

  async function refreshData() {
    loading = true;
    error = '';
    try {
      const user = await api.getMe();
      auth.updateBalance(user.balance);

      const perksResult = await api.getMyPerks();
      userPerks = perksResult.perks || [];
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function loadQR() {
    try {
      const result = await api.getQR();
      qrBase64 = result.qr_base64;
      showQR = true;
    } catch (e) {
      error = 'Не удалось загрузить QR код';
    }
  }
</script>

<div class="terminal">
  <div class="terminal-header">
    <p class="text-dim">ВЫ ВОШЛИ КАК</p>
    <h2 class="terminal-title">{$auth.name}</h2>
    <p class="text-dim">ID: {$auth.playerUuid}</p>
  </div>

  {#if loading}
    <div class="loading">
      <p>ЗАГРУЗКА<span class="loading-cursor">_</span></p>
    </div>
  {:else}
    <div class="balance-display">
      <p class="balance-label">Баланс</p>
      <p>{$auth.balance} <span class="text-amber">КРЫШЕК</span></p>
    </div>

    <hr class="separator" />

    <button
      class="btn btn-block btn-amber"
      on:click={() => dispatch('scan')}
    >
      [ СКАНИРОВАТЬ QR ]
    </button>

    <button
      class="btn btn-block"
      style="margin-top: 12px;"
      on:click={() => dispatch('navigate', 'stats')}
    >
      [ ХАРАКТЕРИСТИКИ ]
    </button>

    <button
      class="btn btn-block"
      style="margin-top: 12px;"
      on:click={loadQR}
    >
      [ МОЙ QR КОД ]
    </button>

    {#if showQR && qrBase64}
      <div class="qr-container">
        <img
          class="qr-image"
          src="data:image/png;base64,{qrBase64}"
          alt="QR код игрока"
        />
        <p class="text-dim" style="margin-top: 12px;">
          Покажите для получения крышек
        </p>
        <button
          class="btn"
          style="margin-top: 12px;"
          on:click={() => showQR = false}
        >
          СКРЫТЬ
        </button>
      </div>
    {/if}

    {#if userPerks.length > 0}
      <hr class="separator" />
      <div class="perks-section">
        <p class="text-dim" style="margin-bottom: 8px;">АКТИВНЫЕ ПЕРКИ</p>
        <div class="perks-list">
          {#each userPerks as perk}
            <div class="perk-badge">
              {#if perk.image_url}
                <img src={perk.image_url} alt={perk.name} class="perk-image" />
              {/if}
              <span class="perk-name">{perk.name}</span>
            </div>
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
  {/if}
</div>

<style>
  .perks-section {
    margin-top: 16px;
  }
  .perks-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .perk-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    border: 1px solid var(--terminal-green-dim);
    background: rgba(20, 255, 0, 0.1);
    font-size: 12px;
  }
  .perk-image {
    width: 24px;
    height: 24px;
    object-fit: cover;
  }
  .perk-name {
    color: var(--terminal-green);
  }
</style>
