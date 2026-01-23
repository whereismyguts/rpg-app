<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { auth } from '../stores/auth.js';
  import { api } from '../api.js';

  const dispatch = createEventDispatcher();

  let loading = true;
  let error = '';
  let qrBase64 = '';
  let showQR = false;

  onMount(async () => {
    await refreshData();
  });

  async function refreshData() {
    loading = true;
    error = '';
    try {
      const user = await api.getMe();
      auth.updateBalance(user.balance);
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
      error = 'Failed to load QR code';
    }
  }
</script>

<div class="terminal">
  <div class="terminal-header">
    <p class="text-dim">LOGGED IN AS</p>
    <h2 class="terminal-title">{$auth.name}</h2>
    <p class="text-dim">ID: {$auth.playerUuid}</p>
  </div>

  {#if loading}
    <div class="loading">
      <p>LOADING DATA<span class="loading-cursor">_</span></p>
    </div>
  {:else}
    <div class="balance-display">
      <p class="balance-label">Balance</p>
      <p>{$auth.balance} <span class="text-amber">CAPS</span></p>
    </div>

    <hr class="separator" />

    <button
      class="btn btn-block btn-amber"
      on:click={() => dispatch('scan')}
    >
      [ SCAN QR CODE ]
    </button>

    <button
      class="btn btn-block"
      style="margin-top: 12px;"
      on:click={() => dispatch('navigate', 'stats')}
    >
      [ VIEW STATS ]
    </button>

    <button
      class="btn btn-block"
      style="margin-top: 12px;"
      on:click={loadQR}
    >
      [ SHOW MY QR ]
    </button>

    {#if showQR && qrBase64}
      <div class="qr-container">
        <img
          class="qr-image"
          src="data:image/png;base64,{qrBase64}"
          alt="Player QR Code"
        />
        <p class="text-dim" style="margin-top: 12px;">
          Scan to receive caps
        </p>
        <button
          class="btn"
          style="margin-top: 12px;"
          on:click={() => showQR = false}
        >
          HIDE
        </button>
      </div>
    {/if}

    {#if error}
      <div class="message message-error">
        ERROR: {error}
      </div>
    {/if}

    <button
      class="btn btn-block text-dim"
      style="margin-top: 24px; border-color: var(--terminal-green-dim);"
      on:click={refreshData}
    >
      [ REFRESH ]
    </button>

    <button
      class="btn btn-block text-danger"
      style="margin-top: 12px;"
      on:click={() => dispatch('logout')}
    >
      [ LOGOUT ]
    </button>
  {/if}
</div>
