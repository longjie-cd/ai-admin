<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Dict } from '@/api/sys/dict'

const props = defineProps<{
  item: Dict
  selectedId: number | null
}>()

defineEmits<{
  select: [item: Dict]
  'create-child': [parentId: number]
}>()

const isExpanded = ref(false)
const itemSelected = computed(() => props.item.id === props.selectedId)
</script>

<template>
  <div>
    <div
      class="flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer transition-colors text-sm"
      :class="itemSelected ? 'bg-primary text-primary-foreground' : 'hover:bg-accent'"
      @click="$emit('select', item)"
    >
      <button
        v-if="item.children?.length"
        class="p-0.5 hover:bg-white/20 rounded"
        @click.stop="isExpanded = !isExpanded"
      >
        <svg class="w-4 h-4 transition-transform" :style="{ transform: isExpanded ? 'rotate(90deg)' : '' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
      <div v-else class="w-4" />
      <span class="truncate flex-1">{{ item.name }}</span>
    </div>

    <div v-if="isExpanded && item.children?.length" class="pl-4 space-y-1">
      <DictTreeItem
        v-for="child in item.children"
        :key="child.id"
        :item="child"
        :selected-id="selectedId"
        @select="$emit('select', $event)"
        @create-child="$emit('create-child', $event)"
      />
    </div>
  </div>
</template>
