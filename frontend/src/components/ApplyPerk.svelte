<script>
  import { createEventDispatcher } from 'svelte';
  import { auth } from '../stores/auth.js';
  import { api } from '../api.js';

  export let perk = null;
  export let alreadyApplied = false;

  const dispatch = createEventDispatcher();

  let loading = false;
  let error = '';
  let success = false;
  let result = null;

  function getEffectDescription(perk) {
    if (!perk) return '';
    const effectType = perk.effect_type || '';
    const effectValue = perk.effect_value || 0;
    const sign = effectValue > 0 ? '+' : '';

    const attrNames = {
      'attr_strength': 'СИЛА',
      'attr_perception': 'ВОСПРИЯТИЕ',
      'attr_endurance': 'ВЫНОСЛИВОСТЬ',
      'attr_charisma': 'ХАРИЗМА',
      'attr_intelligence': 'ИНТЕЛЛЕКТ',
      'attr_agility': 'ЛОВКОСТЬ',
      'attr_luck': 'УДАЧА',
    };

    if (effectType.startsWith('attr_')) {
      const attr = attrNames[effectType] || effectType.replace('attr_', '').toUpperCase();
      return `${attr} ${sign}${effectValue}`;
    } else if (effectType === 'balance') {
      return `Баланс ${sign}${effectValue} крышек`;
    }
    return '';
  }

  async function confirmApply() {
    loading = true;
    error = '';

    try {
      result = await api.applyPerk(perk.perk_id);
      auth.updateBalance(result.new_balance);
      success = true;
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="terminal">
  <div class="terminal-header">
    <h2 class="terminal-title">ПЕРК</h2>
  </div>

  {#if success}
    <div class="message message-success">
      <p>ПЕРК ПРИМЕНЁН!</p>
      <p style="margin-top: 8px;">Вы получили: {result.perk.name}</p>
      <p style="margin-top: 12px; font-size: 0.9rem;" class="text-dim">
        {result.perk.description}
      </p>
    </div>
    <button class="btn btn-block" on:click={() => dispatch('complete')}>
      [ ГОТОВО ]
    </button>
  {:else if perk}
    <div class="perk-card">
      <h3 class="perk-name">{perk.name}</h3>
      {#if perk.description}
        <p class="perk-description">{perk.description}</p>
      {/if}
      <div class="perk-effect">
        <span class="effect-label">ЭФФЕКТ:</span>
        <span class="effect-value text-amber">{getEffectDescription(perk)}</span>
      </div>
      {#if perk.one_time}
        <p class="perk-note">* Одноразовый</p>
      {/if}
    </div>

    {#if alreadyApplied}
      <div class="message message-error">
        Этот перк уже был применён!
      </div>
      <button class="btn btn-block" on:click={() => dispatch('cancel')}>
        [ НАЗАД ]
      </button>
    {:else}
      {#if error}
        <div class="message message-error">
          ОШИБКА: {error}
        </div>
      {/if}

      <div class="actions">
        <button class="btn" on:click={() => dispatch('cancel')}>
          ОТМЕНА
        </button>
        <button
          class="btn btn-amber"
          on:click={confirmApply}
          disabled={loading}
        >
          {loading ? 'ПРИМЕНЕНИЕ...' : 'ПРИМЕНИТЬ'}
        </button>
      </div>
    {/if}
  {:else}
    <div class="message message-error">
      Перк не найден
    </div>
  {/if}
</div>

<style>
  .perk-card {
    background: rgba(20, 255, 0, 0.05);
    border: 1px solid var(--terminal-green);
    padding: 16px;
    margin-bottom: 16px;
  }

  .perk-name {
    font-size: 1.4rem;
    margin-bottom: 8px;
  }

  .perk-description {
    color: var(--terminal-dim);
    margin-bottom: 12px;
    line-height: 1.4;
  }

  .perk-effect {
    display: flex;
    justify-content: space-between;
    font-size: 1.1rem;
    margin-top: 12px;
  }

  .perk-note {
    font-size: 0.8rem;
    color: var(--terminal-dim);
    margin-top: 8px;
    font-style: italic;
  }

  .actions {
    display: flex;
    gap: 12px;
    margin-top: 16px;
  }

  .actions .btn {
    flex: 1;
  }
</style>
