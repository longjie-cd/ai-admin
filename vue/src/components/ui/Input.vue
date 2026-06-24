<script setup lang="ts">
defineProps<{
  class?: string
  type?: string
  placeholder?: string
  modelValue?: string | number
  disabled?: boolean
}>()
defineEmits<{ 'update:modelValue': [value: string | number] }>()
</script>

<template>
  <input
    v-bind="$attrs"
    :type="$props.type ?? 'text'"
    :placeholder="$props.placeholder"
    :value="$props.modelValue"
    :disabled="$props.disabled"
    class="ds-input"
    :class="$props.class"
    @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>

<style>
.ds-input {
  display: flex;
  width: 100%;
  height: var(--input-h);
  padding: 0 var(--input-px);
  border-radius: var(--input-radius);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: hsl(var(--text-1));
  font-size: var(--input-font-size);
  line-height: 1;
  transition: border-color var(--input-transition), box-shadow var(--input-transition);
  outline: none;
}
.ds-input::placeholder { color: hsl(var(--text-3)); }
.ds-input:hover:not(:disabled) { border-color: hsl(var(--border-strong)); }
.ds-input:focus {
  border-color: hsl(var(--primary));
  box-shadow: var(--input-focus-ring);
}
.ds-input:disabled { cursor: not-allowed; opacity: 0.5; background: hsl(var(--bg-sunken)); }
</style>
