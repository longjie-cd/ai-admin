<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { ossApi, type OssFile } from '@/api/sys/oss'
import FileTreeItem from '@/components/FileTreeItem.vue'
import FilePreview from '@/components/FilePreview.vue'
import Button from '@/components/ui/Button.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Input from '@/components/ui/Input.vue'
import { FolderPlus, Upload, RefreshCw, ChevronRight, Folder, FileText, FileImage, FileSpreadsheet, File, Trash2, Pencil, Download, Copy, ClipboardPaste, Move } from 'lucide-vue-next'

const files = ref<OssFile[]>([])
const selectedItem = ref<OssFile | null>(null)
const loading = ref(false)
const submitting = ref(false)
const dialogOpen = ref(false)
const dialogMode = ref<'create-folder' | 'create-file' | 'rename'>('create-folder')
const dialogTitle = ref('')
const editId = ref<number | null>(null)
const form = ref({ name: '', url: '', description: '' })
const uploadFile = ref<File | null>(null)
const uploadProgress = ref(0)
const uploading = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)
const uploadMode = ref<'local' | 'url'>('local')

// 拖拽、复制粘贴、右键菜单
const clipboard = ref<{ item: OssFile; action: 'copy' | 'cut' } | null>(null)
const dragItem = ref<OssFile | null>(null)
const dragOverFolder = ref<OssFile | null>(null)
const contextMenu = ref<{ x: number; y: number; item: OssFile | null } | null>(null)
const moveDialogOpen = ref(false)
const moveTargetId = ref<number | null>(null)

const breadcrumbs = computed(() => {
  if (!selectedItem.value) return []
  const crumbs: { name: string; item: OssFile | null }[] = []
  const findPath = (items: OssFile[], target: OssFile, path: OssFile[]): boolean => {
    for (const item of items) {
      const newPath = [...path, item]
      if (item.id === target.id) {
        crumbs.push(...newPath.map(i => ({ name: i.name, item: i })))
        return true
      }
      if (item.children?.length && findPath(item.children, target, newPath)) {
        return true
      }
    }
    return false
  }
  findPath(files.value, selectedItem.value, [])
  return crumbs
})

const currentFolderContents = computed(() => {
  if (!selectedItem.value || selectedItem.value.type !== 'folder') return []
  return [...(selectedItem.value.children || [])].sort((a, b) => {
    if (a.type !== b.type) return a.type === 'folder' ? -1 : 1
    return a.name.localeCompare(b.name)
  })
})

function iconFor(file: OssFile) {
  if (file.type === 'folder') return Folder
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

function formatSize(bytes: number) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function load() {
  loading.value = true
  try {
    const res = await ossApi.list()
    files.value = res.items
  } finally {
    loading.value = false
  }
}

function selectItem(item: OssFile) {
  selectedItem.value = item
}

function openCreateFolder(parentId?: number) {
  dialogMode.value = 'create-folder'
  dialogTitle.value = '新建文件夹'
  editId.value = parentId ?? null
  form.value = { name: '', url: '', description: '' }
  dialogOpen.value = true
}

function openCreateFile(parentId?: number) {
  dialogMode.value = 'create-file'
  dialogTitle.value = '上传文件'
  editId.value = parentId ?? null
  form.value = { name: '', url: '', description: '' }
  uploadFile.value = null
  uploadProgress.value = 0
  uploadMode.value = 'local'
  dialogOpen.value = true
}

function openRename(item: OssFile) {
  dialogMode.value = 'rename'
  dialogTitle.value = '重命名'
  editId.value = item.id
  form.value = { name: item.name, url: item.url || '', description: item.description || '' }
  dialogOpen.value = true
}

function guessContentType(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  const map: Record<string, string> = {
    pdf: 'application/pdf',
    doc: 'application/msword',
    docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    xls: 'application/vnd.ms-excel',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    ppt: 'application/vnd.ms-powerpoint',
    pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    png: 'image/png',
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    gif: 'image/gif',
    txt: 'text/plain',
    csv: 'text/csv',
  }
  return map[ext] || 'application/octet-stream'
}

function onFileSelected(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files && input.files.length > 0) {
    uploadFile.value = input.files[0]
    form.value.name = input.files[0].name
  }
}

