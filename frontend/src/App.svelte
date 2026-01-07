<script>
  import { onMount } from 'svelte';
  import { auth } from './stores/auth.js';
  import { api } from './api.js';

  import Login from './components/Login.svelte';
  import Home from './components/Home.svelte';
  import Stats from './components/Stats.svelte';
  import Transfer from './components/Transfer.svelte';

  let currentPage = 'home';
  let loading = true;
  let error = '';

  onMount(async () => {
    // Initialize Telegram WebApp if available
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
    }

    // Only restore from localStorage if user previously logged in via QR/UUID
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

    // No automatic Telegram auth - user must login via QR or UUID
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
  }
</script>

<div class="scanlines"></div>

{#if loading}
  <div class="page">
    <div class="loading">
      <p>INITIALIZING TERMINAL<span class="loading-cursor">_</span></p>
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
      HOME
    </button>
    <button
      class="nav-btn"
      class:active={currentPage === 'stats'}
      on:click={() => navigate('stats')}
    >
      STATS
    </button>
    <button
      class="nav-btn"
      class:active={currentPage === 'send'}
      on:click={() => navigate('send')}
    >
      SEND
    </button>
  </nav>

  <div class="page">
    {#if currentPage === 'home'}
      <Home on:navigate={(e) => navigate(e.detail)} on:logout={handleLogout} />
    {:else if currentPage === 'stats'}
      <Stats />
    {:else if currentPage === 'send'}
      <Transfer on:complete={() => navigate('home')} />
    {/if}
  </div>
{/if}
