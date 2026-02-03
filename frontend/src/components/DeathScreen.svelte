<script>
  import { createEventDispatcher } from 'svelte';
  import { api } from '../api.js';
  import { auth } from '../stores/auth.js';

  const dispatch = createEventDispatcher();

  let loading = false;
  let error = '';

  async function handleRespawn() {
    loading = true;
    error = '';

    try {
      const result = await api.respawn();
      auth.updateHp(result.new_hp);
      dispatch('respawn');
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="death-screen">
  <div class="death-content">
    <div class="skull">💀</div>
    <h1 class="death-title">ВЫ МЕРТВЫ</h1>
    <p class="death-text">Ваше путешествие по Пустоши закончилось...</p>

    <div class="death-warning">
      <p>При возрождении вы потеряете:</p>
      <ul>
        <li>Все перки</li>
        <li>Все временные эффекты</li>
      </ul>
      <p>HP будет восстановлено до 5</p>
    </div>

    {#if error}
      <div class="message message-error">
        {error}
      </div>
    {/if}

    <button
      class="btn btn-respawn"
      on:click={handleRespawn}
      disabled={loading}
    >
      {loading ? 'ВОЗРОЖДЕНИЕ...' : '[ ВОЗРОДИТЬСЯ ]'}
    </button>
  </div>
</div>

<style>
  .death-screen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: #0a0a0a;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
  }

  .death-content {
    text-align: center;
    padding: 32px;
    max-width: 400px;
  }

  .skull {
    font-size: 80px;
    margin-bottom: 16px;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
  }

  .death-title {
    font-size: 2.5rem;
    color: var(--error-red, #ff4444);
    text-transform: uppercase;
    letter-spacing: 4px;
    margin-bottom: 16px;
    text-shadow: 0 0 20px var(--error-red, #ff4444);
  }

  .death-text {
    color: var(--terminal-green-dim, #0a7f00);
    font-size: 1rem;
    margin-bottom: 24px;
  }

  .death-warning {
    background: rgba(255, 68, 68, 0.1);
    border: 1px solid var(--error-red, #ff4444);
    padding: 16px;
    margin-bottom: 24px;
    text-align: left;
  }

  .death-warning p {
    color: var(--terminal-amber, #ffb000);
    margin-bottom: 8px;
  }

  .death-warning ul {
    margin: 8px 0;
    padding-left: 20px;
    color: var(--terminal-green-dim, #0a7f00);
  }

  .death-warning li {
    margin: 4px 0;
  }

  .btn-respawn {
    background: transparent;
    border: 2px solid var(--error-red, #ff4444);
    color: var(--error-red, #ff4444);
    padding: 16px 32px;
    font-family: inherit;
    font-size: 1.1rem;
    cursor: pointer;
    text-transform: uppercase;
    letter-spacing: 2px;
    transition: all 0.3s ease;
  }

  .btn-respawn:hover:not(:disabled) {
    background: var(--error-red, #ff4444);
    color: #0a0a0a;
    box-shadow: 0 0 30px var(--error-red, #ff4444);
  }

  .btn-respawn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .message-error {
    padding: 12px;
    margin-bottom: 16px;
    border: 1px solid var(--error-red, #ff4444);
    background: rgba(255, 68, 68, 0.1);
    color: var(--error-red, #ff4444);
  }
</style>
