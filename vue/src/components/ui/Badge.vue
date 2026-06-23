<script setup lang="ts">
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  variant?: 'default' | 'secondary' | 'success' | 'destructive' | 'outline'
  class?: string
}>(), { variant: 'default' })

const variants = {
  default: 'bg-primary text-primary-foreground',
  secondary: 'bg-secondary text-secondary-foreground',
  success: 'bg-green-100 text-green-700',
  destructive: 'bg-destructive/10 text-destructive',
  outline: 'border border-input text-foreground',
}
</script>

<template>
  <span :class="cn('inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium', variants[variant], props.class)">
    <slot />
  </span>
</template>
