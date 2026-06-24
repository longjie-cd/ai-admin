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

const emit = defineEmits<{ 'update:open': [value: boolean]; confirm: []; close: [] }>()

function closeDialog() {
  emit('update:open', false)
  emit('close')
}

watch(() => props.open, (val) => {
  document.body.style.overflow = val ? 'hidden' : ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="ds-dialog">
      <div v-if="open" class="ds-dialog-root">
        <div class="ds-dialog-overlay" @click="closeDialog" />
        <div class="ds-dialog-panel">
          <!-- Header -->
          <div class="ds-dialog-header">
            <h3 class="ds-dialog-title">{{ title }}</h3>
            <button class="ds-dialog-close" @click="closeDialog">
              <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <!-- Body -->
          <div class="ds-dialog-body"><slot /></div>
          <!-- Footer -->
          <div class="ds-dialog-footer">
            <Button variant="outline" size="sm" @click="closeDialog">
              {{ cancelText ?? '取消' }}
            </Button>
            <Button size="sm" :disabled="loading" @click="emit('confirm')">
              {{ loading ? '提交中...' : (confirmText ?? '确定') }}
            </Button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style>
.ds-dialog-root {
  position: fixed; inset: 0; z-index: 100;
  display: flex; align-items: center; justify-content: center;
  padding: 16px;
}
.ds-dialog-overlay {
  position: absolute; inset: 0;
  background: var(--dialog-overlay);
  backdrop-filter: blur(2px);
}
.ds-dialog-panel {
  position: relative; z-index: 1;
  width: 100%; max-width: var(--dialog-max-w);
  background: hsl(var(--bg-overlay));
  border: 1px solid hsl(var(--border-default));
  border-radius: var(--dialog-radius);
  box-shadow: var(--dialog-shadow);
  display: flex; flex-direction: column;
  max-height: calc(100vh - 48px);
}
.ds-dialog-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid hsl(var(--border-subtle));
  flex-shrink: 0;
}
.ds-dialog-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: hsl(var(--text-1));
}
.ds-dialog-close {
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-sm);
  color: hsl(var(--text-3));
  transition: background var(--transition-fast), color var(--transition-fast);
}
.ds-dialog-close:hover { background: hsl(var(--bg-hover)); color: hsl(var(--text-1)); }
.ds-dialog-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}
.ds-dialog-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 14px 20px;
  border-top: 1px solid hsl(var(--border-subtle));
  flex-shrink: 0;
}

/* Animation */
.ds-dialog-enter-active { transition: opacity 0.15s ease; }
.ds-dialog-leave-active { transition: opacity 0.1s ease; }
.ds-dialog-enter-from, .ds-dialog-leave-to { opacity: 0; }
.ds-dialog-enter-active .ds-dialog-panel { animation: dialog-in 0.18s cubic-bezier(0.34,1.56,0.64,1); }
@keyframes dialog-in {
  from { transform: scale(0.96) translateY(4px); opacity: 0; }
  to   { transform: scale(1) translateY(0); opacity: 1; }
}
</style>
