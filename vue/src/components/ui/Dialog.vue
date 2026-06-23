<script setup lang="ts">
import { watch } from 'vue'
import Button from './Button.vue'

const props = defineProps<{
  open: boolean
  title: string
  confirmText?: string
  cancelText?: string
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  confirm: []
}>()

watch(() => props.open, (val) => {
  document.body.style.overflow = val ? 'hidden' : ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/50" @click="emit('update:open', false)" />
        <div class="relative z-10 w-full max-w-md mx-4 bg-background rounded-xl shadow-xl border">
          <div class="flex items-center justify-between px-6 py-4 border-b">
            <h3 class="text-base font-semibold">{{ title }}</h3>
            <button class="text-muted-foreground hover:text-foreground transition-colors" @click="emit('update:open', false)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="px-6 py-4">
            <slot />
          </div>
          <div class="flex justify-end gap-2 px-6 py-4 border-t">
            <Button variant="outline" @click="emit('update:open', false)">{{ cancelText ?? '取消' }}</Button>
            <Button :disabled="loading" @click="emit('confirm')">{{ loading ? '提交中...' : (confirmText ?? '确定') }}</Button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.dialog-enter-active, .dialog-leave-active { transition: opacity 0.15s ease; }
.dialog-enter-from, .dialog-leave-to { opacity: 0; }
</style>
