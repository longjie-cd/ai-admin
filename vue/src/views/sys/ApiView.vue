<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiInterfaceApi, type ApiInterface } from '@/api/sys/api_interface'
import Table from '@/components/ui/Table.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'

const apis = ref<ApiInterface[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogOpen = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const syncUrl = ref('')
const syncLoading = ref(false)

const form = ref({ name: '', path: '', method: 'GET', description: '', openapi_url: '' })

const METHOD_OPTIONS = [
  { label: 'GET', value: 'GET' },
  { label: 'POST', value: 'POST' },
  { label: 'PUT', value: 'PUT' },
  { label: 'DELETE', value: 'DELETE' },
  { label: 'PATCH', value: 'PATCH' },
]

const METHOD_VARIANTS: Record<string, 'default' | 'secondary' | 'success' | 'warning' | 'destructive' | 'outline'> = {
  GET: 'secondary',
  POST: 'success',
  PUT: 'warning',
  DELETE: 'destructive',
  PATCH: 'outline',
}

async function load() {
  loading.value = true
  try {
    const res = await apiInterfaceApi.list()
    apis.value = res.items
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  editId.value = null
  form.value = { name: '', path: '', method: 'GET', description: '', openapi_url: '' }
  dialogOpen.value = true
}

function openEdit(api: ApiInterface) {
  isEdit.value = true
  editId.value = api.id
  form.value = { name: api.name, path: api.path, method: api.method, description: api.description ?? '', openapi_url: api.openapi_url ?? '' }
  dialogOpen.value = true
}

async function submit() {
  submitting.value = true
  try {
    if (isEdit.value && editId.value) {
      const updated = await apiInterfaceApi.update(editId.value, form.value)
      const idx = apis.value.findIndex(a => a.id === editId.value)
      if (idx !== -1) apis.value[idx] = updated
    } else {
      const created = await apiInterfaceApi.create(form.value)
      apis.value.push(created)
    }
    dialogOpen.value = false
  } finally {
    submitting.value = false
  }
}

async function remove(api: ApiInterface) {
  if (!confirm(`确定删除「${api.name}」？`)) return
  await apiInterfaceApi.remove(api.id)
  apis.value = apis.value.filter(a => a.id !== api.id)
}

async function syncFromOpenApi() {
  if (!syncUrl.value.trim()) return
  syncLoading.value = true
  try {
    const res = await fetch(syncUrl.value)
    const spec = await res.json()
    const paths: Record<string, Record<string, { summary?: string; description?: string }>> = spec.paths ?? {}
    let count = 0
    for (const [path, methods] of Object.entries(paths)) {
      for (const [method, op] of Object.entries(methods)) {
        const m = method.toUpperCase()
        if (!['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].includes(m)) continue
        try {
          const created = await apiInterfaceApi.create({
            name: op.summary ?? `${m} ${path}`,
            path,
            method: m,
            description: op.description,
            openapi_url: syncUrl.value,
          })
          apis.value.push(created)
          count++
        } catch {
          // skip duplicates
        }
      }
    }
    alert(`同步完成，新增 ${count} 条接口`)
    syncUrl.value = ''
  } catch (e) {
    alert('同步失败，请检查 URL 或 OpenAPI 规范格式')
  } finally {
    syncLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">API 接口管理</h1>
        <p class="text-sm text-muted-foreground mt-0.5">共 {{ apis.length }} 个接口</p>
      </div>
      <Button @click="openCreate">新建接口</Button>
    </div>

    <!-- OpenAPI 同步 -->
    <div class="flex gap-2 p-4 border rounded-lg bg-muted/30">
      <div class="flex-1">
        <Input v-model="syncUrl" placeholder="输入 OpenAPI 规范 URL，如 http://localhost:8000/openapi.json" />
      </div>
      <Button variant="secondary" :disabled="!syncUrl.trim() || syncLoading" @click="syncFromOpenApi">
        {{ syncLoading ? '同步中...' : '从 OpenAPI 同步' }}
      </Button>
    </div>

    <Table :loading="loading">
      <template #head>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground w-16">方法</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">路径</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">名称</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">描述</th>
        <th class="text-right px-4 py-3 font-medium text-muted-foreground">操作</th>
      </template>
      <tr v-for="api in apis" :key="api.id" class="border-t hover:bg-muted/30 transition-colors">
        <td class="px-4 py-3">
          <Badge :variant="METHOD_VARIANTS[api.method] ?? 'secondary'" class="font-mono text-xs">
            {{ api.method }}
          </Badge>
        </td>
        <td class="px-4 py-3 font-mono text-sm text-muted-foreground">{{ api.path }}</td>
        <td class="px-4 py-3 font-medium">{{ api.name }}</td>
        <td class="px-4 py-3 text-muted-foreground text-sm">{{ api.description ?? '-' }}</td>
        <td class="px-4 py-3 text-right">
          <Button variant="ghost" size="sm" @click="openEdit(api)">编辑</Button>
          <Button variant="ghost" size="sm" class="text-destructive hover:text-destructive" @click="remove(api)">删除</Button>
        </td>
      </tr>
    </Table>

    <Dialog :open="dialogOpen" :title="isEdit ? '编辑接口' : '新建接口'" :loading="submitting"
      @update:open="dialogOpen = $event" @confirm="submit">
      <div class="space-y-3">
        <div class="space-y-1">
          <label class="text-sm font-medium">名称 *</label>
          <Input v-model="form.name" placeholder="如：获取用户列表" />
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div class="space-y-1">
            <label class="text-sm font-medium">方法</label>
            <Select :model-value="form.method" :options="METHOD_OPTIONS"
              @update:model-value="form.method = String($event)" />
          </div>
          <div class="col-span-2 space-y-1">
            <label class="text-sm font-medium">路径 *</label>
            <Input v-model="form.path" placeholder="如：/api/sys/user" class="font-mono" />
          </div>
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">描述</label>
          <Input v-model="form.description" placeholder="可选" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">OpenAPI 来源 URL</label>
          <Input v-model="form.openapi_url" placeholder="可选，记录该接口来源的 OpenAPI 文档" />
        </div>
      </div>
    </Dialog>
  </div>
</template>
