<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { userApi, type User, type UserCreate, type UserUpdate } from '@/api/sys/user'
import { roleApi, type Role } from '@/api/sys/role'
import { teamApi, type Team } from '@/api/sys/team'
import Table from '@/components/ui/Table.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'

const users = ref<User[]>([])
const roles = ref<Role[]>([])
const teams = ref<Team[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogOpen = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)

const DATA_SCOPE_OPTIONS = [
  { label: '仅个人数据', value: 'personal' },
  { label: '指定部门数据', value: 'department' },
  { label: '全部数据', value: 'all' },
]

const form = ref<UserCreate & UserUpdate>({
  username: '', password: '', nickname: '', email: '',
  role_ids: [], team_id: null, disabled: false,
  data_scope: 'personal', department_ids: [],
})

const roleOptions = computed(() => roles.value.map(r => ({ label: r.name, value: r.id })))
const teamOptions = computed(() => [
  { label: '无', value: '' },
  ...teams.value.map(t => ({ label: t.name, value: t.id })),
])

async function load() {
  loading.value = true
  try {
    const [u, r, t] = await Promise.all([userApi.list(), roleApi.list(), teamApi.list()])
    users.value = u.items
    roles.value = r.items
    teams.value = t.items
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  editId.value = null
  form.value = { username: '', password: '', nickname: '', email: '', role_ids: [], team_id: null, disabled: false, data_scope: 'personal', department_ids: [] }
  dialogOpen.value = true
}

function openEdit(user: User) {
  isEdit.value = true
  editId.value = user.id
  form.value = { username: user.username, nickname: user.nickname ?? '', email: user.email ?? '', role_ids: [...user.role_ids], team_id: user.team_id, disabled: user.disabled, data_scope: user.data_scope ?? 'personal', department_ids: [...(user.department_ids ?? [])] }
  dialogOpen.value = true
}

async function submit() {
  submitting.value = true
  try {
    if (isEdit.value && editId.value) {
      const updated = await userApi.update(editId.value, {
        nickname: form.value.nickname,
        email: form.value.email,
        disabled: form.value.disabled,
        role_ids: form.value.role_ids,
        team_id: form.value.team_id || null,
        data_scope: form.value.data_scope,
        department_ids: form.value.department_ids,
      })
      const idx = users.value.findIndex(u => u.id === editId.value)
      if (idx !== -1) users.value[idx] = updated
    } else {
      const created = await userApi.create({ ...form.value, team_id: form.value.team_id || null, data_scope: form.value.data_scope, department_ids: form.value.department_ids })
      users.value.push(created)
    }
    dialogOpen.value = false
  } finally {
    submitting.value = false
  }
}

async function remove(user: User) {
  if (!confirm(`确定删除用户「${user.username}」？`)) return
  await userApi.remove(user.id)
  users.value = users.value.filter(u => u.id !== user.id)
}

function getRoleName(id: number) {
  return roles.value.find(r => r.id === id)?.name ?? `#${id}`
}
function getTeamName(id: number | null) {
  if (!id) return '-'
  return teams.value.find(t => t.id === id)?.name ?? `#${id}`
}

function toggleRole(id: number) {
  const ids = form.value.role_ids ?? []
  const idx = ids.indexOf(id)
  if (idx === -1) ids.push(id)
  else ids.splice(idx, 1)
  form.value.role_ids = ids
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">用户管理</h1>
        <p class="text-sm text-muted-foreground mt-0.5">共 {{ users.length }} 名用户</p>
      </div>
      <Button @click="openCreate">新建用户</Button>
    </div>

    <Table :loading="loading">
      <template #head>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">用户名</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">昵称</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">邮箱</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">角色</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">团队</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">数据权限</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">状态</th>
        <th class="text-right px-4 py-3 font-medium text-muted-foreground">操作</th>
      </template>
      <tr v-for="user in users" :key="user.id" class="border-t hover:bg-muted/30 transition-colors">
        <td class="px-4 py-3 font-medium">{{ user.username }}</td>
        <td class="px-4 py-3 text-muted-foreground">{{ user.nickname ?? '-' }}</td>
        <td class="px-4 py-3 text-muted-foreground">{{ user.email ?? '-' }}</td>
        <td class="px-4 py-3">
          <div class="flex flex-wrap gap-1">
            <Badge v-for="rid in user.role_ids" :key="rid" variant="secondary">{{ getRoleName(rid) }}</Badge>
            <span v-if="!user.role_ids.length" class="text-muted-foreground">-</span>
          </div>
        </td>
        <td class="px-4 py-3 text-muted-foreground">{{ getTeamName(user.team_id) }}</td>
        <td class="px-4 py-3">
          <Badge :variant="user.data_scope === 'all' ? 'destructive' : user.data_scope === 'department' ? 'secondary' : 'outline'" class="text-xs">
            {{ user.data_scope === 'all' ? '全部' : user.data_scope === 'department' ? '部门' : '个人' }}
          </Badge>
        </td>
        <td class="px-4 py-3">
          <Badge :variant="user.disabled ? 'destructive' : 'success'">
            {{ user.disabled ? '禁用' : '正常' }}
          </Badge>
        </td>
        <td class="px-4 py-3 text-right">
          <Button variant="ghost" size="sm" @click="openEdit(user)">编辑</Button>
          <Button variant="ghost" size="sm" class="text-destructive hover:text-destructive" @click="remove(user)">删除</Button>
        </td>
      </tr>
    </Table>

    <Dialog :open="dialogOpen" :title="isEdit ? '编辑用户' : '新建用户'" :loading="submitting"
      @update:open="dialogOpen = $event" @confirm="submit">
      <div class="space-y-3">
        <template v-if="!isEdit">
          <div class="space-y-1">
            <label class="text-sm font-medium">用户名 *</label>
            <Input v-model="form.username" placeholder="至少 3 个字符" />
          </div>
          <div class="space-y-1">
            <label class="text-sm font-medium">密码 *</label>
            <Input v-model="form.password" type="password" placeholder="至少 6 个字符" />
          </div>
        </template>
        <div class="space-y-1">
          <label class="text-sm font-medium">昵称</label>
          <Input v-model="form.nickname" placeholder="可选" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">邮箱</label>
          <Input v-model="form.email" placeholder="可选" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">所属团队</label>
          <Select :model-value="form.team_id ?? ''" :options="teamOptions" placeholder="请选择"
            @update:model-value="form.team_id = $event === '' ? null : Number($event)" />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">角色</label>
          <div class="flex flex-wrap gap-2">
            <button v-for="role in roles" :key="role.id"
              class="px-2.5 py-1 rounded-md text-xs border transition-colors"
              :class="(form.role_ids ?? []).includes(role.id)
                ? 'bg-primary text-primary-foreground border-primary'
                : 'bg-background border-input hover:bg-muted'"
              @click="toggleRole(role.id)">
              {{ role.name }}
            </button>
          </div>
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">数据权限</label>
          <Select :model-value="form.data_scope ?? 'personal'" :options="DATA_SCOPE_OPTIONS"
            @update:model-value="form.data_scope = $event" />
        </div>
        <div v-if="isEdit" class="flex items-center gap-2">
          <input id="disabled" type="checkbox" :checked="form.disabled" @change="form.disabled = ($event.target as HTMLInputElement).checked" />
          <label for="disabled" class="text-sm">禁用账号</label>
        </div>
      </div>
    </Dialog>
  </div>
</template>
