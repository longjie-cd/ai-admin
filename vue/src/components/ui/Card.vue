<script setup lang="ts">
defineProps<{ class?: string; padding?: boolean }>()
</script>

<template>
  <div class="ds-card" :class="[$props.class, $props.padding !== false && 'ds-card--padded']">
    <slot />
  </div>
</template>

<style>
.ds-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}
.ds-card--padded { padding: var(--card-padding); }
</style>
