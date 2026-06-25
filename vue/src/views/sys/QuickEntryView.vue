<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { quickEntryApi, type QuickEntry, type QuickEntryCreate, type QuickEntryUpdate } from '@/api/sys/quick_entry'
import { userApi, type User } from '@/api/sys/user'
import { teamApi, type Team } from '@/api/sys/team'
import { roleApi, type Role } from '@/api/sys/role'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const entries = ref<QuickEntry[]>([])
const users = ref<User[]>([])
const teams = ref<Team[]>([])
const roles = ref<Role[]>([])
const loading = ref(false)
const submitting = ref(false)

const showDialog = ref(false)
const editingId = ref<number | null>(null)
const form = ref<QuickEntryCreate>({
  name: '',
  icon: '',
  path: '',
  auth_type: 'user',
  auth_ids: [],
  sort: 0,
})

const authTypeLabel: Record<string, string> = {
  user: '人员',
  team: '部门',
  role: '角色',
}

const authOptions = computed(() => {
  if (form.value.auth_type === 'user') {
    return users.value.map(u => ({ value: u.id, label: u.nickname ?? u.username }))
  }
  if (form.value.auth_type === 'team') {
    return teams.value.map(t => ({ value: t.id, label: t.name }))
  }
  return roles.value.map(r => ({ value: r.id, label: r.name }))
})

async function load() {
  loading.value = true
  try {
    const [e, u, t, r] = await Promise.all([
      quickEntryApi.list(),
      userApi.list(),
      teamApi.list(),
      roleApi.list(),
    ])
    entries.value = e.items
    users.value = u.items
    teams.value = t.items
    roles.value = r.items
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = {
    name: '',
    icon: '',
    path: '',
    auth_type: 'user',
    auth_ids: [],
    sort: 0,
  }
  editingId.value = null
}

function openCreate() {
  resetForm()
  showDialog.value = true
}

function openEdit(entry: QuickEntry) {
  editingId.value = entry.id
  form.value = {
    name: entry.name,
    icon: entry.icon ?? '',
    path: entry.path,
    auth_type: entry.auth_type,
    auth_ids: [...entry.auth_ids],
    sort: entry.sort,
  }
  showDialog.value = true
}

async function submit() {
  const name = form.value.name.trim()
  const path = form.value.path.trim()
  if (!name || !path) return

  submitting.value = true
  try {
    const body: QuickEntryCreate = {
      name,
      path,
      icon: form.value.icon || undefined,
      auth_type: form.value.auth_type,
      auth_ids: form.value.auth_ids,
      sort: form.value.sort ?? 0,
    }
    if (editingId.value) {
      const updateBody: QuickEntryUpdate = { ...body }
      await quickEntryApi.update(editingId.value, updateBody)
    } else {
      await quickEntryApi.create(body)
    }
    showDialog.value = false
    resetForm()
    await load()
  } finally {
    submitting.value = false
  }
}

async function remove(id: number) {
  await quickEntryApi.remove(id)
  entries.value = entries.value.filter(e => e.id !== id)
}

function toggleAuthId(id: number) {
  const ids = form.value.auth_ids ?? []
  const index = ids.indexOf(id)
  if (index === -1) {
    ids.push(id)
  } else {
    ids.splice(index, 1)
  }
  form.value.auth_ids = [...ids]
}

function authNames(entry: QuickEntry): string {
  if (!entry.auth_ids.length) return '全部可见'
  let options: { id: number; name: string }[] = []
  if (entry.auth_type === 'user') {
    options = users.value.map(u => ({ id: u.id, name: u.nickname ?? u.username }))
  } else if (entry.auth_type === 'team') {
    options = teams.value.map(t => ({ id: t.id, name: t.name }))
  } else {
    options = roles.value.map(r => ({ id: r.id, name: r.name }))
  }
  const names = entry.auth_ids.map(id => options.find(o => o.id === id)?.name ?? id).join(', ')
  return `${authTypeLabel[entry.auth_type]}: ${names}`
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">快捷入口</h1>
        <p class="text-sm mt-0.5" style="color: hsl(var(--text-2))">共 {{ entries.length }} 个入口</p>
      </div>
      <Button size="sm" @click="openCreate">+ 添加快捷入口</Button>
    </div>

    <Card class="p-0 overflow-hidden">
      <div v-if="loading" class="p-12 text-center" style="color: hsl(var(--text-3))">加载中...</div>
      <div v-else-if="entries.length === 0" class="p-12 text-center" style="color: hsl(var(--text-3))">暂无快捷入口</div>
      <div v-else>
        <div v-for="(entry, i) in entries" :key="entry.id"
          class="flex items-center gap-4 px-5 py-4"
          :style="i > 0 ? 'border-top: 1px solid hsl(var(--border-subtle))' : ''">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white flex-shrink-0"
            style="background: hsl(var(--primary))">
            <svg v-if="entry.icon === 'external'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-medium text-sm">{{ entry.name }}</div>
            <div class="text-xs mt-0.5 truncate" style="color: hsl(var(--text-3))">{{ entry.path }}</div>
            <div class="text-xs mt-1" style="color: hsl(var(--text-3))">{{ authNames(entry) }}</div>
          </div>
          <div class="flex items-center gap-1">
            <button class="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
              style="color: hsl(var(--text-3))"
              @click="openEdit(entry)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </button>
            <button class="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
              style="color: hsl(var(--text-3))"
              @click="remove(entry.id)">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </Card>

    <Dialog :open="showDialog" :title="editingId ? '编辑快捷入口' : '添加快捷入口'" :loading="submitting"
      @update:open="showDialog = $event; if (!showDialog) resetForm()" @confirm="submit">
      <div class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium">名称</label>
          <Input v-model="form.name" placeholder="入口名称" />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">跳转路径</label>
          <Input v-model="form.path" placeholder="如 /sys/user 或 https://example.com" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-1.5">
            <label class="text-sm font-medium">授权对象类型</label>
            <select v-model="form.auth_type" class="ds-input w-full">
              <option value="user">人员</option>
              <option value="team">部门</option>
              <option value="role">角色</option>
            </select>
          </div>
          <div class="space-y-1.5">
            <label class="text-sm font-medium">排序</label>
            <Input v-model="form.sort" type="number" placeholder="数字越小越靠前" />
          </div>
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">授权对象（不选则全部可见）</label>
          <div class="max-h-40 overflow-y-auto rounded-lg border p-2 space-y-1" style="border-color: hsl(var(--border-subtle))">
            <label v-for="opt in authOptions" :key="opt.value"
              class="flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer hover:bg-[hsl(var(--bg-hover))]">
              <input
                type="checkbox"
                :checked="form.auth_ids?.includes(opt.value)"
                class="w-4 h-4 rounded border-gray-300"
                @change="toggleAuthId(opt.value)"
              >
              <span class="text-sm">{{ opt.label }}</span>
            </label>
          </div>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<style scoped>
.ds-input {
  height: var(--input-h);
  padding: 0 var(--input-px);
  border-radius: var(--input-radius);
  font-size: var(--input-font-size);
  border: 1px solid var(--input-border);
  background: var(--input-bg);
  color: hsl(var(--text-1));
  outline: none;
  width: 100%;
  transition: box-shadow var(--input-transition);
}
.ds-input:focus { box-shadow: var(--input-focus-ring); }
</style>
