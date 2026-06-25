<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { quickEntryApi, type QuickEntry } from '@/api/sys/quick_entry'

const router = useRouter()
const entries = ref<QuickEntry[]>([])

onMounted(async () => {
  try {
    entries.value = (await quickEntryApi.listMine()).items
  } catch { /* ignore */ }
})

function handleClick(entry: QuickEntry) {
  if (entry.path.startsWith('http')) {
    window.open(entry.path, '_blank')
  } else {
    router.push(entry.path)
  }
}
</script>

<template>
  <div v-if="entries.length" class="rounded-2xl border border-border p-6" style="background: hsl(var(--card))">
    <div class="flex items-center justify-between mb-4">
      <div>
        <h2 class="text-base font-semibold">快捷入口</h2>
        <p class="text-xs mt-1 text-muted-foreground">根据权限展示常用功能</p>
      </div>
    </div>
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
      <button
        v-for="entry in entries"
        :key="entry.id"
        class="group flex flex-col items-center gap-2 rounded-xl border p-4 text-center transition-all hover:border-primary/50 hover:bg-primary/[0.04]"
        style="border-color: hsl(var(--border-subtle))"
        @click="handleClick(entry)"
      >
        <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white"
          style="background: hsl(var(--primary))">
          <svg v-if="entry.icon === 'external'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
        </div>
        <span class="text-xs font-medium truncate w-full">{{ entry.name }}</span>
      </button>
    </div>
  </div>
</template>