function triggerFileSelect() {
  fileInputRef.value?.click()
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function submit() {
  if (dialogMode.value === 'create-file' && uploadMode.value === 'local') {
    await submitDirectUpload()
  } else {
    await submitLegacy()
  }
}

/** 前端直传 OSS：获取预签名 URL → XHR PUT 上传 → 刷新列表 */
async function submitDirectUpload() {
  if (!uploadFile.value) return
  uploading.value = true
  uploadProgress.value = 0
  try {
    // 1. 获取预签名上传 URL
    const token = await ossApi.getUploadToken({
      file_name: uploadFile.value.name,
      content_type: uploadFile.value.type || 'application/octet-stream',
      parent_id: editId.value,
    })
    // 2. 直传到 OSS
    await ossApi.uploadToOss(token.upload_url, uploadFile.value, (p) => {
      uploadProgress.value = p
    })
    dialogOpen.value = false
    await load()
    if (editId.value) {
      const updated = findFileById(files.value, editId.value)
      if (updated) selectedItem.value = updated
    }
  } catch (err: any) {
    alert(err.message || '上传失败')
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

/** 旧方式：通过 URL 下载后上传 */
async function submitLegacy() {
  if (!form.value.name.trim()) return
  submitting.value = true
  try {
    if (dialogMode.value === 'rename' && editId.value) {
      await ossApi.update(editId.value, {
        name: form.value.name,
        description: form.value.description || null,
      })
    } else if (dialogMode.value === 'create-folder') {
      await ossApi.create({
        name: form.value.name,
        type: 'folder',
        parent_id: editId.value,
        description: form.value.description || null,
      })
    } else if (dialogMode.value === 'create-file') {
      await ossApi.create({
        name: form.value.name,
        type: 'file',
        parent_id: editId.value,
        url: form.value.url || null,
        content_type: guessContentType(form.value.name),
        size: 0,
        description: form.value.description || null,
      })
    }
    dialogOpen.value = false
    await load()
    if (editId.value) {
      const updated = findFileById(files.value, editId.value)
      if (updated) selectedItem.value = updated
    }
  } finally {
    submitting.value = false
  }
}

function findFileById(items: OssFile[], id: number): OssFile | null {
  for (const item of items) {
    if (item.id === id) return item
    if (item.children?.length) {
      const found = findFileById(item.children, id)
      if (found) return found
    }
  }
  return null
}

async function removeItem(item: OssFile) {
  if (!confirm(`确定删除「${item.name}」${item.type === 'folder' ? '及其所有子项' : ''}？`)) return
  await ossApi.remove(item.id)
  if (selectedItem.value?.id === item.id) selectedItem.value = null
  await load()
}

function downloadFile(item: OssFile) {
  if (item.url) window.open(item.url, '_blank')
}

// ---- 拖拽移动 ----
function onDragStart(item: OssFile) {
  dragItem.value = item
}
function onDragOverFolder(folder: OssFile, e: DragEvent) {
  e.preventDefault()
  if (folder.type === 'folder' && dragItem.value && dragItem.value.id !== folder.id) {
    dragOverFolder.value = folder
  }
}
function onDragLeave() {
  dragOverFolder.value = null
}
function onDrop(targetFolder: OssFile | null) {
  if (!dragItem.value) return
  const targetId = targetFolder?.type === 'folder' ? targetFolder.id : null
  if (dragItem.value.type === 'folder' && targetId === dragItem.value.id) {
    dragItem.value = null; dragOverFolder.value = null; return
  }
  doMove(dragItem.value, targetId)
  dragItem.value = null; dragOverFolder.value = null
}
async function doMove(item: OssFile, targetParentId: number | null) {
  if (item.parent_id === targetParentId) return
  try {
    await ossApi.update(item.id, { parent_id: targetParentId })
    await load()
  } catch (e: any) { alert(e.message || '移动失败') }
}

// ---- 复制粘贴 ----
function copyItem(item: OssFile) { clipboard.value = { item, action: 'copy' } }
function cutItem(item: OssFile) { clipboard.value = { item, action: 'cut' } }
async function pasteToFolder(folderId: number | null) {
  if (!clipboard.value) return
  const { item, action } = clipboard.value
  try {
    if (action === 'copy') {
      await ossApi.copy(item.id, folderId)
    } else {
      await ossApi.update(item.id, { parent_id: folderId })
    }
    clipboard.value = null
    await load()
  } catch (e: any) { alert(e.message || '粘贴失败') }
}
function onKeydown(e: KeyboardEvent) {
  if (!selectedItem.value) return
  if ((e.metaKey || e.ctrlKey) && e.key === 'c') { copyItem(selectedItem.value); e.preventDefault() }
  if ((e.metaKey || e.ctrlKey) && e.key === 'v') { pasteToFolder(selectedItem.value.type === 'folder' ? selectedItem.value.id : selectedItem.value.parent_id); e.preventDefault() }
  if ((e.metaKey || e.ctrlKey) && e.key === 'x') { cutItem(selectedItem.value); e.preventDefault() }
}

// ---- 右键菜单 ----
function onContextMenu(e: MouseEvent, item: OssFile | null) {
  e.preventDefault()
  contextMenu.value = { x: e.clientX, y: e.clientY, item }
}
function closeContextMenu() { contextMenu.value = null }
function contextAction(action: string) {
  const item = contextMenu.value?.item
  closeContextMenu()
  if (!item && action !== 'paste') return
  switch (action) {
    case 'rename': openRename(item!); break
    case 'copy': copyItem(item!); break
    case 'cut': cutItem(item!); break
    case 'paste': pasteToFolder(selectedItem.value?.type === 'folder' ? selectedItem.value.id : null); break
    case 'delete': removeItem(item!); break
    case 'download': downloadFile(item!); break
  }
}

onMounted(() => { load(); window.addEventListener('keydown', onKeydown); window.addEventListener('click', closeContextMenu) })
onUnmounted(() => { window.removeEventListener('keydown', onKeydown); window.removeEventListener('click', closeContextMenu) })
</script>

<template>
  <div class="flex h-[calc(100vh-120px)] gap-4">
    <!-- 左侧文件树 -->
    <div class="w-72 flex flex-col border rounded-lg bg-muted/30 shrink-0">
      <div class="px-4 py-3 border-b flex items-center justify-between flex-shrink-0">
        <h3 class="font-medium text-sm">文件目录</h3>
        <div class="flex gap-1">
          <Button v-if="clipboard" size="sm" variant="ghost" class="!p-1.5 text-green-600" @click="pasteToFolder(null)" title="粘贴到根目录">
            <ClipboardPaste class="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" class="!p-1.5" @click="load" title="刷新">
            <RefreshCw class="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" class="!p-1.5" @click="openCreateFolder()" title="新建文件夹">
            <FolderPlus class="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" class="!p-1.5" @click="openCreateFile()" title="上传文件">
            <Upload class="w-4 h-4" />
          </Button>
        </div>
      </div>
      <div v-if="loading" class="flex-1 flex items-center justify-center text-muted-foreground text-sm">
        加载中...
      </div>
      <div v-else class="flex-1 overflow-y-auto p-2" @contextmenu="onContextMenu($event, null)" @dragover.prevent @drop.prevent="onDrop(null)">
        <div v-if="files.length === 0" class="text-center text-muted-foreground text-sm py-8">
          暂无文件
        </div>
        <div v-else class="space-y-0.5">
          <FileTreeItem
            v-for="item in files"
            :key="item.id"
            :item="item"
            :selected-id="selectedItem?.id ?? null"
            :drag-over-id="dragOverFolder?.id ?? null"
            @select="selectItem"
            @dragstart="onDragStart(item)"
            @dragover="onDragOverFolder(item, $event)"
            @dragleave="onDragLeave"
            @drop.stop="onDrop(item)"
            @contextmenu="onContextMenu($event, item)"
          />
        </div>
      </div>
    </div>

    <!-- 右侧主区域 -->
    <div class="flex-1 flex flex-col border rounded-lg bg-background overflow-hidden">
      <!-- 面包屑导航 -->
      <div class="px-4 py-2.5 border-b flex items-center justify-between flex-shrink-0">
        <div class="flex items-center gap-1 text-sm min-w-0 overflow-x-auto">
          <button class="text-muted-foreground hover:text-foreground shrink-0" @click="selectedItem = null">
            <Folder class="w-4 h-4" />
          </button>
          <template v-for="(crumb, idx) in breadcrumbs" :key="crumb.item?.id">
            <ChevronRight class="w-3.5 h-3.5 text-muted-foreground shrink-0" />
            <span
              class="shrink-0"
              :class="idx === breadcrumbs.length - 1 ? 'font-medium' : 'text-muted-foreground cursor-pointer hover:text-foreground'"
              @click="crumb.item && selectItem(crumb.item)"
            >{{ crumb.name }}</span>
          </template>
        </div>
        <div v-if="selectedItem" class="flex gap-1 shrink-0 ml-2">
          <Button size="sm" variant="ghost" class="!p-1.5" @click="copyItem(selectedItem)" title="复制 (Ctrl+C)">
            <Copy class="w-4 h-4" />
          </Button>
          <Button v-if="clipboard" size="sm" variant="ghost" class="!p-1.5 text-green-600" @click="pasteToFolder(selectedItem.type === 'folder' ? selectedItem.id : selectedItem.parent_id)" title="粘贴到此文件夹">
            <ClipboardPaste class="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" class="!p-1.5" @click="openRename(selectedItem)" title="重命名">
            <Pencil class="w-4 h-4" />
          </Button>
          <Button v-if="selectedItem.type === 'folder'" size="sm" variant="ghost" class="!p-1.5" @click="openCreateFolder(selectedItem.id)" title="新建子文件夹">
            <FolderPlus class="w-4 h-4" />
          </Button>
          <Button v-if="selectedItem.type === 'folder'" size="sm" variant="ghost" class="!p-1.5" @click="openCreateFile(selectedItem.id)" title="上传文件到此文件夹">
            <Upload class="w-4 h-4" />
          </Button>
          <Button v-if="selectedItem.type === 'file' && selectedItem.url" size="sm" variant="ghost" class="!p-1.5" @click="downloadFile(selectedItem)" title="下载">
            <Download class="w-4 h-4" />
          </Button>
          <Button size="sm" variant="ghost" class="!p-1.5 hover:!text-red-500" @click="removeItem(selectedItem)" title="删除">
            <Trash2 class="w-4 h-4" />
          </Button>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="flex-1 min-h-0 overflow-hidden">
        <!-- 未选择任何项：显示根目录文件列表 -->
        <div v-if="!selectedItem" class="h-full overflow-y-auto p-4" @contextmenu="onContextMenu($event, null)" @dragover.prevent @drop.prevent="onDrop(null)">
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <div
              v-for="item in files"
              :key="item.id"
              class="flex flex-col items-center gap-2 p-3 rounded-lg border hover:bg-accent hover:border-primary/40 cursor-pointer transition-all group"
              :class="{ 'border-green-400 bg-green-50': dragOverFolder?.id === item.id }"
              draggable="true"
              @click="selectItem(item)"
              @contextmenu="onContextMenu($event, item)"
              @dragstart="onDragStart(item)"
              @dragover="onDragOverFolder(item, $event)"
              @dragleave="onDragLeave"
              @drop.stop="onDrop(item)"
            >
              <component :is="iconFor(item)" class="w-10 h-10" :class="iconColor(item)" />
              <span class="text-xs text-center truncate w-full">{{ item.name }}</span>
              <span v-if="item.type === 'folder'" class="text-[10px] text-muted-foreground">{{ item.children?.length || 0 }} 项</span>
            </div>
          </div>
          <div v-if="files.length === 0" class="flex flex-col items-center justify-center h-full text-muted-foreground gap-3">
            <Folder class="w-16 h-16 opacity-30" />
            <p class="text-sm">暂无文件，点击左上角按钮上传</p>
          </div>
        </div>

        <!-- 选中文件夹：显示文件夹内容 -->
        <div v-else-if="selectedItem.type === 'folder'" class="h-full overflow-y-auto p-4" @contextmenu="onContextMenu($event, null)" @dragover.prevent @drop.prevent="onDrop(selectedItem)">
          <div v-if="currentFolderContents.length === 0" class="flex flex-col items-center justify-center h-full text-muted-foreground gap-3">
            <Folder class="w-16 h-16 opacity-30" />
            <p class="text-sm">文件夹为空</p>
            <Button size="sm" variant="outline" @click="openCreateFile(selectedItem.id)">
              <Upload class="w-4 h-4" /> 上传文件
            </Button>
          </div>
          <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            <div
              v-for="item in currentFolderContents"
              :key="item.id"
              class="flex flex-col items-center gap-2 p-3 rounded-lg border hover:bg-accent hover:border-primary/40 cursor-pointer transition-all group relative"
              :class="{ 'border-green-400 bg-green-50': dragOverFolder?.id === item.id }"
              draggable="true"
              @click="selectItem(item)"
              @contextmenu="onContextMenu($event, item)"
              @dragstart="onDragStart(item)"
              @dragover="onDragOverFolder(item, $event)"
              @dragleave="onDragLeave"
              @drop.stop="onDrop(item)"
            >
              <button
                class="absolute top-1 right-1 p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-destructive/10 hover:text-red-500 transition-all"
                @click.stop="removeItem(item)"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
              <component :is="iconFor(item)" class="w-10 h-10" :class="iconColor(item)" />
              <span class="text-xs text-center truncate w-full">{{ item.name }}</span>
              <span v-if="item.type === 'folder'" class="text-[10px] text-muted-foreground">{{ item.children?.length || 0 }} 项</span>
              <span v-else class="text-[10px] text-muted-foreground">{{ formatSize(item.size) }}</span>
            </div>
          </div>
        </div>

        <!-- 选中文件：显示文件预览 -->
        <FilePreview v-else :file="selectedItem" />
      </div>
    </div>
  </div>

  <!-- 创建/编辑对话框 -->
  <Dialog
    :open="dialogOpen"
    :title="dialogTitle"
    :loading="submitting || uploading"
    @update:open="dialogOpen = $event"
    @confirm="submit"
  >
    <div class="space-y-3">
      <!-- 上传文件：本地直传模式 -->
      <template v-if="dialogMode === 'create-file'">
        <div class="flex gap-2 border-b pb-2">
          <button
            class="text-sm px-3 py-1 rounded-md transition-colors"
            :class="uploadMode === 'local' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'"
            @click="uploadMode = 'local'"
          >本地上传</button>
          <button
            class="text-sm px-3 py-1 rounded-md transition-colors"
            :class="uploadMode === 'url' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'"
            @click="uploadMode = 'url'"
          >URL 导入</button>
        </div>

        <!-- 本地直传 -->
        <div v-if="uploadMode === 'local'" class="space-y-3">
          <div
            class="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:border-primary/60 hover:bg-accent/50 transition-all"
            @click="triggerFileSelect"
            @dragover.prevent
            @drop.prevent="(e: DragEvent) => { if (e.dataTransfer?.files[0]) { uploadFile = e.dataTransfer.files[0]; form.name = e.dataTransfer.files[0].name } }"
          >
            <input ref="fileInputRef" type="file" class="hidden" @change="onFileSelected" />
            <Upload class="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
            <p class="text-sm text-muted-foreground">点击或拖拽文件到此处</p>
          </div>
          <div v-if="uploadFile" class="flex items-center gap-2 p-2 rounded-md bg-muted/50">
            <FileText class="w-4 h-4 text-blue-500 shrink-0" />
            <div class="flex-1 min-w-0">
              <p class="text-sm truncate">{{ uploadFile.name }}</p>
              <p class="text-xs text-muted-foreground">{{ formatFileSize(uploadFile.size) }}</p>
            </div>
          </div>
          <div v-if="uploading" class="space-y-1">
            <div class="flex justify-between text-xs">
              <span>上传中...</span>
              <span>{{ uploadProgress }}%</span>
            </div>
            <div class="w-full bg-muted rounded-full h-2">
              <div class="bg-primary h-2 rounded-full transition-all duration-300" :style="{ width: uploadProgress + '%' }" />
            </div>
          </div>
          <div class="space-y-1">
            <label class="text-sm font-medium">描述</label>
            <Input v-model="form.description" placeholder="可选" />
          </div>
        </div>

        <!-- URL 导入 -->
        <div v-else class="space-y-3">
          <div class="space-y-1">
            <label class="text-sm font-medium">文件名称 *</label>
            <Input v-model="form.name" placeholder="请输入名称" />
          </div>
          <div class="space-y-1">
            <label class="text-sm font-medium">文件 URL</label>
            <Input v-model="form.url" placeholder="输入文件的可访问 URL（如 OSS 地址）" />
            <p class="text-xs text-muted-foreground">文件内容类型将根据扩展名自动识别</p>
          </div>
          <div class="space-y-1">
            <label class="text-sm font-medium">描述</label>
            <Input v-model="form.description" placeholder="可选" />
          </div>
        </div>
      </template>

      <!-- 新建文件夹 / 重命名 -->
      <template v-else>
        <div class="space-y-1">
          <label class="text-sm font-medium">名称 *</label>
          <Input v-model="form.name" placeholder="请输入名称" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">描述</label>
          <Input v-model="form.description" placeholder="可选" />
        </div>
      </template>
    </div>
  </Dialog>

  <!-- 右键菜单 -->
  <Teleport to="body">
    <div
      v-if="contextMenu"
      class="fixed z-50 min-w-[160px] rounded-md border bg-background shadow-lg py-1"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
    >
      <template v-if="contextMenu.item">
        <button v-if="contextMenu.item.type === 'file'" class="w-full px-3 py-1.5 text-sm text-left hover:bg-accent flex items-center gap-2" @click="contextAction('download')">
          <Download class="w-3.5 h-3.5" /> 下载
        </button>
        <button class="w-full px-3 py-1.5 text-sm text-left hover:bg-accent flex items-center gap-2" @click="contextAction('copy')">
          <Copy class="w-3.5 h-3.5" /> 复制 <span class="ml-auto text-xs text-muted-foreground">Ctrl+C</span>
        </button>
        <button class="w-full px-3 py-1.5 text-sm text-left hover:bg-accent flex items-center gap-2" @click="contextAction('cut')">
          <Move class="w-3.5 h-3.5" /> 剪切 <span class="ml-auto text-xs text-muted-foreground">Ctrl+X</span>
        </button>
        <button v-if="clipboard" class="w-full px-3 py-1.5 text-sm text-left hover:bg-accent flex items-center gap-2 text-green-600" @click="contextAction('paste')">
          <ClipboardPaste class="w-3.5 h-3.5" /> 粘贴 <span class="ml-auto text-xs text-muted-foreground">Ctrl+V</span>
        </button>
        <div class="my-1 border-t" />
        <button class="w-full px-3 py-1.5 text-sm text-left hover:bg-accent flex items-center gap-2" @click="contextAction('rename')">
          <Pencil class="w-3.5 h-3.5" /> 重命名
        </button>
        <button class="w-full px-3 py-1.5 text-sm text-left hover:bg-accent flex items-center gap-2 text-red-500" @click="contextAction('delete')">
          <Trash2 class="w-3.5 h-3.5" /> 删除
        </button>
      </template>
      <template v-else>
        <button v-if="clipboard" class="w-full px-3 py-1.5 text-sm text-left hover:bg-accent flex items-center gap-2 text-green-600" @click="contextAction('paste')">
          <ClipboardPaste class="w-3.5 h-3.5" /> 粘贴到此处
        </button>
        <button class="w-full px-3 py-1.5 text-sm text-left hover:bg-accent flex items-center gap-2" @click="openCreateFolder()">
          <FolderPlus class="w-3.5 h-3.5" /> 新建文件夹
        </button>
        <button class="w-full px-3 py-1.5 text-sm text-left hover:bg-accent flex items-center gap-2" @click="openCreateFile()">
          <Upload class="w-3.5 h-3.5" /> 上传文件
        </button>
      </template>
    </div>
  </Teleport>
</template>
