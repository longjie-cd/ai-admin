<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { permissionApi, type Permission } from '@/api/sys/permission'
import Table from '@/components/ui/Table.vue'
import Button from '@/components/ui/Button.vue'
import Badge from '@/components/ui/Badge.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Input from '@/components/ui/Input.vue'

const permissions = ref<Permission[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogOpen = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const form = ref({ name: '', code: '', group: '', description: '' })

const groups = computed(() => [...new Set(permissions.value.map(p => p.group))])
const grouped = computed(() => {
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
    const res = await permissionApi.list()
    permissions.value = res.items
  } finally { loading.value = false }
}

function openCreate() {
  isEdit.value = false; editId.value = null
  form.value = { name: '', code: '', group: '', description: '' }
  dialogOpen.value = true
}
function openEdit(p: Permission) {
  isEdit.value = true; editId.value = p.id
  form.value = { name: p.name, code: p.code, group: p.group, description: p.description ?? '' }
  dialogOpen.value = true
}

async function submit() {
  submitting.value = true
  try {
    if (isEdit.value && editId.value) {
      const updated = await permissionApi.update(editId.value, { name: form.value.name, group: form.value.group, description: form.value.description })
      const idx = permissions.value.findIndex(p => p.id === editId.value)
      if (idx !== -1) permissions.value[idx] = updated
    } else {
      permissions.value.push(await permissionApi.create(form.value))
    }
    dialogOpen.value = false
  } finally { submitting.value = false }
}

async function remove(p: Permission) {
  if (!confirm(`确定删除权限「${p.name}」？`)) return
  await permissionApi.remove(p.id)
  permissions.value = permissions.value.filter(x => x.id !== p.id)
}

onMounted(load)
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">权限管理</h1>
        <p class="text-sm text-muted-foreground mt-0.5">共 {{ permissions.length }} 项权限，{{ groups.length }} 个分组</p>
      </div>
      <Button @click="openCreate">新建权限</Button>
    </div>

    <div v-if="loading" class="py-12 text-center text-muted-foreground">加载中...</div>

    <div v-else class="space-y-4">
      <div v-for="[group, perms] in grouped" :key="group" class="rounded-lg border overflow-hidden">
        <div class="px-4 py-2.5 bg-muted/50 border-b flex items-center justify-between">
          <span class="text-sm font-medium">{{ group }}</span>
          <Badge variant="secondary">{{ perms.length }} 项</Badge>
        </div>
        <table class="w-full text-sm">
          <tbody>
            <tr v-for="perm in perms" :key="perm.id" class="border-t first:border-t-0 hover:bg-muted/30 transition-colors">
              <td class="px-4 py-2.5 font-medium w-36">{{ perm.name }}</td>
              <td class="px-4 py-2.5"><code class="text-xs bg-muted px-1.5 py-0.5 rounded">{{ perm.code }}</code></td>
              <td class="px-4 py-2.5 text-muted-foreground">{{ perm.description || '-' }}</td>
              <td class="px-4 py-2.5 text-right">
                <Button variant="ghost" size="sm" @click="openEdit(perm)">编辑</Button>
                <Button variant="ghost" size="sm" class="text-destructive hover:text-destructive" @click="remove(perm)">删除</Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Dialog :open="dialogOpen" :title="isEdit ? '编辑权限' : '新建权限'" :loading="submitting"
      @update:open="dialogOpen = $event" @confirm="submit">
      <div class="space-y-3">
        <div class="space-y-1">
          <label class="text-sm font-medium">权限名称 *</label>
          <Input v-model="form.name" placeholder="如：查看报表" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">权限码 *</label>
          <Input v-model="form.code" placeholder="如：sys:report:view" :disabled="isEdit" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">分组 *</label>
          <Input v-model="form.group" placeholder="如：报表管理" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">描述</label>
          <Input v-model="form.description" placeholder="可选" />
        </div>
      </div>
    </Dialog>
  </div>
</template>
