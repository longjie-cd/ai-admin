<script setup lang="ts">
import { cn } from '@/lib/utils'

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
    :value="modelValue ?? ''"
    :disabled="disabled"
    :class="cn(
      'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
      'disabled:cursor-not-allowed disabled:opacity-50',
      $props.class
    )"
    @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
  >
    <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
    <option v-for="opt in options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
  </select>
</template>
