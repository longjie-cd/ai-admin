<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { todoApi, type Todo, type TodoCreate } from '@/api/sys/todo'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Dialog from '@/components/ui/Dialog.vue'

const todos = ref<Todo[]>([])
const showCreate = ref(false)
const filter = ref<'all' | 'pending' | 'in_progress' | 'done'>('all')

const form = ref<TodoCreate>({ title: '', status: 'pending', priority: 'medium' })

const filtered = computed(() => {
  if (filter.value === 'all') return todos.value
  return todos.value.filter(t => t.status === filter.value)
})

const priorityConf: Record<string, { label: string; color: string; bg: string }> = {
  high:   { label: '高', color: '#EF4444', bg: 'rgba(239,68,68,0.1)' },
  medium: { label: '中', color: '#F59E0B', bg: 'rgba(245,158,11,0.1)' },
  low:    { label: '低', color: '#6B7280', bg: 'rgba(107,114,128,0.1)' },
}
const statusConf: Record<string, { label: string; color: string }> = {
  pending:     { label: '待处理', color: '#6B7280' },
  in_progress: { label: '进行中', color: '#3B82F6' },
  done:        { label: '已完成', color: '#10B981' },
}

async function load() {
  todos.value = (await todoApi.list()).items
}

async function create() {
  if (!form.value.title.trim()) return
  await todoApi.create(form.value)
  showCreate.value = false
  form.value = { title: '', status: 'pending', priority: 'medium' }
  await load()
}

async function toggleDone(todo: Todo) {
  const newStatus = todo.status === 'done' ? 'pending' : 'done'
  await todoApi.update(todo.id, { status: newStatus })
  todo.status = newStatus
}

async function remove(id: number) {
  await todoApi.remove(id)
  todos.value = todos.value.filter(t => t.id !== id)
}

onMounted(load)
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">待办管理</h1>
        <p class="text-sm mt-0.5" style="color: hsl(var(--text-2))">共 {{ todos.length }} 条待办</p>
      </div>
      <Button size="sm" @click="showCreate = true">+ 新建待办</Button>
    </div>

    <!-- Filter -->
    <div class="flex gap-1 p-1 rounded-xl" style="background: hsl(var(--bg-sunken)); width: fit-content">
      <button v-for="[v,l] in [['all','全部'],['pending','待处理'],['in_progress','进行中'],['done','已完成']]" :key="v"
        class="px-4 py-1.5 rounded-lg text-sm font-medium transition-all"
        :style="filter === v
          ? 'background: hsl(var(--bg-surface)); color: hsl(var(--text-1)); box-shadow: var(--shadow-xs)'
          : 'color: hsl(var(--text-2))'"
        @click="filter = v as any">{{ l }}</button>
    </div>

    <!-- List -->
    <div class="rounded-2xl border overflow-hidden" style="background: hsl(var(--card)); border-color: hsl(var(--border-subtle))">
      <div v-if="filtered.length === 0" class="p-12 text-center" style="color: hsl(var(--text-3))">暂无待办</div>
      <div v-else>
        <div v-for="(todo, i) in filtered" :key="todo.id"
          class="flex items-center gap-4 px-5 py-4 transition-colors"
          :style="i > 0 ? 'border-top: 1px solid hsl(var(--border-subtle))' : ''">
          <!-- Checkbox -->
          <button class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all"
            :style="todo.status === 'done'
              ? 'border-color: #10B981; background: #10B981'
              : 'border-color: hsl(var(--border-strong))'"
            @click="toggleDone(todo)">
            <svg v-if="todo.status === 'done'" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
            </svg>
          </button>
          <!-- Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-sm font-medium" :class="todo.status === 'done' ? 'line-through opacity-50' : ''">{{ todo.title }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full font-medium"
                :style="{ background: priorityConf[todo.priority]?.bg, color: priorityConf[todo.priority]?.color }">
                {{ priorityConf[todo.priority]?.label }}优先
              </span>
            </div>
            <div class="flex items-center gap-3 mt-1">
              <span class="text-xs font-medium" :style="{ color: statusConf[todo.status]?.color }">
                {{ statusConf[todo.status]?.label }}
              </span>
              <span v-if="todo.due_date" class="text-xs" style="color: hsl(var(--text-3))">截止 {{ todo.due_date }}</span>
            </div>
          </div>
          <!-- Delete -->
          <button class="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
            style="color: hsl(var(--text-3))"
            @click="remove(todo.id)">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Create Dialog -->
    <Dialog :open="showCreate" title="新建待办" @close="showCreate = false">
      <div class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium">标题</label>
          <Input v-model="form.title" placeholder="待办事项标题" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-1.5">
            <label class="text-sm font-medium">优先级</label>
            <select v-model="form.priority" class="ds-input w-full">
              <option value="low">低</option>
              <option value="medium">中</option>
              <option value="high">高</option>
            </select>
          </div>
          <div class="space-y-1.5">
            <label class="text-sm font-medium">截止日期</label>
            <Input v-model="form.due_date" type="date" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button variant="outline" @click="showCreate = false">取消</Button>
        <Button @click="create">创建</Button>
      </template>
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
