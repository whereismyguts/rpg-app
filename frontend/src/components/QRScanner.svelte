<script>
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import { Html5Qrcode } from 'html5-qrcode';

  const dispatch = createEventDispatcher();

  let scanner = null;
  let error = '';
  let scanning = false;
  let cameraReady = false;
  const scannerId = 'qr-scanner-' + Math.random().toString(36).substr(2, 9);

  onMount(async () => {
    await startScanner();
  });

  onDestroy(() => {
    stopScanner();
  });

  async function startScanner() {
    error = '';
    scanning = true;

    try {
      scanner = new Html5Qrcode(scannerId);

      await scanner.start(
        { facingMode: 'environment' },
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0,
        },
        (decodedText) => {
          dispatch('scan', { data: decodedText });
          stopScanner();
        },
        () => {}
      );

      cameraReady = true;
    } catch (e) {
      console.error('Camera error:', e);
      if (e.toString().includes('NotAllowedError')) {
        error = 'Доступ к камере запрещён. Разрешите доступ к камере.';
      } else if (e.toString().includes('NotFoundError')) {
        error = 'Камера не найдена на устройстве.';
      } else {
        error = 'Ошибка доступа к камере: ' + (e.message || e);
      }
      scanning = false;
    }
  }

  function stopScanner() {
    if (scanner) {
      scanner.stop().catch(() => {});
      scanner = null;
    }
    scanning = false;
    cameraReady = false;
  }

  function handleCancel() {
    stopScanner();
    dispatch('cancel');
  }
</script>

<div class="scanner-container">
  <div class="scanner-header">
    <p class="text-dim">СКАНИРОВАНИЕ QR КОДА...</p>
  </div>

  <div id={scannerId} class="scanner-viewport"></div>

  {#if !cameraReady && scanning}
    <div class="scanner-loading">
      <p>ИНИЦИАЛИЗАЦИЯ КАМЕРЫ<span class="loading-cursor">_</span></p>
    </div>
  {/if}

  {#if error}
    <div class="message message-error">
      ОШИБКА: {error}
    </div>
  {/if}

  <button
    class="btn btn-block cancel-btn"
    on:click={handleCancel}
  >
    [ ОТМЕНА ]
  </button>
</div>

<style>
  .scanner-container {
    width: 100%;
  }

  .scanner-header {
    text-align: center;
    margin-bottom: 16px;
  }

  .scanner-viewport {
    width: 100%;
    min-height: 300px;
    background: #0a0a0a;
    border: 2px solid var(--terminal-green, #14ff00);
    border-radius: 4px;
    overflow: hidden;
  }

  .scanner-viewport :global(video) {
    width: 100% !important;
    height: auto !important;
  }

  .scanner-loading {
    text-align: center;
    padding: 20px;
    color: var(--terminal-green, #14ff00);
  }

  .loading-cursor {
    animation: blink 1s infinite;
  }

  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }

  .cancel-btn {
    margin-top: 16px;
    position: relative;
    z-index: 10;
  }
</style>
