<script setup lang="ts">
const props = withDefaults(defineProps<{
  variant?: 'default' | 'secondary' | 'success' | 'warning' | 'destructive' | 'outline'
  class?: string
}>(), { variant: 'default' })
</script>

<template>
  <span class="ds-badge" :class="[`ds-badge--${props.variant}`, props.class]">
    <slot />
  </span>
</template>

<style>
.ds-badge {
  display: inline-flex;
  align-items: center;
  border-radius: var(--badge-radius);
  font-size: var(--badge-font-size);
  font-weight: var(--badge-font-weight);
  padding: var(--badge-py) var(--badge-px);
  line-height: 1;
  white-space: nowrap;
  border: 1px solid transparent;
}
.ds-badge--default {
  background: hsl(var(--primary) / 0.12);
  color: hsl(var(--primary));
  border-color: hsl(var(--primary) / 0.2);
}
.ds-badge--secondary {
  background: hsl(var(--bg-sunken));
  color: hsl(var(--text-2));
  border-color: hsl(var(--border-default));
}
.ds-badge--success {
  background: hsl(var(--success-bg));
  color: hsl(var(--success-text));
  border-color: hsl(var(--success-border));
}
.ds-badge--warning {
  background: hsl(var(--warning-bg));
  color: hsl(var(--warning-text));
  border-color: hsl(var(--warning-border));
}
.ds-badge--destructive {
  background: hsl(var(--error-bg));
  color: hsl(var(--error-text));
  border-color: hsl(var(--error-border));
}
.ds-badge--outline {
  background: transparent;
  color: hsl(var(--text-2));
  border-color: hsl(var(--border-default));
}
</style>
