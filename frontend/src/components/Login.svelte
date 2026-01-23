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
  let showQRScanner = false;

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
      error = 'Введите ID игрока';
      return;
    }

    loading = true;
    error = '';

    try {
      const result = await api.login(
        null,
        playerUuid.trim().toUpperCase(),
        passwordEnabled ? password : null
      );
      dispatch('login', result);
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function handleQRScan(event) {
    playerUuid = event.detail.data;
    showQRScanner = false;
  }

  function handleKeydown(event) {
    if (event.key === 'Enter') {
      handleLogin();
    }
  }
</script>

<div class="page">
  <div class="terminal">
    <div class="terminal-header">
      <h1 class="terminal-title">Терминал Vault-Tec</h1>
      <p class="text-dim">ROBCO INDUSTRIES UNIFIED OPERATING SYSTEM</p>
    </div>

    {#if showQRScanner}
      <QRScanner on:scan={handleQRScan} on:cancel={() => showQRScanner = false} />
    {:else}
      <div class="form-group">
        <label>ID игрока</label>
        <input
          type="text"
          bind:value={playerUuid}
          placeholder="Введите ID"
          on:keydown={handleKeydown}
          disabled={loading}
        />
      </div>

      <button
        class="btn btn-block"
        style="margin-bottom: 16px;"
        on:click={() => showQRScanner = true}
        disabled={loading}
      >
        [ СКАНИРОВАТЬ QR ]
      </button>

      {#if passwordEnabled}
        <div class="form-group">
          <label>Пароль</label>
          <input
            type="password"
            bind:value={password}
            placeholder="Введите пароль"
            on:keydown={handleKeydown}
            disabled={loading}
          />
        </div>
      {/if}

      {#if error}
        <div class="message message-error">
          ОШИБКА: {error}
        </div>
      {/if}

      <button
        class="btn btn-block btn-amber"
        on:click={handleLogin}
        disabled={loading}
      >
        {loading ? 'АВТОРИЗАЦИЯ...' : '[ ВОЙТИ ]'}
      </button>
    {/if}
  </div>
</div>
