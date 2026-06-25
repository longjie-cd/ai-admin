<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { messageApi, type Message } from '@/api/sys/message'
import { userApi, type User } from '@/api/sys/user'
import { teamApi, type Team } from '@/api/sys/team'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import Dialog from '@/components/ui/Dialog.vue'

const router = useRouter()

const messages = ref<Message[]>([])
const users = ref<User[]>([])
const teams = ref<Team[]>([])
const loading = ref(false)
const filter = ref<'all' | 'unread' | 'read'>('all')
const showCreate = ref(false)
const submitting = ref(false)
const form = ref<{
  send_scope: 'user' | 'team' | 'all'
  user_id: string
  team_id: string
  title: string
  content: string
  type: string
}>({
  send_scope: 'user',
  user_id: '',
  team_id: '',
  title: '',
  content: '',
  type: 'info',
})

const filtered = computed(() => {
  if (filter.value === 'unread') return messages.value.filter(m => !m.is_read)
  if (filter.value === 'read') return messages.value.filter(m => m.is_read)
  return messages.value
})

const unreadCount = computed(() => messages.value.filter(m => !m.is_read).length)

const typeConfig: Record<string, { label: string; color: string; bg: string }> = {
  info:    { label: '通知', color: '#3B82F6', bg: 'rgba(59,130,246,0.1)' },
  success: { label: '成功', color: '#10B981', bg: 'rgba(16,185,129,0.1)' },
  warning: { label: '警告', color: '#F59E0B', bg: 'rgba(245,158,11,0.1)' },
  error:   { label: '错误', color: '#EF4444', bg: 'rgba(239,68,68,0.1)' },
}

async function load() {
  loading.value = true
  try {
    const [messageRes, userRes, teamRes] = await Promise.all([
      messageApi.list(),
      userApi.list(),
      teamApi.list(),
    ])
    messages.value = messageRes.items
    users.value = userRes.items
    teams.value = teamRes.items
  }
  finally { loading.value = false }
}

async function markRead(msg: Message) {
  if (!msg.is_read) {
    await messageApi.update(msg.id, { is_read: true })
    msg.is_read = true
  }
  if (msg.link) {
    await router.push(msg.link)
  }
}

async function markAllRead() {
  await messageApi.markAllRead()
  messages.value.forEach(m => m.is_read = true)
}

async function remove(id: number) {
  await messageApi.remove(id)
  messages.value = messages.value.filter(m => m.id !== id)
}

const userOptions = computed(() => [
  { label: '请选择接收人', value: '' },
  ...users.value.map(user => ({ label: `${user.nickname || user.username} (${user.username})`, value: String(user.id) })),
])

const teamOptions = computed(() => [
  { label: '请选择团队', value: '' },
  ...teams.value.map(team => ({ label: `${team.name} (${team.user_ids.length}人)`, value: String(team.id) })),
])

const scopeOptions = [
  { label: '单人发送', value: 'user' },
  { label: '团队发送', value: 'team' },
  { label: '全员广播', value: 'all' },
]

const typeOptions = [
  { label: '通知', value: 'info' },
  { label: '成功', value: 'success' },
  { label: '警告', value: 'warning' },
  { label: '错误', value: 'error' },
]

function resetForm() {
  form.value = { send_scope: 'user', user_id: '', team_id: '', title: '', content: '', type: 'info' }
}

function openCreate() {
  resetForm()
  showCreate.value = true
}

function updateSendScope(value: string | number) {
  const next = String(value)
  form.value.send_scope = (next === 'team' || next === 'all') ? next : 'user'
  form.value.user_id = ''
  form.value.team_id = ''
}

