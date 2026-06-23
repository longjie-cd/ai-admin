<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { menuApi, type Menu } from '@/api/sys/menu'
import { apiInterfaceApi, type ApiInterface } from '@/api/sys/api_interface'
import { permissionApi, type Permission } from '@/api/sys/permission'
import Button from '@/components/ui/Button.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'
import Badge from '@/components/ui/Badge.vue'
import MenuTreeItem from '@/components/MenuTreeItem.vue'

const menus = ref<Menu[]>([])
const allMenusFlat = ref<Menu[]>([])
const apis = ref<ApiInterface[]>([])
const permissions = ref<Permission[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogOpen = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const selectedItem = ref<Menu | null>(null)

const form = ref({
  parent_id: null as number | null,
  name: '',
  path: '',
  icon: '',
  sort: 0,
  api_id: null as number | null,
  permission_ids: [] as number[],
})

const parentOptions = computed(() => [
  { label: '无（根菜单）', value: '' },
  ...allMenusFlat.value
    .filter(m => m.id !== editId.value)
    .map(m => ({ label: m.name, value: m.id })),
])

const apiOptions = computed(() => [
  { label: '无', value: '' },
  ...apis.value.map(a => ({ label: `${a.method} ${a.path}`, value: a.id })),
])

function flatten(items: Menu[]): Menu[] {
  const result: Menu[] = []
  for (const item of items) {
    result.push(item)
    if (item.children?.length) result.push(...flatten(item.children))
  }
  return result
}

async function load() {
  loading.value = true
  try {
    const [m, a, p] = await Promise.all([
      menuApi.list(),
      apiInterfaceApi.list(),
      permissionApi.list(),
    ])
    menus.value = m.items
    allMenusFlat.value = flatten(m.items)
    apis.value = a.items
    permissions.value = p.items
    if (menus.value.length && !selectedItem.value) {
      selectedItem.value = menus.value[0]
    }
  } finally {
    loading.value = false
  }
}

function openCreate(parentId?: number) {
  isEdit.value = false
  editId.value = null
  form.value = { parent_id: parentId ?? null, name: '', path: '', icon: '', sort: 0, api_id: null, permission_ids: [] }
  dialogOpen.value = true
}

function openEdit(menu: Menu) {
  isEdit.value = true
  editId.value = menu.id
  form.value = {
    parent_id: menu.parent_id ?? null,
    name: menu.name,
    path: menu.path,
    icon: menu.icon ?? '',
    sort: menu.sort,
    api_id: menu.api_id ?? null,
    permission_ids: [...menu.permission_ids],
  }
  dialogOpen.value = true
}

async function submit() {
  submitting.value = true
  try {
    const payload = {
      ...form.value,
      parent_id: form.value.parent_id ?? undefined,
      api_id: form.value.api_id ?? undefined,
    }
    if (isEdit.value && editId.value) {
      await menuApi.update(editId.value, payload)
    } else {
      await menuApi.create(payload)
    }
    dialogOpen.value = false
    await load()
  } finally {
    submitting.value = false
  }
}

async function remove(menu: Menu) {
  if (!confirm(`确定删除菜单「${menu.name}」？`)) return
  await menuApi.remove(menu.id)
  if (selectedItem.value?.id === menu.id) selectedItem.value = null
  await load()
}

function togglePermission(id: number) {
  const idx = form.value.permission_ids.indexOf(id)
  if (idx === -1) form.value.permission_ids.push(id)
  else form.value.permission_ids.splice(idx, 1)
}

function getApiLabel(id?: number) {
  if (!id) return null
  const a = apis.value.find(x => x.id === id)
  return a ? `${a.method} ${a.path}` : null
}

function getPermissionNames(ids: number[]) {
  return ids.map(id => permissions.value.find(p => p.id === id)?.name ?? `#${id}`)
}

onMounted(load)
</script>

<template>
  <div class="flex h-[calc(100vh-120px)] gap-4">
    <!-- 左侧菜单树 -->
    <div class="w-72 flex flex-col border rounded-lg bg-muted/30">
      <div class="px-4 py-3 border-b flex items-center justify-between flex-shrink-0">
        <h3 class="font-medium text-sm">菜单树</h3>
        <Button size="sm" @click="openCreate()">新建</Button>
      </div>
      <div v-if="loading" class="flex-1 flex items-center justify-center text-muted-foreground text-sm">加载中...</div>
      <div v-else class="flex-1 overflow-y-auto p-2">
        <div v-if="!menus.length" class="text-center text-muted-foreground text-sm py-8">暂无菜单</div>
        <MenuTreeItem
          v-for="item in menus"
          :key="item.id"
          :item="item"
          :selected-id="selectedItem?.id ?? null"
          @select="selectedItem = $event"
          @create-child="openCreate($event)"
        />
      </div>
    </div>

    <!-- 右侧详情 -->
    <div class="flex-1 flex flex-col border rounded-lg bg-background overflow-hidden">
      <div v-if="!selectedItem" class="flex-1 flex items-center justify-center text-muted-foreground">
        请从左侧选择菜单项
      </div>
      <template v-else>
        <div class="px-6 py-4 border-b flex items-center justify-between flex-shrink-0">
          <div>
            <h2 class="text-lg font-semibold">{{ selectedItem.name }}</h2>
            <p class="text-sm text-muted-foreground mt-1 font-mono">{{ selectedItem.path }}</p>
          </div>
          <div class="flex gap-2">
            <Button size="sm" @click="openCreate(selectedItem.id)">新建子菜单</Button>
            <Button size="sm" @click="openEdit(selectedItem)">编辑</Button>
            <Button size="sm" variant="destructive" @click="remove(selectedItem)">删除</Button>
          </div>
        </div>
        <div class="flex-1 overflow-y-auto p-6">
          <div class="space-y-5 max-w-2xl">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="text-sm font-medium text-muted-foreground">名称</label>
                <p class="mt-1">{{ selectedItem.name }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-muted-foreground">排序</label>
                <p class="mt-1">{{ selectedItem.sort }}</p>
              </div>
            </div>
            <div>
              <label class="text-sm font-medium text-muted-foreground">路径</label>
              <p class="mt-1 font-mono text-sm">{{ selectedItem.path }}</p>
            </div>
            <div v-if="selectedItem.icon">
              <label class="text-sm font-medium text-muted-foreground">图标</label>
              <p class="mt-1">{{ selectedItem.icon }}</p>
            </div>
            <div v-if="getApiLabel(selectedItem.api_id)">
              <label class="text-sm font-medium text-muted-foreground">关联 API</label>
              <p class="mt-1 font-mono text-sm bg-muted px-2 py-1 rounded inline-block">{{ getApiLabel(selectedItem.api_id) }}</p>
            </div>
            <div v-if="selectedItem.permission_ids?.length">
              <label class="text-sm font-medium text-muted-foreground">关联权限</label>
              <div class="mt-2 flex flex-wrap gap-1">
                <Badge v-for="name in getPermissionNames(selectedItem.permission_ids)" :key="name" variant="secondary">
                  {{ name }}
                </Badge>
              </div>
            </div>
            <div v-if="selectedItem.children?.length">
              <label class="text-sm font-medium text-muted-foreground">子菜单</label>
              <div class="mt-2 space-y-1">
                <div
                  v-for="child in selectedItem.children" :key="child.id"
                  class="px-3 py-2 rounded bg-muted/50 hover:bg-muted cursor-pointer transition-colors"
                  @click="selectedItem = child"
                >
                  <div class="font-medium text-sm">{{ child.name }}</div>
                  <div class="text-xs text-muted-foreground font-mono">{{ child.path }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>

  <!-- 编辑对话框 -->
  <Dialog :open="dialogOpen" :title="isEdit ? '编辑菜单' : '新建菜单'" :loading="submitting"
    @update:open="dialogOpen = $event" @confirm="submit">
    <div class="space-y-3">
      <div class="space-y-1">
        <label class="text-sm font-medium">父级菜单</label>
        <Select :model-value="form.parent_id ?? ''" :options="parentOptions"
          @update:model-value="form.parent_id = $event === '' ? null : Number($event)" />
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium">名称 *</label>
        <Input v-model="form.name" placeholder="如：系统管理" />
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium">路径 *</label>
        <Input v-model="form.path" placeholder="如：/sys/user" class="font-mono" />
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div class="space-y-1">
          <label class="text-sm font-medium">图标</label>
          <Input v-model="form.icon" placeholder="图标名称" />
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">排序</label>
          <Input v-model.number="form.sort" type="number" />
        </div>
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium">关联 API</label>
        <Select :model-value="form.api_id ?? ''" :options="apiOptions"
          @update:model-value="form.api_id = $event === '' ? null : Number($event)" />
      </div>
      <div class="space-y-1.5">
        <label class="text-sm font-medium">关联权限</label>
        <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
          <button
            v-for="perm in permissions" :key="perm.id"
            class="px-2.5 py-1 rounded-md text-xs border transition-colors"
            :class="form.permission_ids.includes(perm.id)
              ? 'bg-primary text-primary-foreground border-primary'
              : 'bg-background border-input hover:bg-muted'"
            @click="togglePermission(perm.id)"
          >{{ perm.name }}</button>
        </div>
      </div>
    </div>
  </Dialog>
</template>
