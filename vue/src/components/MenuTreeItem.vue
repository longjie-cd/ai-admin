<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Menu } from '@/api/sys/menu'

const props = defineProps<{
  item: Menu
  selectedId: number | null
}>()

const emit = defineEmits<{
  select: [item: Menu]
  'create-child': [parentId: number]
}>()

const isExpanded = ref(true)
const itemSelected = computed(() => props.item.id === props.selectedId)
</script>

<template>
  <div>
    <div
      class="flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer transition-colors text-sm"
      :class="itemSelected ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'"
      @click="emit('select', item)"
    >
      <button
        v-if="item.children?.length"
        class="p-0.5 hover:bg-white/20 rounded"
        @click.stop="isExpanded = !isExpanded"
      >
        <svg class="w-3.5 h-3.5 transition-transform" :style="{ transform: isExpanded ? 'rotate(90deg)' : '' }"
          fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
      <div v-else class="w-3.5" />
      <span class="truncate flex-1">{{ item.name }}</span>
      <span class="text-xs opacity-60 font-mono hidden group-hover:inline">{{ item.path }}</span>
    </div>
    <div v-if="isExpanded && item.children?.length" class="pl-4 space-y-0.5">
      <MenuTreeItem
        v-for="child in item.children"
        :key="child.id"
        :item="child"
        :selected-id="selectedId"
        @select="emit('select', $event)"
        @create-child="emit('create-child', $event)"
      />
    </div>
  </div>
</template>
