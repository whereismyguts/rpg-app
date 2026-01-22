<script>
  export let name;
  export let value;
  export let max = 10;
  export let description = '';
</script>

<div class="stat-bar" title={description}>
  <span class="stat-label">{name}</span>
  <div class="stat-track">
    {#each Array(max) as _, i}
      <div class="stat-segment" class:filled={i < value}></div>
    {/each}
  </div>
  <span class="stat-value">{value}</span>
</div>
