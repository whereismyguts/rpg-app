<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { auth } from '../stores/auth.js';
  import { api } from '../api.js';
  import QRScanner from './QRScanner.svelte';

  const dispatch = createEventDispatcher();

  export let recipient = null;

  let step = recipient ? 'amount' : 'scan';
  let recipientUuid = recipient?.player_uuid || '';
  let amount = '';
  let error = '';
  let loading = false;
  let success = false;
  let transferResult = null;

  $: if (recipient) {
    step = 'amount';
    recipientUuid = recipient.player_uuid;
  }

  async function lookupRecipient(uuid) {
    if (!uuid.trim()) {
      error = 'Отсканируйте QR получателя';
      return;
    }

    const normalizedUuid = uuid.trim().toUpperCase();
    if (normalizedUuid === $auth.playerUuid) {
      error = 'Нельзя отправить себе';
      return;
    }

    loading = true;
    error = '';

    try {
      recipient = await api.lookupUser(normalizedUuid);
      recipientUuid = normalizedUuid;
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
    let data = event.detail.data.trim().toUpperCase();
    // parse LOGIN:UUID format
    if (data.startsWith('LOGIN:')) {
      data = data.substring(6);
    }
    lookupRecipient(data);
  }

  function reset() {
    step = 'scan';
    recipientUuid = '';
    recipient = null;
    amount = '';
    error = '';
    success = false;
    transferResult = null;
  }

  function goBack() {
    dispatch('complete');
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
  {:else if step === 'scan'}
    <div class="scan-prompt">
      <p>Отсканируйте QR код получателя</p>
    </div>

    {#if error}
      <div class="message message-error">
        ОШИБКА: {error}
      </div>
    {/if}

    <QRScanner
      on:scan={handleQRScan}
      on:cancel={goBack}
    />

    <button
      class="btn btn-block"
      style="margin-top: 16px;"
      on:click={goBack}
    >
      [ НА ГЛАВНУЮ ]
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

<style>
  .scan-prompt {
    text-align: center;
    padding: 16px 0;
    margin-bottom: 16px;
  }
</style>
