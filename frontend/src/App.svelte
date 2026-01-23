<script>
  import { onMount } from 'svelte';
  import { auth } from './stores/auth.js';
  import { api } from './api.js';

  import Login from './components/Login.svelte';
  import Home from './components/Home.svelte';
  import Stats from './components/Stats.svelte';
  import Transfer from './components/Transfer.svelte';
  import QRScanner from './components/QRScanner.svelte';
  import PayItem from './components/PayItem.svelte';
  import ApplyPerk from './components/ApplyPerk.svelte';

  let currentPage = 'home';
  let loading = true;

  // QR scan result data
  let scanResult = null;
  let scanError = '';

  onMount(async () => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();

      if (window.Telegram.WebApp.initData) {
        try {
          const result = await api.login(window.Telegram.WebApp.initData, null, null);
          if (result && result.player_uuid) {
            api.setPlayerUuid(result.player_uuid);
            auth.login(result);
            loading = false;
            return;
          }
        } catch (e) {
          console.log('No bot session, showing login');
        }
      }
    }

    const savedUuid = auth.restore();
    if (savedUuid) {
      try {
        api.setPlayerUuid(savedUuid);
        const user = await api.getMe();
        auth.login(user);
      } catch (e) {
        auth.logout();
      }
    }

    loading = false;
  });

  function handleLogin(event) {
    const userData = event.detail;
    api.setPlayerUuid(userData.player_uuid);
    auth.login(userData);
  }

  function handleLogout() {
    auth.logout();
    api.setPlayerUuid(null);
  }

  function navigate(page) {
    currentPage = page;
    scanResult = null;
    scanError = '';
  }

  async function handleQRScan(event) {
    const qrData = event.detail.data;
    scanError = '';

    try {
      const parsed = await api.parseQR(qrData);

      if (parsed.type === 'login') {
        // login - if not authenticated, log in
        if (!$auth.isAuthenticated) {
          const result = await api.login(null, parsed.data.player_uuid, null);
          api.setPlayerUuid(result.player_uuid);
          auth.login(result);
        }
        currentPage = 'home';
      } else if (parsed.type === 'pay') {
        // pay for item
        scanResult = { type: 'pay', item: parsed.data };
        currentPage = 'pay';
      } else if (parsed.type === 'send') {
        // send money - prefill recipient
        scanResult = { type: 'send', recipient: parsed.data };
        currentPage = 'send';
      } else if (parsed.type === 'perk') {
        // apply perk
        scanResult = { type: 'perk', perk: parsed.data };
        currentPage = 'perk';
      }
    } catch (e) {
      scanError = e.message;
    }
  }

  function openScanner() {
    currentPage = 'scan';
    scanResult = null;
    scanError = '';
  }
</script>

<div class="scanlines"></div>

{#if loading}
  <div class="page">
    <div class="loading">
      <p>ЗАГРУЗКА ТЕРМИНАЛА<span class="loading-cursor">_</span></p>
    </div>
  </div>
{:else if !$auth.isAuthenticated}
  <Login on:login={handleLogin} />
{:else}
  <nav class="nav">
    <button
      class="nav-btn"
      class:active={currentPage === 'home'}
      on:click={() => navigate('home')}
    >
      ГЛАВНАЯ
    </button>
    <button
      class="nav-btn"
      class:active={currentPage === 'stats'}
      on:click={() => navigate('stats')}
    >
      СТАТЫ
    </button>
    <button
      class="nav-btn scan-btn"
      class:active={currentPage === 'scan'}
      on:click={openScanner}
    >
      СКАН
    </button>
  </nav>

  <div class="page">
    {#if currentPage === 'home'}
      <Home on:navigate={(e) => navigate(e.detail)} on:logout={handleLogout} on:scan={openScanner} />
    {:else if currentPage === 'stats'}
      <Stats />
    {:else if currentPage === 'scan'}
      <div class="terminal">
        <div class="terminal-header">
          <h2 class="terminal-title">СКАНЕР</h2>
          <p class="text-dim">Наведите камеру на QR код</p>
        </div>
        {#if scanError}
          <div class="message message-error" style="margin-bottom: 16px;">
            ОШИБКА: {scanError}
          </div>
        {/if}
        <QRScanner
          on:scan={handleQRScan}
          on:cancel={() => navigate('home')}
        />
      </div>
    {:else if currentPage === 'send'}
      <Transfer
        recipient={scanResult?.recipient}
        on:complete={() => navigate('home')}
      />
    {:else if currentPage === 'pay'}
      <PayItem
        item={scanResult?.item}
        on:complete={() => navigate('home')}
        on:cancel={() => navigate('home')}
      />
    {:else if currentPage === 'perk'}
      <ApplyPerk
        perk={scanResult?.perk}
        on:complete={() => navigate('home')}
        on:cancel={() => navigate('home')}
      />
    {/if}
  </div>
{/if}

<style>
  .scan-btn {
    background: var(--terminal-amber) !important;
    color: #000 !important;
  }

  .scan-btn:hover {
    background: #ffcc00 !important;
  }
</style>
