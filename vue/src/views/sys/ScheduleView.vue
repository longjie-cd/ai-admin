<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { scheduleApi, type Schedule, type ScheduleCreate } from '@/api/sys/schedule'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Dialog from '@/components/ui/Dialog.vue'

const schedules = ref<Schedule[]>([])
const showCreate = ref(false)
const viewMode = ref<'calendar' | 'list'>('calendar')
const calendarCursor = ref(new Date())
const selectedSchedule = ref<Schedule | null>(null)

const form = ref<ScheduleCreate>({
  title: '',
  description: '',
  start_time: '',
  end_time: '',
  all_day: false,
  color: '#6366F1',
})

const upcoming = computed(() =>
  [...schedules.value].sort((a: Schedule, b: Schedule) => a.start_time.localeCompare(b.start_time)),
)

const monthLabel = computed(() =>
  calendarCursor.value.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' }),
)

const calendarDays = computed(() => {
  const year = calendarCursor.value.getFullYear()
  const month = calendarCursor.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const startWeekday = firstDay.getDay()
  const startDate = new Date(firstDay)
  startDate.setDate(firstDay.getDate() - startWeekday)

  return Array.from({ length: 42 }, (_, index) => {
    const date = new Date(startDate)
    date.setDate(startDate.getDate() + index)
    const key = date.toISOString().slice(0, 10)
    const items = upcoming.value.filter(item => item.start_time.slice(0, 10) === key)
    return {
      key,
      date,
      items,
      isCurrentMonth: date.getMonth() === month,
      isToday: key === new Date().toISOString().slice(0, 10),
    }
  })
})

async function load() {
  schedules.value = (await scheduleApi.list()).items
}

function resetForm() {
  const today = new Date().toISOString().slice(0, 16)
  form.value = {
    title: '',
    description: '',
    start_time: today,
    end_time: today,
    all_day: false,
    color: '#6366F1',
  }
}

async function create() {
  if (!form.value.title.trim() || !form.value.start_time || !form.value.end_time) return
  await scheduleApi.create(form.value)
  showCreate.value = false
  resetForm()
  await load()
}

async function remove(id: number) {
  await scheduleApi.remove(id)
  schedules.value = schedules.value.filter(item => item.id !== id)
}

function formatTime(value: string) {
  return value.replace('T', ' ')
}

function shiftMonth(step: number) {
  const next = new Date(calendarCursor.value)
  next.setMonth(next.getMonth() + step)
  calendarCursor.value = next
}

function closeCreate() {
  showCreate.value = false
}

function openScheduleDetail(item: Schedule) {
  selectedSchedule.value = item
}

function closeScheduleDetail() {
  selectedSchedule.value = null
}

