<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { teamApi, type Team } from '@/api/sys/team'
import { userApi, type User } from '@/api/sys/user'
import { roleApi, type Role } from '@/api/sys/role'
import Table from '@/components/ui/Table.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Input from '@/components/ui/Input.vue'

const teams = ref<Team[]>([])
const users = ref<User[]>([])
const roles = ref<Role[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogOpen = ref(false)
const memberDialogOpen = ref(false)
const roleDialogOpen = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const form = ref({ name: '', code: '', description: '', role_ids: [] as number[] })
const memberIds = ref<number[]>([])
const editRoleIds = ref<number[]>([])

const usernameMap = computed(() =>
  Object.fromEntries(users.value.map(u => [u.id, u.nickname ?? u.username]))
)
const roleMap = computed(() =>
  Object.fromEntries(roles.value.map(r => [r.id, r.name]))
)

async function load() {
  loading.value = true
  try {
    const [t, u, r] = await Promise.all([teamApi.list(), userApi.list(), roleApi.list()])
    teams.value = t.items
    users.value = u.items
    roles.value = r.items
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false; editId.value = null
  form.value = { name: '', code: '', description: '', role_ids: [] }
  dialogOpen.value = true
}
function openEdit(team: Team) {
  isEdit.value = true; editId.value = team.id
  form.value = { name: team.name, code: team.code, description: team.description ?? '', role_ids: [...(team.role_ids ?? [])] }
  dialogOpen.value = true
}
function openRoles(team: Team) {
  editId.value = team.id
  editRoleIds.value = [...(team.role_ids ?? [])]
  roleDialogOpen.value = true
}
function openMembers(team: Team) {
  editId.value = team.id
  memberIds.value = [...team.user_ids]
  memberDialogOpen.value = true
}

async function submit() {
  submitting.value = true
  try {
    if (isEdit.value && editId.value) {
      const updated = await teamApi.update(editId.value, { name: form.value.name, description: form.value.description, role_ids: form.value.role_ids })
      const idx = teams.value.findIndex(t => t.id === editId.value)
      if (idx !== -1) teams.value[idx] = { ...teams.value[idx], ...updated }
    } else {
      const created = await teamApi.create({ name: form.value.name, code: form.value.code, description: form.value.description, role_ids: form.value.role_ids })
      teams.value.push(created)
    }
    dialogOpen.value = false
  } finally { submitting.value = false }
}

async function submitRoles() {
  if (!editId.value) return
  submitting.value = true
  try {
    const updated = await teamApi.update(editId.value, { role_ids: editRoleIds.value })
    const idx = teams.value.findIndex(t => t.id === editId.value)
    if (idx !== -1) teams.value[idx] = { ...teams.value[idx], ...updated }
    roleDialogOpen.value = false
  } finally { submitting.value = false }
}

function toggleEditRole(id: number) {
  const idx = editRoleIds.value.indexOf(id)
  if (idx === -1) editRoleIds.value.push(id)
  else editRoleIds.value.splice(idx, 1)
}

async function submitMembers() {
  if (!editId.value) return
  submitting.value = true
  try {
    const updated = await teamApi.updateMembers(editId.value, memberIds.value)
    const idx = teams.value.findIndex(t => t.id === editId.value)
    if (idx !== -1) teams.value[idx] = updated
    memberDialogOpen.value = false
  } finally { submitting.value = false }
}

async function remove(team: Team) {
  if (!confirm(`确定删除团队「${team.name}」？`)) return
  await teamApi.remove(team.id)
  teams.value = teams.value.filter(t => t.id !== team.id)
}

function toggleMember(id: number) {
  const idx = memberIds.value.indexOf(id)
  if (idx === -1) memberIds.value.push(id)
  else memberIds.value.splice(idx, 1)
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">团队管理</h1>
        <p class="text-sm text-muted-foreground mt-0.5">共 {{ teams.length }} 个团队</p>
      </div>
      <Button @click="openCreate">新建团队</Button>
    </div>

    <Table :loading="loading">
      <template #head>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">团队名称</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">描述</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">部门角色</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">成员</th>
        <th class="text-right px-4 py-3 font-medium text-muted-foreground">操作</th>
      </template>
      <tr v-for="team in teams" :key="team.id" class="border-t hover:bg-muted/30 transition-colors">
        <td class="px-4 py-3 font-medium">{{ team.name }}</td>
        <td class="px-4 py-3 text-muted-foreground">{{ team.description ?? '-' }}</td>
        <td class="px-4 py-3">
          <div class="flex flex-wrap gap-1">
            <Badge v-for="rid in (team.role_ids ?? [])" :key="rid" variant="secondary">{{ roleMap[rid] ?? `#${rid}` }}</Badge>
            <span v-if="!(team.role_ids ?? []).length" class="text-muted-foreground text-sm">-</span>
          </div>
        </td>
        <td class="px-4 py-3">
          <div class="flex flex-wrap gap-1">
            <Badge v-for="uid in team.user_ids" :key="uid" variant="outline">{{ usernameMap[uid] ?? `#${uid}` }}</Badge>
            <span v-if="!team.user_ids.length" class="text-muted-foreground text-sm">暂无成员</span>
          </div>
        </td>
        <td class="px-4 py-3 text-right space-x-1">
          <Button variant="ghost" size="sm" @click="openRoles(team)">角色</Button>
          <Button variant="ghost" size="sm" @click="openMembers(team)">成员</Button>
          <Button variant="ghost" size="sm" @click="openEdit(team)">编辑</Button>
          <Button variant="ghost" size="sm" class="text-destructive hover:text-destructive" @click="remove(team)">删除</Button>
        </td>
      </tr>
    </Table>

    <Dialog :open="dialogOpen" :title="isEdit ? '编辑团队' : '新建团队'" :loading="submitting"
      @update:open="dialogOpen = $event" @confirm="submit">
      <div class="space-y-3">
        <div class="space-y-1">
          <label class="text-sm font-medium">团队名称 *</label>
          <Input v-model="form.name" placeholder="请输入团队名称" />
        </div>
        <template v-if="!isEdit">
          <div class="space-y-1">
            <label class="text-sm font-medium">编码 *</label>
            <Input v-model="form.code" placeholder="如：dev_team" />
          </div>
        </template>
        <div class="space-y-1">
          <label class="text-sm font-medium">描述</label>
          <Input v-model="form.description" placeholder="可选" />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">部门角色</label>
          <div class="flex flex-wrap gap-2">
            <button v-for="role in roles" :key="role.id"
              class="px-2.5 py-1 rounded-md text-xs border transition-colors"
              :class="form.role_ids.includes(role.id)
                ? 'bg-primary text-primary-foreground border-primary'
                : 'bg-background border-input hover:bg-muted'"
              @click="form.role_ids.includes(role.id) ? form.role_ids.splice(form.role_ids.indexOf(role.id), 1) : form.role_ids.push(role.id)">
              {{ role.name }}
            </button>
          </div>
        </div>
      </div>
    </Dialog>

    <Dialog :open="roleDialogOpen" title="管理部门角色" :loading="submitting"
      @update:open="roleDialogOpen = $event" @confirm="submitRoles">
      <div class="flex flex-wrap gap-2 py-1">
        <button v-for="role in roles" :key="role.id"
          class="px-2.5 py-1 rounded-md text-xs border transition-colors"
          :class="editRoleIds.includes(role.id)
            ? 'bg-primary text-primary-foreground border-primary'
            : 'bg-background border-input hover:bg-muted'"
          @click="toggleEditRole(role.id)">
          {{ role.name }}
        </button>
      </div>
    </Dialog>

    <Dialog :open="memberDialogOpen" title="管理成员" :loading="submitting"
      @update:open="memberDialogOpen = $event" @confirm="submitMembers">
      <div class="flex flex-wrap gap-2 py-1">
        <button v-for="user in users" :key="user.id"
          class="px-2.5 py-1 rounded-md text-xs border transition-colors"
          :class="memberIds.includes(user.id)
            ? 'bg-primary text-primary-foreground border-primary'
            : 'bg-background border-input hover:bg-muted'"
          @click="toggleMember(user.id)">
          {{ user.nickname ?? user.username }}
        </button>
      </div>
    </Dialog>
  </div>
</template>
