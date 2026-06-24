<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { dictApi, type Dict } from '@/api/sys/dict'
import DictTreeItem from '@/components/DictTreeItem.vue'
import Button from '@/components/ui/Button.vue'
import Dialog from '@/components/ui/Dialog.vue'
import Input from '@/components/ui/Input.vue'
import Select from '@/components/ui/Select.vue'

const dicts = ref<Dict[]>([])
const allDicts = ref<Dict[]>([])
const selectedItem = ref<Dict | null>(null)
const loading = ref(false)
const submitting = ref(false)
const dialogOpen = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)

const form = ref<{parent_id: number | null; name: string; code: string; type: string; value: string; sort: number; description: string}>({
  parent_id: null, name: '', code: '', type: 'string', value: '', sort: 0, description: ''
})

const flatDicts = computed(() => {
  const flat: Dict[] = []
  const traverse = (items: Dict[]) => {
    items.forEach(item => {
      flat.push(item)
      if (item.children?.length) traverse(item.children)
    })
  }
  traverse(dicts.value)
  return flat
})

const parentOptions = computed(() => [
  { label: '无（根级）', value: '' },
  ...flatDicts.value.filter(d => d.id !== selectedItem.value?.id).map(d => ({ label: d.name, value: d.id }))
])

async function load() {
  loading.value = true
  try {
    const res = await dictApi.list()
    dicts.value = res.items
    allDicts.value = await dictApi.listFlat()
    if (dicts.value.length > 0) {
      selectItem(dicts.value[0])
    }
  } finally {
    loading.value = false
  }
}

function selectItem(item: Dict) {
  selectedItem.value = item
}

function openCreate(parentId?: number) {
  isEdit.value = false
  editId.value = null
  form.value = { parent_id: parentId ?? null, name: '', code: '', type: 'string', value: '', sort: 0, description: '' }
  dialogOpen.value = true
}

function openEdit() {
  if (!selectedItem.value) return
  isEdit.value = true
  editId.value = selectedItem.value.id
  form.value = {
    parent_id: selectedItem.value.parent_id,
    name: selectedItem.value.name,
    code: selectedItem.value.code,
    type: selectedItem.value.type,
    value: selectedItem.value.value,
    sort: selectedItem.value.sort,
    description: selectedItem.value.description ?? ''
  }
  dialogOpen.value = true
}

async function submit() {
  submitting.value = true
  try {
    if (isEdit.value && editId.value) {
      await dictApi.update(editId.value, {
        name: form.value.name,
        value: form.value.value,
        type: form.value.type,
        parent_id: form.value.parent_id,
        sort: form.value.sort,
        description: form.value.description
      })
    } else {
      await dictApi.create(form.value)
    }
    dialogOpen.value = false
    await load()
  } finally {
    submitting.value = false
  }
}

async function remove() {
  if (!selectedItem.value) return
  if (!confirm(`确定删除「${selectedItem.value.name}」？`)) return
  await dictApi.remove(selectedItem.value.id)
  selectedItem.value = null
  await load()
}

onMounted(load)
</script>