async function create() {
  if (!form.value.title.trim() || !form.value.content.trim()) return
  submitting.value = true
  try {
    if (form.value.send_scope === 'user' && !form.value.user_id) return
    if (form.value.send_scope === 'team' && !form.value.team_id) return
    const payload = {
      send_scope: form.value.send_scope,
      title: form.value.title,
      content: form.value.content,
      type: form.value.type,
    } as const

    await messageApi.create({
      ...payload,
      ...(form.value.send_scope === 'user' ? { user_id: Number(form.value.user_id) } : {}),
      ...(form.value.send_scope === 'team' ? { team_id: Number(form.value.team_id) } : {}),
    })
    showCreate.value = false
    resetForm()
    await load()
  } finally {
    submitting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">消息管理</h1>
        <p class="text-sm mt-0.5" style="color: hsl(var(--text-2))">共 {{ messages.length }} 条，{{ unreadCount }} 条未读</p>
      </div>
      <div class="flex gap-2">
        <Button size="sm" @click="openCreate">发消息</Button>
        <Button variant="outline" size="sm" @click="markAllRead" :disabled="unreadCount === 0">全部已读</Button>
        <Button variant="outline" size="sm" @click="load">刷新</Button>
      </div>
    </div>

    <!-- Filter tabs -->
    <div class="flex gap-1 p-1 rounded-xl" style="background: hsl(var(--bg-sunken)); width: fit-content">
      <button v-for="t in [['all','全部'],['unread','未读'],['read','已读']]" :key="t[0]"
        class="px-4 py-1.5 rounded-lg text-sm font-medium transition-all"
        :style="filter === t[0]
          ? 'background: hsl(var(--bg-surface)); color: hsl(var(--text-1)); box-shadow: var(--shadow-xs)'
          : 'color: hsl(var(--text-2))'"
        @click="filter = t[0] as any">{{ t[1] }}</button>
    </div>

    <!-- Message list -->
    <div class="rounded-2xl border overflow-hidden" style="background: hsl(var(--card)); border-color: hsl(var(--border-subtle))">
      <div v-if="loading" class="p-12 text-center" style="color: hsl(var(--text-3))">加载中...</div>
      <div v-else-if="filtered.length === 0" class="p-12 text-center" style="color: hsl(var(--text-3))">暂无消息</div>
      <div v-else>
        <div v-for="(msg, i) in filtered" :key="msg.id"
          class="flex items-start gap-4 p-5 cursor-pointer transition-colors"
          :style="[
            i > 0 ? 'border-top: 1px solid hsl(var(--border-subtle))' : '',
            !msg.is_read ? 'background: hsl(var(--primary) / 0.03)' : '',
          ]"
          @click="markRead(msg)"
        >
          <!-- Type badge -->
          <div class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
            :style="{ background: typeConfig[msg.type]?.bg }">
            <div class="w-2.5 h-2.5 rounded-full" :style="{ background: typeConfig[msg.type]?.color }"/>
          </div>
          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-sm font-medium" :class="!msg.is_read ? '' : 'opacity-70'">{{ msg.title }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                :style="{ background: typeConfig[msg.type]?.bg, color: typeConfig[msg.type]?.color }">
                {{ typeConfig[msg.type]?.label }}
              </span>
              <span v-if="!msg.is_read" class="w-2 h-2 rounded-full flex-shrink-0" style="background: hsl(var(--primary))"/>
            </div>
            <p class="text-sm" style="color: hsl(var(--text-2))">{{ msg.content }}</p>
            <p class="text-xs mt-1.5" style="color: hsl(var(--text-3))">{{ msg.created_at }}</p>
          </div>
          <!-- Delete -->
          <button class="w-7 h-7 rounded-lg flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all flex-shrink-0"
            style="color: hsl(var(--text-3))"
            @click.stop="remove(msg.id)">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <Dialog :open="showCreate" title="发送消息" :loading="submitting" @close="showCreate = false" @confirm="create">
      <div class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium">发送范围</label>
          <Select :model-value="form.send_scope" :options="scopeOptions" @update:model-value="updateSendScope" />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">接收人</label>
          <Select v-if="form.send_scope === 'user'" :model-value="form.user_id" :options="userOptions" @update:model-value="form.user_id = String($event)" />
          <Select v-else-if="form.send_scope === 'team'" :model-value="form.team_id" :options="teamOptions" @update:model-value="form.team_id = String($event)" />
          <div v-else class="rounded-xl border px-3 py-2 text-sm" style="border-color: hsl(var(--border-default)); color: hsl(var(--text-2)); background: hsl(var(--bg-surface));">
            将向全部用户发送
          </div>
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">消息类型</label>
          <Select :model-value="form.type" :options="typeOptions" @update:model-value="form.type = String($event)" />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">标题</label>
          <Input v-model="form.title" placeholder="消息标题" />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">内容</label>
          <textarea
            v-model="form.content"
            rows="4"
            class="w-full rounded-xl border px-3 py-2 text-sm outline-none"
            style="border-color: hsl(var(--border-default)); background: hsl(var(--bg-surface)); color: hsl(var(--text-1));"
            placeholder="输入消息内容"
          />
        </div>
      </div>
    </Dialog>
  </div>
</template>
