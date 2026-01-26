<script>
  import { onMount } from 'svelte';
  import { api } from '../api.js';
  import AttributeBar from './ui/AttributeBar.svelte';

  let stats = null;
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      stats = await api.getStats();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });
</script>

<div class="terminal">
  <div class="terminal-header">
    <h2 class="terminal-title">S.P.E.C.I.A.L.</h2>
    <p class="text-dim">ХАРАКТЕРИСТИКИ ПЕРСОНАЖА</p>
  </div>

  {#if loading}
    <div class="loading">
      <p>ЗАГРУЗКА<span class="loading-cursor">_</span></p>
    </div>
  {:else if error}
    <div class="message message-error">
      ОШИБКА: {error}
    </div>
  {:else if stats}
    <div class="user-info">
      <p class="user-name">{stats.name}</p>
      {#if stats.profession}
        <p class="text-dim">Профессия: {stats.profession}</p>
      {/if}
      {#if stats.band}
        <p class="text-dim">Группировка: {stats.band}</p>
      {/if}
    </div>

    <hr class="separator" />

    <div class="stats-grid">
      {#each stats.attributes as attr}
        <AttributeBar
          name={attr.display_name}
          value={attr.value}
          max={attr.max_value}
          description={attr.description}
          bonus={attr.bonus}
        />
      {/each}
    </div>
  {/if}
</div>
