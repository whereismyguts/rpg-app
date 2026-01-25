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
    <h2 class="terminal-title">ПОКУПКА</h2>
  </div>

  {#if success}
    <div class="message message-success">
      <p>ПОКУПКА ЗАВЕРШЕНА</p>
      <p style="margin-top: 8px;">Вы купили: {result.item.name}</p>
      <p style="margin-top: 8px;">Оплачено: {result.paid} крышек</p>
      <p style="margin-top: 8px;">Новый баланс: {result.new_balance} крышек</p>
    </div>
    <button class="btn btn-block" on:click={() => dispatch('complete')}>
      [ ГОТОВО ]
    </button>
  {:else if item}
    <div class="item-card">
      {#if item.image_url}
        <div class="image-wrapper">
          <img src={item.image_url} alt={item.name} class="item-image" />
        </div>
      {/if}
      <h3 class="item-name">{item.name}</h3>
      {#if item.description}
        <p class="item-description">{item.description}</p>
      {/if}
      <div class="item-price">
        <span class="price-label">ЦЕНА:</span>
        <span class="price-value text-amber">{item.price} крышек</span>
      </div>
    </div>

    <hr class="separator" />

    <div class="balance-info">
      <p>Ваш баланс: <strong>{$auth.balance}</strong> крышек</p>
      {#if !canAfford}
        <p class="text-error">Недостаточно крышек!</p>
      {:else}
        <p class="text-dim">После покупки: {$auth.balance - item.price} крышек</p>
      {/if}
    </div>

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
        on:click={confirmPurchase}
        disabled={loading || !canAfford}
      >
        {loading ? 'ОПЛАТА...' : 'КУПИТЬ'}
      </button>
    </div>
  {:else}
    <div class="message message-error">
      Товар не найден
    </div>
  {/if}
</div>

<style>
  .item-card {
    background: rgba(20, 255, 0, 0.05);
    border: 1px solid var(--terminal-green);
    padding: 16px;
    margin-bottom: 16px;
    text-align: center;
  }

  .image-wrapper {
    width: 180px;
    height: 180px;
    margin: 0 auto 12px;
    overflow: hidden;
    border: 1px solid var(--terminal-green-dim);
  }

  .item-image {
    width: 200px;
    height: 200px;
    object-fit: cover;
    margin: -10px;
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