<template>
  <div class="flex h-[calc(100vh-120px)] gap-4">
    <!-- 左侧树形菜单 -->
    <div class="w-72 flex flex-col border rounded-lg bg-muted/30">
      <div class="px-4 py-3 border-b flex items-center justify-between flex-shrink-0">
        <h3 class="font-medium text-sm">字典树</h3>
        <Button size="sm" @click="openCreate()">新建</Button>
      </div>
      <div v-if="loading" class="flex-1 flex items-center justify-center text-muted-foreground text-sm">
        加载中...
      </div>
      <div v-else class="flex-1 overflow-y-auto p-2">
        <div v-if="dicts.length === 0" class="text-center text-muted-foreground text-sm py-8">
          暂无数据
        </div>
        <div v-else class="space-y-1">
          <DictTreeItem
            v-for="item in dicts"
            :key="item.id"
            :item="item"
            :selected-id="selectedItem?.id ?? null"
            @select="selectItem"
            @create-child="openCreate"
          />
        </div>
      </div>
    </div>

    <!-- 右侧详情面板 -->
    <div class="flex-1 flex flex-col border rounded-lg bg-background overflow-hidden">
      <div v-if="!selectedItem" class="flex-1 flex items-center justify-center text-muted-foreground">
        请从左侧选择字典项
      </div>
      <template v-else>
        <div class="px-6 py-4 border-b flex items-center justify-between flex-shrink-0">
          <div>
            <h2 class="text-lg font-semibold">{{ selectedItem.name }}</h2>
            <p class="text-sm text-muted-foreground mt-1">
              编码：<code class="bg-muted px-2 py-1 rounded text-xs">{{ selectedItem.code }}</code>
            </p>
          </div>
          <div class="flex gap-2">
            <Button size="sm" @click="openCreate(selectedItem.id)">新建子项</Button>
            <Button size="sm" @click="openEdit">编辑</Button>
            <Button size="sm" variant="destructive" @click="remove">删除</Button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div class="space-y-6 max-w-2xl">
            <div>
              <label class="text-sm font-medium text-muted-foreground">名称</label>
              <p class="mt-1 text-base">{{ selectedItem.name }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-muted-foreground">编码</label>
              <p class="mt-1 text-base">{{ selectedItem.code }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-muted-foreground">类型</label>
              <p class="mt-1 text-base">{{ selectedItem.type }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-muted-foreground">值</label>
              <p class="mt-1 text-base">{{ selectedItem.value }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-muted-foreground">排序</label>
              <p class="mt-1 text-base">{{ selectedItem.sort }}</p>
            </div>
            <div v-if="selectedItem.description">
              <label class="text-sm font-medium text-muted-foreground">描述</label>
              <p class="mt-1 text-base">{{ selectedItem.description }}</p>
            </div>
            <div v-if="selectedItem.children?.length">
              <label class="text-sm font-medium text-muted-foreground">子项</label>
              <div class="mt-2 space-y-1">
                <div
                  v-for="child in selectedItem.children"
                  :key="child.id"
                  class="px-3 py-2 rounded bg-muted/50 hover:bg-muted cursor-pointer transition-colors"
                  @click="selectItem(child)"
                >
                  <div class="font-medium text-sm">{{ child.name }}</div>
                  <div class="text-xs text-muted-foreground">{{ child.code }} = {{ child.value }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>

  <!-- 编辑对话框 -->
  <Dialog :open="dialogOpen" :title="isEdit ? '编辑字典' : '新建字典'" :loading="submitting"
    @update:open="dialogOpen = $event" @confirm="submit">
    <div class="space-y-3">
      <div class="space-y-1">
        <label class="text-sm font-medium">父级</label>
        <Select :model-value="form.parent_id ?? ''" :options="parentOptions" placeholder="请选择"
          @update:model-value="form.parent_id = $event === '' ? null : Number($event)" />
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium">名称 *</label>
        <Input v-model="form.name" placeholder="如：性别" />
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium">编码 *</label>
        <Input v-model="form.code" placeholder="如：gender" :disabled="isEdit" />
      </div>
      <div class="space-y-1">
          <label class="text-sm font-medium">类型</label>
          <Select :model-value="form.type" :options="[{label: 'String', value: 'string'}, {label: 'Number', value: 'number'}, {label: 'Boolean', value: 'boolean'}, {label: 'JSON', value: 'json'}, {label: 'Textarea', value: 'textarea'}]" placeholder="请选择"
          @update:model-value="form.type = String($event)" />
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium">值 *</label>
        <!-- String input -->
        <Input v-if="form.type === 'string'" v-model="form.value" placeholder="输入字符串值" />
        <!-- Number input -->
        <Input v-else-if="form.type === 'number'" v-model="form.value" type="number" placeholder="输入数字值" />
        <!-- Boolean switch -->
        <div v-else-if="form.type === 'boolean'" class="flex items-center gap-2">
          <input
            type="checkbox"
            :checked="form.value === 'true'"
            @change="form.value = ($event.target as HTMLInputElement).checked ? 'true' : 'false'"
            class="rounded border-gray-300"
          />
          <span class="text-sm">{{ form.value === 'true' ? '是' : '否' }}</span>
        </div>
        <!-- Textarea -->
        <textarea
          v-else-if="form.type === 'textarea'"
          v-model="form.value"
          placeholder="输入多行内容"
          rows="4"
          class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <!-- JSON input -->
        <textarea
          v-else-if="form.type === 'json'"
          v-model="form.value"
          placeholder="输入 JSON 格式数据"
          rows="4"
          class="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary font-mono text-xs"
        />
      </div>
        <div class="space-y-1">
          <label class="text-sm font-medium">排序</label>
          <Input v-model="form.sort" type="number" placeholder="数字越小越靠前" />
        </div>
      <div class="space-y-1">
        <label class="text-sm font-medium">描述</label>
        <Input v-model="form.description" placeholder="可选" />
      </div>
    </div>
  </Dialog>
</template>
