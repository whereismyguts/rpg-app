<script>
  import { createEventDispatcher } from 'svelte';
  import { auth } from '../stores/auth.js';
  import { api } from '../api.js';
  import QRScanner from './QRScanner.svelte';

  const dispatch = createEventDispatcher();

  let step = 'recipient'; // recipient | amount | confirm
  let recipientUuid = '';
  let recipient = null;
  let amount = '';
  let error = '';
  let loading = false;
  let showQRScanner = false;
  let success = false;
  let transferResult = null;

  async function lookupRecipient() {
    if (!recipientUuid.trim()) {
      error = 'Please enter recipient Player ID';
      return;
    }

    const uuid = recipientUuid.trim().toUpperCase();
    if (uuid === $auth.playerUuid) {
      error = 'Cannot send to yourself';
      return;
    }

    loading = true;
    error = '';

    try {
      recipient = await api.lookupUser(uuid);
      step = 'amount';
    } catch (e) {
      error = 'Recipient not found';
    } finally {
      loading = false;
    }
  }

  function validateAmount() {
    const num = parseFloat(amount);
    if (isNaN(num) || num <= 0) {
      error = 'Please enter a valid amount';
      return;
    }
    if (num > $auth.balance) {
      error = 'Insufficient funds';
      return;
    }
    error = '';
    step = 'confirm';
  }

  async function confirmTransfer() {
    loading = true;
    error = '';

    try {
      transferResult = await api.sendMoney(recipient.player_uuid, parseFloat(amount));
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
    <h2 class="terminal-title">Transfer Caps</h2>
    <p class="text-dim">Your balance: {$auth.balance} caps</p>
  </div>

  {#if success}
    <div class="message message-success">
      <p>TRANSFER COMPLETE</p>
      <p style="margin-top: 8px;">
        Sent {transferResult.transferred} caps to {transferResult.to_name}
      </p>
      <p style="margin-top: 8px;">
        New balance: {transferResult.new_balance} caps
      </p>
    </div>
    <button class="btn btn-block" on:click={() => dispatch('complete')}>
      [ DONE ]
    </button>
  {:else if showQRScanner}
    <QRScanner
      on:scan={handleQRScan}
      on:cancel={() => showQRScanner = false}
    />
  {:else if step === 'recipient'}
    <div class="form-group">
      <label>Recipient Player ID</label>
      <input
        type="text"
        bind:value={recipientUuid}
        placeholder="Enter Player ID"
        disabled={loading}
      />
    </div>

    <button
      class="btn btn-block"
      style="margin-bottom: 16px;"
      on:click={() => showQRScanner = true}
      disabled={loading}
    >
      [ SCAN QR CODE ]
    </button>

    {#if error}
      <div class="message message-error">
        ERROR: {error}
      </div>
    {/if}

    <button
      class="btn btn-block btn-amber"
      on:click={lookupRecipient}
      disabled={loading}
    >
      {loading ? 'SEARCHING...' : '[ FIND RECIPIENT ]'}
    </button>
  {:else if step === 'amount'}
    <div class="user-info">
      <p class="text-dim">SENDING TO</p>
      <p class="user-name">{recipient.name}</p>
      <p class="user-id">ID: {recipient.player_uuid}</p>
    </div>

    <hr class="separator" />

    <div class="form-group">
      <label>Amount (caps)</label>
      <input
        type="number"
        bind:value={amount}
        placeholder="Enter amount"
        min="1"
        max={$auth.balance}
      />
    </div>

    {#if error}
      <div class="message message-error">
        ERROR: {error}
      </div>
    {/if}

    <div style="display: flex; gap: 12px;">
      <button class="btn" style="flex: 1;" on:click={reset}>
        BACK
      </button>
      <button class="btn btn-amber" style="flex: 1;" on:click={validateAmount}>
        NEXT
      </button>
    </div>
  {:else if step === 'confirm'}
    <div class="confirm-box">
      <h3>CONFIRM TRANSFER</h3>
      <p>To: <strong>{recipient.name}</strong></p>
      <p>Amount: <strong class="text-amber">{amount} caps</strong></p>
      <p class="text-dim" style="margin-top: 12px;">
        Balance after: {$auth.balance - parseFloat(amount)} caps
      </p>

      {#if error}
        <div class="message message-error">
          ERROR: {error}
        </div>
      {/if}

      <div class="confirm-actions">
        <button class="btn" on:click={() => step = 'amount'} disabled={loading}>
          BACK
        </button>
        <button class="btn btn-amber" on:click={confirmTransfer} disabled={loading}>
          {loading ? 'SENDING...' : 'CONFIRM'}
        </button>
      </div>
    </div>
  {/if}
</div>
