<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { announcementApi, type Announcement, type AnnouncementCreate, type AnnouncementUpdate } from '@/api/sys/announcement'
import { userApi, type User } from '@/api/sys/user'
import { teamApi, type Team } from '@/api/sys/team'
import { roleApi, type Role } from '@/api/sys/role'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const announcements = ref<Announcement[]>([])
const users = ref<User[]>([])
const teams = ref<Team[]>([])
const roles = ref<Role[]>([])
const loading = ref(false)
const submitting = ref(false)

const showDialog = ref(false)
const editingId = ref<number | null>(null)
const form = ref<AnnouncementCreate>({
  title: '',
  content: '',
  target_type: 'user',
  target_ids: [],
  push_message: false,
})

const targetTypeLabel: Record<string, string> = {
  user: '人员',
  team: '部门',
  role: '角色',
}

const targetOptions = computed(() => {
  if (form.value.target_type === 'user') {
    return users.value.map(u => ({ value: u.id, label: u.nickname ?? u.username }))
  }
  if (form.value.target_type === 'team') {
    return teams.value.map(t => ({ value: t.id, label: t.name }))
  }
  return roles.value.map(r => ({ value: r.id, label: r.name }))
})

async function load() {
  loading.value = true
  try {
    const [a, u, t, r] = await Promise.all([
      announcementApi.list(),
      userApi.list(),
      teamApi.list(),
      roleApi.list(),
    ])
    announcements.value = a.items
    users.value = u.items
    teams.value = t.items
    roles.value = r.items
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = {
    title: '',
    content: '',
    target_type: 'user',
    target_ids: [],
    push_message: false,
  }
  editingId.value = null
}

function openCreate() {
  resetForm()
  showDialog.value = true
}

function openEdit(item: Announcement) {
  editingId.value = item.id
  form.value = {
    title: item.title,
    content: item.content,
    target_type: item.target_type,
    target_ids: [...item.target_ids],
    push_message: item.push_message,
  }
  showDialog.value = true
}

async function submit() {
  const title = form.value.title.trim()
  const content = form.value.content.trim()
  if (!title || !content) return

  submitting.value = true
  try {
    const body: AnnouncementCreate = {
      title,
      content,
      target_type: form.value.target_type,
      target_ids: form.value.target_ids ?? [],
      push_message: form.value.push_message ?? false,
    }
    if (editingId.value) {
      const updateBody: AnnouncementUpdate = { ...body }
      await announcementApi.update(editingId.value, updateBody)
    } else {
      await announcementApi.create(body)
    }
    showDialog.value = false
    resetForm()
    await load()
  } finally {
    submitting.value = false
  }
}

async function remove(id: number) {
  await announcementApi.remove(id)
  announcements.value = announcements.value.filter(a => a.id !== id)
}

function toggleTargetId(id: number) {
  const ids = form.value.target_ids ?? []
  const index = ids.indexOf(id)
  if (index === -1) {
    ids.push(id)
  } else {
    ids.splice(index, 1)
  }
  form.value.target_ids = [...ids]
}

function targetNames(item: Announcement): string {
  if (!item.target_ids.length) return '全部可见'
  let options: { id: number; name: string }[] = []
  if (item.target_type === 'user') {
    options = users.value.map(u => ({ id: u.id, name: u.nickname ?? u.username }))
  } else if (item.target_type === 'team') {
    options = teams.value.map(t => ({ id: t.id, name: t.name }))
  } else {
    options = roles.value.map(r => ({ id: r.id, name: r.name }))
  }
  const names = item.target_ids.map(id => options.find(o => o.id === id)?.name ?? id).join(', ')
  return `${targetTypeLabel[item.target_type]}: ${names}`
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">公告管理</h1>
        <p class="text-sm mt-0.5" style="color: hsl(var(--text-2))">共 {{ announcements.length }} 条公告</p>
      </div>
      <Button size="sm" @click="openCreate">+ 发布公告</Button>
    </div>

    <Card class="p-0 overflow-hidden">
      <div v-if="loading" class="p-12 text-center" style="color: hsl(var(--text-3))">加载中...</div>
      <div v-else-if="announcements.length === 0" class="p-12 text-center" style="color: hsl(var(--text-3))">暂无公告</div>
      <div v-else>
        <div v-for="(item, i) in announcements" :key="item.id"
          class="px-5 py-4 cursor-pointer hover:bg-[hsl(var(--bg-hover))] transition-colors"
          :style="i > 0 ? 'border-top: 1px solid hsl(var(--border-subtle))' : ''"
          @click="router.push(`/sys/announcement/${item.id}`)">
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="font-medium text-sm mb-1">{{ item.title }}</div>
              <p class="text-xs line-clamp-2" style="color: hsl(var(--text-3))">{{ item.content }}</p>
              <div class="flex items-center gap-3 mt-2">
                <span class="text-xs" style="color: hsl(var(--text-3))">{{ targetNames(item) }}</span>
                <span v-if="item.push_message" class="text-xs px-2 py-0.5 rounded-full font-medium" style="background: rgba(59,130,246,0.1); color: #3B82F6;">已推送消息</span>
              </div>
            </div>
            <div class="flex items-center gap-1 flex-shrink-0" @click.stop>
              <button class="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
                style="color: hsl(var(--text-3))"
                @click="openEdit(item)">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </button>
              <button class="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
                style="color: hsl(var(--text-3))"
                @click="remove(item.id)">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Card>

    <Dialog :open="showDialog" :title="editingId ? '编辑公告' : '发布公告'" :loading="submitting"
      @update:open="showDialog = $event; if (!showDialog) resetForm()" @confirm="submit">
      <div class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium">标题</label>
          <Input v-model="form.title" placeholder="公告标题" />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">内容</label>
          <textarea
            v-model="form.content"
            rows="4"
            placeholder="公告正文"
            class="ds-input w-full resize-none"
          />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">显示对象类型</label>
          <select v-model="form.target_type" class="ds-input w-full">
            <option value="user">人员</option>
            <option value="team">部门</option>
            <option value="role">角色</option>
          </select>
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">显示对象（不选则全部可见）</label>
          <div class="max-h-40 overflow-y-auto rounded-lg border p-2 space-y-1" style="border-color: hsl(var(--border-subtle))">
            <label v-for="opt in targetOptions" :key="opt.value"
              class="flex items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer hover:bg-[hsl(var(--bg-hover))]">
              <input
                type="checkbox"
                :checked="form.target_ids?.includes(opt.value)"
                class="w-4 h-4 rounded border-gray-300"
                @change="toggleTargetId(opt.value)"
              >
              <span class="text-sm">{{ opt.label }}</span>
            </label>
          </div>
        </div>
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="form.push_message" type="checkbox" class="w-4 h-4 rounded border-gray-300">
          <span class="text-sm">同时发送消息推送</span>
        </label>
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
textarea.ds-input {
  height: auto;
  padding-top: 8px;
  padding-bottom: 8px;
}
.ds-input:focus { box-shadow: var(--input-focus-ring); }
</style>
