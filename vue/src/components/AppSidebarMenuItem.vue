<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Menu } from '@/api/sys/menu'

const props = defineProps<{
  item: Menu
  currentPath: string
  collapsed?: boolean
}>()

const emit = defineEmits<{
  navigate: [item: Menu]
}>()

function normalizePath(path?: string) {
  if (!path) return ''
  return path.startsWith('/') ? path : `/${path}`
}

function isRouteMatch(menuPath: string, routePath: string) {
  if (!menuPath) return false
  const normalized = normalizePath(menuPath)
  if (normalized === '/') return routePath === '/'
  return routePath === normalized || routePath.startsWith(`${normalized}/`)
}

function branchHasActive(menu: Menu, routePath: string): boolean {
  if (isRouteMatch(menu.path, routePath)) return true
  return (menu.children ?? []).some(child => branchHasActive(child, routePath))
}

const hasChildren = computed(() => (props.item.children ?? []).length > 0)
const isActive = computed(() => isRouteMatch(props.item.path, props.currentPath))
const branchActive = computed(() => branchHasActive(props.item, props.currentPath))
const expanded = ref(branchActive.value)

watch(branchActive, (active) => {
  if (active) expanded.value = true
})

function toggleExpand() {
  expanded.value = !expanded.value
}

function onNavigate() {
  emit('navigate', props.item)
}
</script>

<template>
  <div class="space-y-1">
    <div
      class="group flex items-center gap-2 rounded-xl px-3 py-2 text-sm transition-colors"
      :class="[isActive ? 'bg-[hsl(var(--primary)/0.12)] text-[hsl(var(--primary))]' : 'text-[hsl(var(--text-2))] hover:bg-[hsl(var(--bg-hover))] hover:text-[hsl(var(--text-1))]', collapsed ? 'justify-center px-2' : '']"
      :title="collapsed ? item.name : undefined"
    >
      <button
        class="min-w-0 flex flex-1 items-center gap-2 text-left"
        :class="collapsed ? 'justify-center' : ''"
        @click="onNavigate"
      >
        <span
          class="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-lg text-[11px] font-semibold"
          :class="isActive ? 'bg-[hsl(var(--primary)/0.16)]' : 'bg-[hsl(var(--bg-sunken))] text-[hsl(var(--text-3))] group-hover:text-[hsl(var(--text-2))]'"
        >
          {{ item.name.slice(0, 1) }}
        </span>
        <span v-if="!collapsed" class="truncate">{{ item.name }}</span>
      </button>

      <button
        v-if="hasChildren && !collapsed"
        class="flex h-6 w-6 items-center justify-center rounded-md text-[hsl(var(--text-3))] transition-colors hover:bg-[hsl(var(--bg-hover))]"
        @click="toggleExpand"
      >
        <svg
          class="h-3.5 w-3.5 transition-transform"
          :style="{ transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)' }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>

    <div v-if="hasChildren && expanded && !collapsed" class="space-y-1 border-l border-[hsl(var(--border-subtle))] pl-3 ml-3">
      <AppSidebarMenuItem
        v-for="child in item.children"
        :key="child.id"
        :item="child"
        :current-path="currentPath"
        :collapsed="collapsed"
        @navigate="emit('navigate', $event)"
      />
    </div>
  </div>
</template>
