<script setup lang="ts">
import { computed } from 'vue'
import officePreset from '@file-viewer/preset-office'
import litePreset from '@file-viewer/preset-lite'
import { modelRenderer } from '@file-viewer/renderer-3d'
import { mindmapRenderer } from '@file-viewer/renderer-mindmap'
import type { OssFile } from '@/api/sys/oss'

const props = defineProps<{
  file: OssFile | null
}>()

const viewerOptions = computed(() => ({
  preset: [officePreset, litePreset],
  renderers: [modelRenderer, mindmapRenderer],
  rendererMode: 'replace',
  theme: 'light',
  toolbar: { position: 'bottom-right', download: true, print: true, exportHtml: true },
  watermark: { text: '内部预览', opacity: 0.1 },
}))

const previewUrl = computed(() => props.file?.url || '')
const canPreview = computed(() => {
  if (!props.file || props.file.type !== 'file') return false
  return !!props.file.url
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- 顶部信息栏 -->
    <div v-if="file" class="px-4 py-3 border-b bg-muted/30 flex items-center justify-between shrink-0">
      <div class="min-w-0">
        <p class="text-sm font-medium truncate">{{ file.name }}</p>
        <p class="text-xs text-muted-foreground mt-0.5 truncate">{{ file.path }}</p>
      </div>
      <div class="flex items-center gap-3 text-xs text-muted-foreground shrink-0 ml-4">
        <span v-if="file.size > 0">{{ (file.size / 1024).toFixed(1) }} KB</span>
        <span v-if="file.content_type" class="hidden sm:inline">{{ file.content_type }}</span>
      </div>
    </div>

    <!-- 预览区域 -->
    <div class="flex-1 min-h-0 overflow-hidden">
      <div v-if="!file" class="h-full flex flex-col items-center justify-center text-muted-foreground gap-3">
        <svg class="w-16 h-16 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="text-sm">选择一个文件以预览</p>
      </div>

      <div v-else-if="file.type === 'folder'" class="h-full flex flex-col items-center justify-center text-muted-foreground gap-3">
        <svg class="w-16 h-16 opacity-30 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        <p class="text-sm">这是一个文件夹</p>
        <p class="text-xs">{{ file.children?.length || 0 }} 个子项</p>
      </div>

      <div v-else-if="!canPreview" class="h-full flex flex-col items-center justify-center text-muted-foreground gap-3">
        <svg class="w-16 h-16 opacity-30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-sm">该文件暂无可预览的 URL</p>
      </div>

      <file-viewer
        v-else
        :url="previewUrl"
        :options="viewerOptions"
        class="h-full"
      />
    </div>
  </div>
</template>
