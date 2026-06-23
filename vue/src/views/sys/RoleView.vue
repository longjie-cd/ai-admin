<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { roleApi, type Role } from '@/api/sys/role'
import { permissionApi, type Permission } from '@/api/sys/permission'
import Table from '@/components/ui/Table.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Input from '@/components/ui/Input.vue'

const roles = ref<Role[]>([])
const permissions = ref<Permission[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogOpen = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const form = ref({ name: '', code: '', description: '', permission_ids: [] as number[] })

// group permissions by group field
const permGroups = computed(() => {
  const map = new Map<string, Permission[]>()
  permissions.value.forEach(p => {
    if (!map.has(p.group)) map.set(p.group, [])
    map.get(p.group)!.push(p)
  })
  return map
})

async function load() {
  loading.value = true
  try {
    const [r, p] = await Promise.all([roleApi.list(), permissionApi.list()])
    roles.value = r.items
    permissions.value = p.items
  } finally { loading.value = false }
}

function openCreate() {
  isEdit.value = false; editId.value = null
  form.value = { name: '', code: '', description: '', permission_ids: [] }
  dialogOpen.value = true
}
function openEdit(role: Role) {
  isEdit.value = true; editId.value = role.id
  form.value = { name: role.name, code: role.code, description: role.description ?? '', permission_ids: [...role.permission_ids] }
  dialogOpen.value = true
}

async function submit() {
  submitting.value = true
  try {
    if (isEdit.value && editId.value) {
      const updated = await roleApi.update(editId.value, { name: form.value.name, description: form.value.description, permission_ids: form.value.permission_ids })
      const idx = roles.value.findIndex(r => r.id === editId.value)
      if (idx !== -1) roles.value[idx] = updated
    } else {
      roles.value.push(await roleApi.create(form.value))
    }
    dialogOpen.value = false
  } finally { submitting.value = false }
}

async function remove(role: Role) {
  if (!confirm(`确定删除角色「${role.name}」？`)) return
  await roleApi.remove(role.id)
  roles.value = roles.value.filter(r => r.id !== role.id)
}

function togglePerm(id: number) {
  const idx = form.value.permission_ids.indexOf(id)
  if (idx === -1) form.value.permission_ids.push(id)
  else form.value.permission_ids.splice(idx, 1)
}

function toggleGroup(group: string) {
  const ids = permGroups.value.get(group)!.map(p => p.id)
  const allChecked = ids.every(id => form.value.permission_ids.includes(id))
  if (allChecked) form.value.permission_ids = form.value.permission_ids.filter(id => !ids.includes(id))
  else {
    const set = new Set([...form.value.permission_ids, ...ids])
    form.value.permission_ids = [...set]
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">角色管理</h1>
        <p class="text-sm text-muted-foreground mt-0.5">共 {{ roles.length }} 个角色</p>
      </div>
      <Button @click="openCreate">新建角色</Button>
    </div>

    <Table :loading="loading">
      <template #head>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">角色名称</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">标识码</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">描述</th>
        <th class="text-left px-4 py-3 font-medium text-muted-foreground">权限数</th>
        <th class="text-right px-4 py-3 font-medium text-muted-foreground">操作</th>
      </template>
      <tr v-for="role in roles" :key="role.id" class="border-t hover:bg-muted/30 transition-colors">
        <td class="px-4 py-3 font-medium">{{ role.name }}</td>
        <td class="px-4 py-3"><Badge variant="outline">{{ role.code }}</Badge></td>
        <td class="px-4 py-3 text-muted-foreground">{{ role.description ?? '-' }}</td>
        <td class="px-4 py-3"><Badge variant="secondary">{{ role.permission_ids.length }} 项</Badge></td>
        <td class="px-4 py-3 text-right">
          <Button variant="ghost" size="sm" @click="openEdit(role)">编辑</Button>
          <Button variant="ghost" size="sm" class="text-destructive hover:text-destructive" @click="remove(role)">删除</Button>
        </td>
      </tr>
    </Table>

    <Dialog :open="dialogOpen" :title="isEdit ? '编辑角色' : '新建角色'" :loading="submitting"
      @update:open="dialogOpen = $event" @confirm="submit">
      <div class="space-y-3">
        <div class="space-y-1">
          <label class="text-sm font-medium">角色名称 *</label>
          <Input v-model="form.name" placeholder="如：运营人员" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">标识码 *</label>
          <Input v-model="form.code" placeholder="如：operator（不可重复）" :disabled="isEdit" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">描述</label>
          <Input v-model="form.description" placeholder="可选" />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-medium">权限分配</label>
          <div v-for="[group, perms] in permGroups" :key="group" class="space-y-1.5">
            <button class="text-xs font-medium text-muted-foreground hover:text-foreground flex items-center gap-1"
              @click="toggleGroup(group)">
              <span>{{ group }}</span>
              <span class="text-[10px]">（点击全选）</span>
            </button>
            <div class="flex flex-wrap gap-1.5 pl-1">
              <button v-for="perm in perms" :key="perm.id"
                class="px-2 py-0.5 rounded text-xs border transition-colors"
                :class="form.permission_ids.includes(perm.id)
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-background border-input hover:bg-muted'"
                @click="togglePerm(perm.id)">
                {{ perm.name }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Dialog>
  </div>
</template>
