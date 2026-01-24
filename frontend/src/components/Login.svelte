<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { api } from '../api.js';
  import QRScanner from './QRScanner.svelte';

  const dispatch = createEventDispatcher();

  let playerUuid = '';
  let password = '';
  let error = '';
  let loading = false;
  let passwordEnabled = false;
  let showPasswordInput = false;
  let scannerKey = 0; // used to force scanner recreation
  let showError = false;

  onMount(async () => {
    try {
      const config = await api.getConfig();
      passwordEnabled = config.password_enabled;
    } catch (e) {
      // Ignore
    }
  });

  async function handleLogin() {
    if (!playerUuid.trim()) {
      error = 'Отсканируйте QR код';
      showError = true;
      return;
    }

    loading = true;
    error = '';
    showError = false;

    try {
      const result = await api.login(
        null,
        playerUuid.trim().toUpperCase(),
        passwordEnabled ? password : null
      );
      dispatch('login', result);
    } catch (e) {
      error = e.message;
      showError = true;
    } finally {
      loading = false;
    }
  }

  function handleQRScan(event) {
    let data = event.detail.data.trim().toUpperCase();

    // parse LOGIN:UUID format
    if (data.startsWith('LOGIN:')) {
      data = data.substring(6);
    }

    playerUuid = data;
    showError = false;

    // if password required, show password input
    if (passwordEnabled) {
      showPasswordInput = true;
    } else {
      handleLogin();
    }
  }

  function handlePasswordSubmit() {
    handleLogin();
  }

  function handleKeydown(event) {
    if (event.key === 'Enter') {
      handlePasswordSubmit();
    }
  }

  function tryScanAgain() {
    // reset state and increment key to recreate scanner
    playerUuid = '';
    error = '';
    showError = false;
    scannerKey++;
  }
</script>

<div class="page">
  <div class="terminal">
    <div class="terminal-header">
      <h1 class="terminal-title">Терминал Vault-Tec</h1>
      <p class="text-dim">ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM</p>
    </div>

    {#if showPasswordInput}
      <div class="scanned-info">
        <p class="text-dim">ID: {playerUuid}</p>
      </div>

      <div class="form-group">
        <label>Пароль</label>
        <input
          type="password"
          bind:value={password}
          placeholder="Введите пароль"
          on:keydown={handleKeydown}
          disabled={loading}
          autofocus
        />
      </div>

      {#if error}
        <div class="message message-error">
          ОШИБКА: {error}
        </div>
      {/if}

      <div style="display: flex; gap: 12px;">
        <button
          class="btn"
          style="flex: 1;"
          on:click={() => { showPasswordInput = false; playerUuid = ''; password = ''; }}
          disabled={loading}
        >
          НАЗАД
        </button>
        <button
          class="btn btn-amber"
          style="flex: 1;"
          on:click={handlePasswordSubmit}
          disabled={loading}
        >
          {loading ? 'ВХОД...' : 'ВОЙТИ'}
        </button>
      </div>
    {:else if showError}
      <div class="error-state">
        <div class="message message-error">
          ОШИБКА: {error}
        </div>
        <p class="text-dim" style="margin: 16px 0;">ID: {playerUuid}</p>
        <button class="btn btn-block btn-amber" on:click={tryScanAgain}>
          [ СКАНИРОВАТЬ СНОВА ]
        </button>
      </div>
    {:else}
      <div class="scan-prompt">
        <p>Отсканируйте ваш QR код для входа</p>
      </div>

      {#key scannerKey}
        <QRScanner on:scan={handleQRScan} on:cancel={tryScanAgain} />
      {/key}
    {/if}
  </div>
</div>

<style>
  .scan-prompt {
    text-align: center;
    padding: 16px 0;
    margin-bottom: 16px;
  }

  .scanned-info {
    text-align: center;
    padding: 12px;
    margin-bottom: 16px;
    border: 1px solid var(--terminal-green-dim);
  }

  .error-state {
    text-align: center;
    padding: 20px 0;
  }
</style>