onMounted(async () => {
  resetForm()
  await load()
})
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold">日程管理</h1>
        <p class="text-sm mt-0.5" style="color: hsl(var(--text-2))">共 {{ schedules.length }} 条日程</p>
      </div>
      <div class="flex gap-2">
        <div class="flex gap-1 p-1 rounded-xl" style="background: hsl(var(--bg-sunken));">
          <button
            v-for="mode in [['calendar', '日历'], ['list', '列表']]"
            :key="mode[0]"
            class="px-3 py-1.5 rounded-lg text-sm transition-colors"
            :style="viewMode === mode[0]
              ? 'background: hsl(var(--bg-surface)); color: hsl(var(--text-1)); box-shadow: var(--shadow-xs);'
              : 'color: hsl(var(--text-2));'"
            @click="viewMode = mode[0] as 'calendar' | 'list'"
          >
            {{ mode[1] }}
          </button>
        </div>
        <Button size="sm" @click="showCreate = true">+ 新建日程</Button>
      </div>
    </div>

    <div v-if="viewMode === 'calendar'" class="rounded-2xl border overflow-hidden p-5" style="background: hsl(var(--card)); border-color: hsl(var(--border-subtle))">
      <div class="flex items-center justify-between mb-4">
        <Button variant="outline" size="sm" @click="shiftMonth(-1)">上月</Button>
        <h2 class="text-base font-semibold">{{ monthLabel }}</h2>
        <Button variant="outline" size="sm" @click="shiftMonth(1)">下月</Button>
      </div>
      <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_320px] gap-4">
        <div>
          <div class="grid grid-cols-7 gap-2 text-center text-xs font-medium mb-2" style="color: hsl(var(--text-3));">
            <div v-for="week in ['日', '一', '二', '三', '四', '五', '六']" :key="week">{{ week }}</div>
          </div>
          <div class="grid grid-cols-7 gap-2">
            <div
              v-for="day in calendarDays"
              :key="day.key"
              class="min-h-[120px] rounded-2xl border p-2.5"
              :style="[
                `border-color: hsl(var(--border-subtle));`,
                day.isCurrentMonth ? 'background: hsl(var(--bg-surface));' : 'background: hsl(var(--bg-sunken)); opacity: 0.65;',
              ]"
            >
              <div class="flex items-center justify-between mb-2">
                <span
                  class="text-sm font-medium w-7 h-7 rounded-full flex items-center justify-center"
                  :style="day.isToday ? 'background: hsl(var(--primary)); color: white;' : 'color: hsl(var(--text-1));'"
                >
                  {{ day.date.getDate() }}
                </span>
                <span v-if="day.items.length" class="text-[11px]" style="color: hsl(var(--text-3));">{{ day.items.length }}项</span>
              </div>
              <div class="space-y-1.5">
                <button
                  v-for="item in day.items.slice(0, 3)"
                  :key="item.id"
                  class="w-full rounded-lg px-2 py-1 text-[11px] truncate text-left transition-transform hover:-translate-y-0.5"
                  :style="{ background: `${item.color}1A`, color: item.color }"
                  @click="openScheduleDetail(item)"
                >
                  {{ item.start_time.slice(11, 16) }} {{ item.title }}
                </button>
                <div v-if="day.items.length > 3" class="text-[11px]" style="color: hsl(var(--text-3));">
                  +{{ day.items.length - 3 }} 更多
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="rounded-2xl border p-4 h-fit sticky top-4" style="background: hsl(var(--bg-surface)); border-color: hsl(var(--border-subtle));">
          <div v-if="selectedSchedule">
            <div class="flex items-start justify-between gap-3 mb-4">
              <div class="min-w-0">
                <p class="text-xs font-medium mb-2" :style="{ color: selectedSchedule.color }">日程详情</p>
                <h3 class="text-base font-semibold">{{ selectedSchedule.title }}</h3>
              </div>
              <button class="w-7 h-7 rounded-lg flex items-center justify-center" style="color: hsl(var(--text-3));" @click="closeScheduleDetail">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
            <div class="space-y-3 text-sm">
              <div>
                <p class="text-xs mb-1" style="color: hsl(var(--text-3));">时间</p>
                <p>{{ formatTime(selectedSchedule.start_time) }}</p>
                <p class="mt-1">{{ formatTime(selectedSchedule.end_time) }}</p>
              </div>
              <div v-if="selectedSchedule.description">
                <p class="text-xs mb-1" style="color: hsl(var(--text-3));">说明</p>
                <p style="color: hsl(var(--text-2));">{{ selectedSchedule.description }}</p>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-xs" style="color: hsl(var(--text-3));">标记色</span>
                <span class="w-3 h-3 rounded-full" :style="{ background: selectedSchedule.color }" />
                <span v-if="selectedSchedule.all_day" class="text-xs px-2 py-0.5 rounded-full" style="background: hsl(var(--info-bg)); color: hsl(var(--info-text))">全天</span>
              </div>
            </div>
          </div>
          <div v-else class="py-16 text-center text-sm" style="color: hsl(var(--text-3));">
            点击日历中的日程查看详情
          </div>
        </div>
      </div>
    </div>

    <div v-else class="rounded-2xl border overflow-hidden" style="background: hsl(var(--card)); border-color: hsl(var(--border-subtle))">
      <div v-if="upcoming.length === 0" class="p-12 text-center" style="color: hsl(var(--text-3))">暂无日程</div>
      <div v-else>
        <div
          v-for="(item, i) in upcoming"
          :key="item.id"
          class="flex items-start gap-4 px-5 py-4"
          :style="i > 0 ? 'border-top: 1px solid hsl(var(--border-subtle))' : ''"
        >
          <div class="w-3 h-12 rounded-full flex-shrink-0 mt-0.5" :style="{ background: item.color }" />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2">
              <span class="text-sm font-semibold">{{ item.title }}</span>
              <span v-if="item.all_day" class="text-xs px-2 py-0.5 rounded-full" style="background: hsl(var(--info-bg)); color: hsl(var(--info-text))">全天</span>
            </div>
            <p v-if="item.description" class="text-sm mt-1" style="color: hsl(var(--text-2))">{{ item.description }}</p>
            <p class="text-xs mt-2" style="color: hsl(var(--text-3))">
              {{ formatTime(item.start_time) }} 至 {{ formatTime(item.end_time) }}
            </p>
          </div>
          <button class="w-7 h-7 rounded-lg flex items-center justify-center transition-colors"
            style="color: hsl(var(--text-3))"
            @click="remove(item.id)">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <Dialog :open="showCreate" title="新建日程" @close="closeCreate" @confirm="create">
      <div class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium">标题</label>
          <Input v-model="form.title" placeholder="日程标题" />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">描述</label>
          <Input v-model="form.description" placeholder="补充说明" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-1.5">
            <label class="text-sm font-medium">开始时间</label>
            <Input v-model="form.start_time" type="datetime-local" />
          </div>
          <div class="space-y-1.5">
            <label class="text-sm font-medium">结束时间</label>
            <Input v-model="form.end_time" type="datetime-local" />
          </div>
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium">颜色</label>
          <input v-model="form.color" type="color" class="h-10 w-20 rounded-lg border" style="border-color: hsl(var(--border-default)); background: transparent;" />
        </div>
      </div>
    </Dialog>
  </div>
</template>
