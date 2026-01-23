<script>
  import { createEventDispatcher } from 'svelte';
  import { auth } from '../stores/auth.js';
  import { api } from '../api.js';

  export let item = null;

  const dispatch = createEventDispatcher();

  let loading = false;
  let error = '';
  let success = false;
  let result = null;

  $: canAfford = item && $auth.balance >= item.price;

  async function confirmPurchase() {
    if (!canAfford) return;

    loading = true;
    error = '';

    try {
      result = await api.purchaseItem(item.item_id);
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
    <h2 class="terminal-title">PURCHASE ITEM</h2>
  </div>

  {#if success}
    <div class="message message-success">
      <p>PURCHASE COMPLETE</p>
      <p style="margin-top: 8px;">You bought: {result.item.name}</p>
      <p style="margin-top: 8px;">Paid: {result.paid} caps</p>
      <p style="margin-top: 8px;">New balance: {result.new_balance} caps</p>
    </div>
    <button class="btn btn-block" on:click={() => dispatch('complete')}>
      [ DONE ]
    </button>
  {:else if item}
    <div class="item-card">
      <h3 class="item-name">{item.name}</h3>
      {#if item.description}
        <p class="item-description">{item.description}</p>
      {/if}
      <div class="item-price">
        <span class="price-label">PRICE:</span>
        <span class="price-value text-amber">{item.price} caps</span>
      </div>
    </div>

    <hr class="separator" />

    <div class="balance-info">
      <p>Your balance: <strong>{$auth.balance}</strong> caps</p>
      {#if !canAfford}
        <p class="text-error">Insufficient funds!</p>
      {:else}
        <p class="text-dim">After purchase: {$auth.balance - item.price} caps</p>
      {/if}
    </div>

    {#if error}
      <div class="message message-error">
        ERROR: {error}
      </div>
    {/if}

    <div class="actions">
      <button class="btn" on:click={() => dispatch('cancel')}>
        CANCEL
      </button>
      <button
        class="btn btn-amber"
        on:click={confirmPurchase}
        disabled={loading || !canAfford}
      >
        {loading ? 'PROCESSING...' : 'CONFIRM PURCHASE'}
      </button>
    </div>
  {:else}
    <div class="message message-error">
      Item not found
    </div>
  {/if}
</div>

<style>
  .item-card {
    background: rgba(20, 255, 0, 0.05);
    border: 1px solid var(--terminal-green);
    padding: 16px;
    margin-bottom: 16px;
  }

  .item-name {
    font-size: 1.4rem;
    margin-bottom: 8px;
  }

  .item-description {
    color: var(--terminal-dim);
    margin-bottom: 12px;
  }

  .item-price {
    display: flex;
    justify-content: space-between;
    font-size: 1.2rem;
  }

  .balance-info {
    margin: 16px 0;
    text-align: center;
  }

  .text-error {
    color: var(--terminal-amber);
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
