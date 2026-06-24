<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { profileApi } from '@/api/sys/profile'
import { userApi } from '@/api/sys/user'
import { teamApi } from '@/api/sys/team'
import { roleApi } from '@/api/sys/role'
import { permissionApi } from '@/api/sys/permission'
import { todoApi, type Todo } from '@/api/sys/todo'
import { scheduleApi, type Schedule } from '@/api/sys/schedule'
import type { User } from '@/api/sys/user'

const router = useRouter()
const themeStore = useThemeStore()
const currentUser = ref<User | null>(null)
const todos = ref<Todo[]>([])
const schedules = ref<Schedule[]>([])

const stats = ref({ users: 0, teams: 0, roles: 0, permissions: 0 })

const now = ref(new Date())
let timer: ReturnType<typeof setInterval>

onMounted(async () => {
  timer = setInterval(() => { now.value = new Date() }, 1000)

  try {
    currentUser.value = await profileApi.getProfile()
  } catch { /* ignore */ }

  try {
    const [u, t, r, p] = await Promise.all([
      userApi.list(), teamApi.list(), roleApi.list(), permissionApi.list(),
    ])
    stats.value = {
      users: u.items.length,
      teams: t.items.length,
      roles: r.items.length,
      permissions: p.items.length,
    }
  } catch { /* ignore */ }

  try {
    const [todoRes, scheduleRes] = await Promise.all([
      todoApi.list(),
      scheduleApi.list(),
    ])
    todos.value = todoRes.items
    schedules.value = scheduleRes.items
  } catch { /* ignore */ }
})

onUnmounted(() => clearInterval(timer))

const timeStr = () => now.value.toLocaleTimeString('zh-CN', { hour12: false })
const dateStr = () => now.value.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })

const greeting = () => {
  const h = now.value.getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
}

const modules = [
  {
    name: '消息管理',
    desc: '查看和处理个人系统消息',
    path: '/sys/message',
    gradient: 'from-sky-500 to-blue-600',
    icon: 'message',
  },
  {
    name: '待办管理',
    desc: '跟踪任务进度与优先级',
    path: '/sys/todo',
    gradient: 'from-amber-500 to-orange-500',
    icon: 'todo',
  },
  {
    name: '日程管理',
    desc: '维护个人时间安排与提醒',
    path: '/sys/schedule',
    gradient: 'from-emerald-500 to-lime-500',
    icon: 'schedule',
  },
  {
    name: '用户管理',
    desc: '账号创建与权限分配',
    path: '/sys/user',
    gradient: 'from-violet-500 to-purple-600',
    icon: 'user',
  },
  {
    name: '团队管理',
    desc: '部门组织与成员协作',
    path: '/sys/team',
    gradient: 'from-blue-500 to-cyan-500',
    icon: 'team',
  },
  {
    name: '角色管理',
    desc: '角色定义与权限绑定',
    path: '/sys/role',
    gradient: 'from-emerald-500 to-teal-500',
    icon: 'role',
  },
  {
    name: '权限管理',
    desc: '细粒度接口访问控制',
    path: '/sys/permission',
    gradient: 'from-orange-500 to-amber-500',
    icon: 'permission',
  },
  {
    name: '数据字典',
    desc: '系统枚举值统一管理',
    path: '/sys/dict',
    gradient: 'from-pink-500 to-rose-500',
    icon: 'dict',
  },
  {
    name: 'API 管理',
    desc: '接口注册与文档维护',
    path: '/sys/api',
    gradient: 'from-indigo-500 to-blue-600',
    icon: 'api',
  },
  {
    name: '菜单管理',
    desc: '导航结构与路由配置',
    path: '/sys/menu',
    gradient: 'from-fuchsia-500 to-violet-600',
    icon: 'menu',
  },
]

const quickStats = [
  { label: '系统用户', key: 'users' as const },
  { label: '团队部门', key: 'teams' as const },
  { label: '系统角色', key: 'roles' as const },
  { label: '权限条目', key: 'permissions' as const },
]

const pendingTodos = computed(() => todos.value.filter((item: Todo) => item.status !== 'done').slice(0, 5))
const upcomingSchedules = computed(() =>
  [...schedules.value].sort((a: Schedule, b: Schedule) => a.start_time.localeCompare(b.start_time)).slice(0, 5),
)

const heroStyle = computed(() => ({
  background: `
    radial-gradient(circle at top right, hsl(var(--primary) / 0.16), transparent 30%),
    radial-gradient(circle at left 20%, hsl(var(--primary) / 0.08), transparent 28%),
    linear-gradient(180deg, hsl(var(--card)) 0%, hsl(var(--bg-surface)) 100%)
  `,
  minHeight: '168px',
  border: '1px solid hsl(var(--border-subtle))',
  boxShadow: 'var(--shadow-sm)',
}))

