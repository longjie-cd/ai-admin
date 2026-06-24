<script setup lang="ts">
defineProps<{
  modelValue?: string | number | null
  options: { label: string; value: string | number }[]
  placeholder?: string
  class?: string
  disabled?: boolean
}>()
defineEmits<{ 'update:modelValue': [value: string | number] }>()
</script>

<template>
  <select
    :value="$props.modelValue ?? ''"
    :disabled="$props.disabled"
    class="ds-select"
    :class="$props.class"
    @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
  >
    <option v-if="$props.placeholder" value="" disabled>{{ $props.placeholder }}</option>
    <option v-for="opt in $props.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
  </select>
</template>

<style>
.ds-select {
  display: flex;
  width: 100%;
  height: var(--input-h);
  padding: 0 var(--input-px);
  border-radius: var(--input-radius);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: hsl(var(--text-1));
  font-size: var(--input-font-size);
  transition: border-color var(--input-transition), box-shadow var(--input-transition);
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 32px;
}
.ds-select:hover:not(:disabled) { border-color: hsl(var(--border-strong)); }
.ds-select:focus { border-color: hsl(var(--primary)); box-shadow: var(--input-focus-ring); }
.ds-select:disabled { cursor: not-allowed; opacity: 0.5; background-color: hsl(var(--bg-sunken)); }
</style>
