<script>
  import { createEventDispatcher } from 'svelte';
  import jsQR from 'jsqr';

  const dispatch = createEventDispatcher();

  let fileInput;
  let error = '';
  let scanning = false;

  async function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    scanning = true;
    error = '';

    try {
      const imageData = await loadImage(file);
      const code = jsQR(imageData.data, imageData.width, imageData.height);

      if (code) {
        dispatch('scan', { data: code.data });
      } else {
        error = 'No QR code found in image';
      }
    } catch (e) {
      error = 'Failed to process image';
    } finally {
      scanning = false;
      // Reset file input
      if (fileInput) fileInput.value = '';
    }
  }

  function loadImage(file) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        resolve(ctx.getImageData(0, 0, img.width, img.height));
        URL.revokeObjectURL(img.src);
      };
      img.onerror = () => {
        URL.revokeObjectURL(img.src);
        reject(new Error('Failed to load image'));
      };
      img.src = URL.createObjectURL(file);
    });
  }
</script>

<div>
  <input
    type="file"
    accept="image/*"
    bind:this={fileInput}
    on:change={handleFileSelect}
    style="display: none;"
  />

  <div
    class="file-upload"
    on:click={() => fileInput.click()}
    on:keydown={(e) => e.key === 'Enter' && fileInput.click()}
    role="button"
    tabindex="0"
  >
    {#if scanning}
      <p>SCANNING<span class="loading-cursor">_</span></p>
    {:else}
      <p>TAP TO SELECT QR IMAGE</p>
      <p class="text-dim" style="margin-top: 8px;">
        Upload a photo of a QR code
      </p>
    {/if}
  </div>

  {#if error}
    <div class="message message-error">
      ERROR: {error}
    </div>
  {/if}

  <button
    class="btn btn-block"
    style="margin-top: 16px;"
    on:click={() => dispatch('cancel')}
  >
    [ CANCEL ]
  </button>
</div>