const heroOrbStyles = [
  'background: radial-gradient(circle, hsl(var(--primary) / 0.22), transparent 72%);',
  'background: radial-gradient(circle, hsl(var(--primary) / 0.14), transparent 72%);',
  'background: radial-gradient(circle, hsl(var(--primary) / 0.1), transparent 72%);',
]

const statAccentStyles = [
  { color: 'hsl(var(--primary))', bg: 'hsl(var(--primary) / 0.12)' },
  { color: 'hsl(var(--primary) / 0.86)', bg: 'hsl(var(--primary) / 0.10)' },
  { color: 'hsl(var(--primary) / 0.72)', bg: 'hsl(var(--primary) / 0.08)' },
  { color: 'hsl(var(--primary) / 0.6)', bg: 'hsl(var(--primary) / 0.06)' },
]

const moduleStyle = computed(() => ({
  background: themeStore.current().gradient,
}))

const heroChipStyle = computed(() => ({
  background: 'hsl(var(--primary) / 0.08)',
  color: 'hsl(var(--primary))',
  border: '1px solid hsl(var(--primary) / 0.14)',
}))

function goToTodos() {
  router.push('/sys/todo')
}

function goToSchedules() {
  router.push('/sys/schedule')
}
</script>

<template>
  <div class="space-y-6">

    <!-- Welcome Banner -->
    <div class="relative rounded-2xl overflow-hidden" :style="heroStyle">
      <!-- decorative blobs -->
      <div class="absolute -top-8 -right-8 w-48 h-48 rounded-full opacity-30"
        :style="heroOrbStyles[0]"/>
      <div class="absolute top-4 right-24 w-24 h-24 rounded-full opacity-20"
        :style="heroOrbStyles[1]"/>
      <div class="absolute -bottom-4 left-32 w-32 h-32 rounded-full opacity-20"
        :style="heroOrbStyles[2]"/>

      <div class="relative flex items-center justify-between p-8">
        <div class="max-w-2xl">
          <div class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium mb-4" :style="heroChipStyle">
            <span class="w-2 h-2 rounded-full" style="background: hsl(var(--primary));" />
            控制台总览
          </div>
          <p class="text-sm mb-1" style="color: hsl(var(--text-2));">
            {{ greeting() }}，{{ currentUser?.nickname ?? currentUser?.username ?? '管理员' }}
          </p>
          <h1 class="text-3xl font-bold mb-2" style="color: hsl(var(--text-1));">企业级 AI 管理系统</h1>
          <p class="text-sm leading-6" style="color: hsl(var(--text-2));">
            统一管理用户、团队、角色、权限、菜单与 API 接口
          </p>
        </div>

        <!-- Clock -->
        <div class="text-right flex-shrink-0">
          <div class="text-4xl font-bold tabular-nums" style="color: hsl(var(--text-1));">{{ timeStr() }}</div>
          <div class="text-xs mt-1" style="color: hsl(var(--text-3));">{{ dateStr() }}</div>
        </div>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div
        v-for="(s, index) in quickStats"
        :key="s.key"
        class="stat-card rounded-2xl p-5 border border-border"
        style="background: hsl(var(--card))"
      >
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-muted-foreground">{{ s.label }}</span>
          <div class="w-8 h-8 rounded-lg flex items-center justify-center"
            :style="{ background: statAccentStyles[index]?.bg }">
            <div class="w-3 h-3 rounded-full" :style="{ background: statAccentStyles[index]?.color }"/>
          </div>
        </div>
        <div class="text-3xl font-bold tabular-nums" :style="{ color: statAccentStyles[index]?.color }">
          {{ stats[s.key] }}
        </div>
      </div>
    </div>

    <!-- Modules Grid -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-base font-semibold">功能模块</h2>
        <span class="text-xs text-muted-foreground">共 {{ modules.length }} 个模块</span>
      </div>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        <button
          v-for="m in modules"
          :key="m.path"
          class="group relative rounded-2xl p-5 text-left border border-border stat-card overflow-hidden"
          style="background: hsl(var(--card))"
          @click="router.push(m.path)"
        >
          <!-- icon -->
          <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white mb-4"
            :style="moduleStyle">
            <svg v-if="m.icon === 'user'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            <svg v-else-if="m.icon === 'team'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            <svg v-else-if="m.icon === 'role'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
            <svg v-else-if="m.icon === 'permission'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"/>
            </svg>
            <svg v-else-if="m.icon === 'dict'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
            </svg>
            <svg v-else-if="m.icon === 'api'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
            </svg>
            <svg v-else-if="m.icon === 'menu'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/>
            </svg>
            <svg v-else-if="m.icon === 'message'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
            </svg>
            <svg v-else-if="m.icon === 'todo'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V9m-9 4l2 2 4-4m-4-6h4"/>
            </svg>
            <svg v-else-if="m.icon === 'schedule'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10m-11 9h12a2 2 0 002-2V7a2 2 0 00-2-2H6a2 2 0 00-2 2v11a2 2 0 002 2z"/>
            </svg>
          </div>

          <div class="font-semibold text-sm mb-1">{{ m.name }}</div>
          <div class="text-xs text-muted-foreground leading-relaxed">{{ m.desc }}</div>

          <!-- arrow -->
          <div class="absolute top-4 right-4 w-6 h-6 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
            style="background: hsl(var(--muted));">
            <svg class="w-3.5 h-3.5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </div>
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <div class="rounded-2xl border border-border p-6" style="background: hsl(var(--card))">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-base font-semibold">我的待办</h2>
            <p class="text-xs mt-1 text-muted-foreground">优先展示未完成事项</p>
          </div>
          <button class="text-sm font-medium" style="color: hsl(var(--primary));" @click="goToTodos">查看全部</button>
        </div>
        <div v-if="pendingTodos.length === 0" class="py-10 text-center text-sm text-muted-foreground">暂无待办</div>
        <div v-else class="space-y-3">
          <button
            v-for="todo in pendingTodos"
            :key="todo.id"
            class="w-full rounded-xl border px-4 py-3 text-left hover:bg-muted/40 transition-colors"
            style="border-color: hsl(var(--border-subtle));"
            @click="goToTodos"
          >
            <div class="flex items-center justify-between gap-3">
              <span class="text-sm font-medium">{{ todo.title }}</span>
              <span class="text-xs px-2 py-0.5 rounded-full"
                :style="todo.priority === 'high'
                  ? 'background: rgba(239,68,68,0.1); color: #EF4444;'
                  : todo.priority === 'medium'
                    ? 'background: rgba(245,158,11,0.1); color: #F59E0B;'
                    : 'background: rgba(107,114,128,0.1); color: #6B7280;'">
                {{ todo.priority }}
              </span>
            </div>
            <p class="text-xs mt-2" style="color: hsl(var(--text-3));">
              {{ todo.due_date ? `截止 ${todo.due_date}` : '未设置截止日期' }}
            </p>
          </button>
        </div>
      </div>

      <div class="rounded-2xl border border-border p-6" style="background: hsl(var(--card))">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h2 class="text-base font-semibold">近期日程</h2>
            <p class="text-xs mt-1 text-muted-foreground">同步当前登录人的安排</p>
          </div>
          <button class="text-sm font-medium" style="color: hsl(var(--primary));" @click="goToSchedules">查看全部</button>
        </div>
        <div v-if="upcomingSchedules.length === 0" class="py-10 text-center text-sm text-muted-foreground">暂无日程</div>
        <div v-else class="space-y-3">
          <button
            v-for="item in upcomingSchedules"
            :key="item.id"
            class="w-full rounded-xl border px-4 py-3 text-left hover:bg-muted/40 transition-colors"
            style="border-color: hsl(var(--border-subtle));"
            @click="goToSchedules"
          >
            <div class="flex items-center gap-3">
              <span class="w-2.5 h-10 rounded-full flex-shrink-0" :style="{ background: item.color }" />
              <div class="min-w-0 flex-1">
                <div class="text-sm font-medium truncate">{{ item.title }}</div>
                <p class="text-xs mt-1" style="color: hsl(var(--text-3));">
                  {{ item.start_time.replace('T', ' ') }} - {{ item.end_time.replace('T', ' ') }}
                </p>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- System Info -->
    <div class="rounded-2xl border border-border p-6" style="background: hsl(var(--card))">
      <h2 class="text-base font-semibold mb-4">系统信息</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <p class="text-xs text-muted-foreground mb-1">当前用户</p>
          <p class="text-sm font-medium">{{ currentUser?.username ?? '-' }}</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground mb-1">邮箱</p>
          <p class="text-sm font-medium">{{ currentUser?.email ?? '-' }}</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground mb-1">后端框架</p>
          <p class="text-sm font-medium">FastAPI · Python 3.10</p>
        </div>
        <div>
          <p class="text-xs text-muted-foreground mb-1">前端框架</p>
          <p class="text-sm font-medium">Vue 3 · TypeScript · Tailwind</p>
        </div>
      </div>
    </div>

  </div>
</template>
