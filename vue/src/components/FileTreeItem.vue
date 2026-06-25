<script setup lang="ts">
import { ref, computed } from 'vue'
import { Folder, FolderOpen, FileText, FileImage, FileSpreadsheet, File } from 'lucide-vue-next'
import type { OssFile } from '@/api/sys/oss'

const props = defineProps<{
  item: OssFile
  selectedId: number | null
  dragOverId: number | null
}>()

defineEmits<{
  select: [item: OssFile]
  dragstart: [item: OssFile]
  dragover: [item: OssFile, e: DragEvent]
  dragleave: []
  drop: [item: OssFile]
  contextmenu: [e: MouseEvent, item: OssFile]
}>()

const isExpanded = ref(false)
const isSelected = computed(() => props.item.id === props.selectedId)
const isDragOver = computed(() => props.item.id === props.dragOverId)

const hasChildren = computed(() => props.item.children?.length > 0)

function iconFor(file: OssFile) {
  if (file.type === 'folder') return isExpanded.value ? FolderOpen : Folder
  const ct = file.content_type || ''
  if (ct.startsWith('image/')) return FileImage
  if (ct.includes('spreadsheet')) return FileSpreadsheet
  if (ct.includes('word') || ct.includes('pdf') || ct.includes('presentation')) return FileText
  return File
}

function iconColor(file: OssFile) {
  if (file.type === 'folder') return 'text-blue-500'
  const ct = file.content_type || ''
  if (ct.startsWith('image/')) return 'text-green-500'
  if (ct.includes('spreadsheet')) return 'text-emerald-600'
  if (ct.includes('word')) return 'text-blue-600'
  if (ct.includes('pdf')) return 'text-red-500'
  if (ct.includes('presentation')) return 'text-orange-500'
  return 'text-gray-400'
}
</script>

<template>
  <div>
    <div
      class="flex items-center gap-1.5 px-2 py-1.5 rounded cursor-pointer transition-colors text-sm group"
      :class="[
        isSelected ? 'bg-primary text-primary-foreground' : 'hover:bg-accent',
        isDragOver ? 'border-2 border-green-400 bg-green-50' : '',
      ]"
      :draggable="true"
      @click="$emit('select', item)"
      @dragstart="$emit('dragstart', item)"
      @dragover="$emit('dragover', item, $event)"
      @dragleave="$emit('dragleave')"
      @drop.stop="$emit('drop', item)"
      @contextmenu="$emit('contextmenu', $event, item)"
    >
      <button
        v-if="hasChildren"
        class="p-0.5 rounded shrink-0"
        :class="isSelected ? 'hover:bg-white/20' : 'hover:bg-black/10'"
        @click.stop="isExpanded = !isExpanded"
      >
        <svg class="w-3.5 h-3.5 transition-transform" :style="{ transform: isExpanded ? 'rotate(90deg)' : '' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7" />
        </svg>
      </button>
      <div v-else class="w-5 shrink-0" />
      <component
        :is="iconFor(item)"
        class="w-4 h-4 shrink-0"
        :class="isSelected ? 'text-primary-foreground' : iconColor(item)"
      />
      <span class="truncate flex-1">{{ item.name }}</span>
      <span
        v-if="item.type === 'folder' && hasChildren"
        class="text-xs px-1.5 py-0.5 rounded-full shrink-0"
        :class="isSelected ? 'bg-white/20' : 'bg-muted text-muted-foreground'"
      >
        {{ item.children.length }}
      </span>
    </div>

    <div v-if="isExpanded && hasChildren" class="pl-4 space-y-0.5">
      <FileTreeItem
        v-for="child in item.children"
        :key="child.id"
        :item="child"
        :selected-id="selectedId"
        :drag-over-id="dragOverId"
        @select="$emit('select', $event)"
        @dragstart="$emit('dragstart', $event)"
        @dragover="$emit('dragover', $event[0], $event[1])"
        @dragleave="$emit('dragleave')"
        @drop="$emit('drop', $event)"
        @contextmenu="$emit('contextmenu', $event[0], $event[1])"
      />
    </div>
  </div>
</template>
