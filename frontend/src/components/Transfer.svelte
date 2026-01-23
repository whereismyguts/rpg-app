<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { auth } from '../stores/auth.js';
  import { api } from '../api.js';
  import QRScanner from './QRScanner.svelte';

  const dispatch = createEventDispatcher();

  export let recipient = null;

  let step = recipient ? 'amount' : 'recipient';
  let recipientUuid = recipient?.player_uuid || '';
  let amount = '';
  let error = '';
  let loading = false;
  let showQRScanner = false;
  let success = false;
  let transferResult = null;

  $: if (recipient) {
    step = 'amount';
    recipientUuid = recipient.player_uuid;
  }

  async function lookupRecipient() {
    if (!recipientUuid.trim()) {
      error = 'Введите ID получателя';
      return;
    }

    const uuid = recipientUuid.trim().toUpperCase();
    if (uuid === $auth.playerUuid) {
      error = 'Нельзя отправить себе';
      return;
    }

    loading = true;
    error = '';

    try {
      recipient = await api.lookupUser(uuid);
      step = 'amount';
    } catch (e) {
      error = 'Получатель не найден';
    } finally {
      loading = false;
    }
  }

  function validateAmount() {
    const num = parseInt(amount);
    if (isNaN(num) || num <= 0) {
      error = 'Введите корректную сумму';
      return;
    }
    if (num > $auth.balance) {
      error = 'Недостаточно крышек';
      return;
    }
    error = '';
    step = 'confirm';
  }

  async function confirmTransfer() {
    loading = true;
    error = '';

    try {
      transferResult = await api.sendMoney(recipient.player_uuid, parseInt(amount));
      auth.updateBalance(transferResult.new_balance);
      success = true;
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function handleQRScan(event) {
    recipientUuid = event.detail.data;
    showQRScanner = false;
    lookupRecipient();
  }

  function reset() {
    step = 'recipient';
    recipientUuid = '';
    recipient = null;
    amount = '';
    error = '';
    success = false;
    transferResult = null;
  }
</script>

<div class="terminal">
  <div class="terminal-header">
    <h2 class="terminal-title">Перевод крышек</h2>
    <p class="text-dim">Ваш баланс: {$auth.balance} крышек</p>
  </div>

  {#if success}
    <div class="message message-success">
      <p>ПЕРЕВОД ВЫПОЛНЕН</p>
      <p style="margin-top: 8px;">
        Отправлено {transferResult.transferred} крышек для {transferResult.to_name}
      </p>
      <p style="margin-top: 8px;">
        Новый баланс: {transferResult.new_balance} крышек
      </p>
    </div>
    <button class="btn btn-block" on:click={() => dispatch('complete')}>
      [ ГОТОВО ]
    </button>
  {:else if showQRScanner}
    <QRScanner
      on:scan={handleQRScan}
      on:cancel={() => showQRScanner = false}
    />
  {:else if step === 'recipient'}
    <div class="form-group">
      <label>ID получателя</label>
      <input
        type="text"
        bind:value={recipientUuid}
        placeholder="Введите ID"
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

    {#if error}
      <div class="message message-error">
        ОШИБКА: {error}
      </div>
    {/if}

    <button
      class="btn btn-block btn-amber"
      on:click={lookupRecipient}
      disabled={loading}
    >
      {loading ? 'ПОИСК...' : '[ НАЙТИ ]'}
    </button>
  {:else if step === 'amount'}
    <div class="user-info">
      <p class="text-dim">ПОЛУЧАТЕЛЬ</p>
      <p class="user-name">{recipient.name}</p>
      <p class="user-id">ID: {recipient.player_uuid}</p>
    </div>

    <hr class="separator" />

    <div class="form-group">
      <label>Сумма (крышек)</label>
      <input
        type="number"
        bind:value={amount}
        placeholder="Введите сумму"
        min="1"
        step="1"
        max={$auth.balance}
      />
    </div>

    {#if error}
      <div class="message message-error">
        ОШИБКА: {error}
      </div>
    {/if}

    <div style="display: flex; gap: 12px;">
      <button class="btn" style="flex: 1;" on:click={reset}>
        НАЗАД
      </button>
      <button class="btn btn-amber" style="flex: 1;" on:click={validateAmount}>
        ДАЛЕЕ
      </button>
    </div>
  {:else if step === 'confirm'}
    <div class="confirm-box">
      <h3>ПОДТВЕРЖДЕНИЕ</h3>
      <p>Кому: <strong>{recipient.name}</strong></p>
      <p>Сумма: <strong class="text-amber">{amount} крышек</strong></p>
      <p class="text-dim" style="margin-top: 12px;">
        Баланс после: {$auth.balance - parseInt(amount)} крышек
      </p>

      {#if error}
        <div class="message message-error">
          ОШИБКА: {error}
        </div>
      {/if}

      <div class="confirm-actions">
        <button class="btn" on:click={() => step = 'amount'} disabled={loading}>
          НАЗАД
        </button>
        <button class="btn btn-amber" on:click={confirmTransfer} disabled={loading}>
          {loading ? 'ОТПРАВКА...' : 'ПОДТВЕРДИТЬ'}
        </button>
      </div>
    </div>
  {/if}
</div>
