<script>
  export let name;
  export let value;
  export let max = 10;
  export let description = '';
  export let bonus = 0;
</script>

<div class="stat-bar" title={description}>
  <span class="stat-label">{name}</span>
  <div class="stat-track">
    {#each Array(max) as _, i}
      <div
        class="stat-segment"
        class:filled={i < value - bonus}
        class:bonus={i >= value - bonus && i < value}
      ></div>
    {/each}
  </div>
  <span class="stat-value">
    {value}{#if bonus > 0}<span class="bonus-text">+{bonus}</span>{/if}
  </span>
</div>

<style>
  .stat-segment.bonus {
    background: var(--terminal-amber);
    box-shadow: 0 0 5px var(--terminal-amber);
  }
  .bonus-text {
    color: var(--terminal-amber);
    font-size: 0.7em;
    margin-left: 2px;
  }
</style>
