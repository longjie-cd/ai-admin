<script setup lang="ts">
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore, THEMES } from '@/stores/theme'
import { useSystemStore } from '@/stores/system'
import { profileApi } from '@/api/sys/profile'
import { messageApi, type Message } from '@/api/sys/message'
import type { User } from '@/api/sys/user'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const themeStore = useThemeStore()
const systemStore = useSystemStore()
const currentUser = ref<User | null>(null)
const userDropdownOpen = ref(false)
const messageDropdownOpen = ref(false)
const topMessages = ref<Message[]>([])
const unreadCount = ref(0)
let userDropdownTimer: ReturnType<typeof setTimeout> | null = null

// Sidebar collapsed state — persisted in localStorage
const sidebarCollapsed = ref(localStorage.getItem('sidebar-collapsed') === 'true')
watch(sidebarCollapsed, v => localStorage.setItem('sidebar-collapsed', String(v)))

// Tooltip state (fixed-position, rendered via Teleport to avoid overflow clipping)
const tooltip = ref<{ name: string; x: number; y: number } | null>(null)

function showTooltip(e: MouseEvent, name: string) {
  if (!sidebarCollapsed.value) return
  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  tooltip.value = { name, x: rect.right + 12, y: rect.top + rect.height / 2 }
}
function hideTooltip() {
  tooltip.value = null
}

const nav = [
  {
    group: '应用',
    items: [
      { name: '首页 Dashboard', path: '/', icon: 'home', exact: true },
    ],
  },
  {
    group: '系统管理',
    items: [
      { name: '消息管理', path: '/sys/message', icon: 'message' },
      { name: '待办管理', path: '/sys/todo', icon: 'todo' },
      { name: '日程管理', path: '/sys/schedule', icon: 'schedule' },
      { name: '用户管理', path: '/sys/user', icon: 'user' },
      { name: '团队管理', path: '/sys/team', icon: 'team' },
      { name: '角色管理', path: '/sys/role', icon: 'role' },
      { name: '权限管理', path: '/sys/permission', icon: 'permission' },
      { name: '数据字典', path: '/sys/dict', icon: 'dict' },
      { name: 'API 管理', path: '/sys/api', icon: 'api' },
      { name: '菜单管理', path: '/sys/menu', icon: 'menu' },
    ],
  },
]

function isActive(item: { path: string; exact?: boolean }) {
  if (item.exact) return route.path === item.path
  return route.path.startsWith(item.path)
}

const breadcrumb = computed(() => {
  for (const g of nav) {
    const found = g.items.find(i => isActive(i))
    if (found) return { group: g.group, name: found.name }
  }
  return null
})

async function loadCurrentUser() {
  try { currentUser.value = await profileApi.getProfile() } catch { /* ignore */ }
}

async function loadMessages() {
  try {
    unreadCount.value = (await messageApi.unreadCount()).count
    topMessages.value = (await messageApi.list()).items.slice(0, 6)
  } catch {
    unreadCount.value = 0
    topMessages.value = []
  }
}

function openUserDropdown() {
  if (userDropdownTimer) clearTimeout(userDropdownTimer)
  userDropdownOpen.value = true
}

function scheduleCloseUserDropdown() {
  if (userDropdownTimer) clearTimeout(userDropdownTimer)
  userDropdownTimer = setTimeout(() => {
    userDropdownOpen.value = false
  }, 180)
}

async function toggleMessageDropdown() {
  messageDropdownOpen.value = !messageDropdownOpen.value
  if (messageDropdownOpen.value) {
    await loadMessages()
  }
}

async function openMessagesPage() {
  messageDropdownOpen.value = false
  await router.push('/sys/message')
}

async function openMessage(msg: Message) {
  if (!msg.is_read) {
    try {
      await messageApi.update(msg.id, { is_read: true })
      msg.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch {
      // ignore
    }
  }
  await openMessagesPage()
}

function goToProfile() {
  router.push('/profile')
  userDropdownOpen.value = false
}

function logout() {
  auth.logout()
  router.push('/login')
}

const navIcons: Record<string, string> = {
  home: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6',
  user: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  team: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
  role: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z',
  permission: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z',
  dict: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
  api: 'M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z',
  menu: 'M4 6h16M4 12h16M4 18h7',
  message: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9',
  todo: 'M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V9m-9 4l2 2 4-4m-4-6h4',
  schedule: 'M8 7V3m8 4V3m-9 8h10m-11 9h12a2 2 0 002-2V7a2 2 0 00-2-2H6a2 2 0 00-2 2v11a2 2 0 002 2z',
}

onMounted(() => {
  loadCurrentUser()
  loadMessages()
  themeStore.init()
  systemStore.fetchSystemName()
})

onBeforeUnmount(() => {
  if (userDropdownTimer) clearTimeout(userDropdownTimer)
})
</script>

<template>
  <div class="flex h-screen overflow-hidden" style="background: hsl(var(--background))">

    <!-- Sidebar -->
    <aside
      class="flex-shrink-0 flex flex-col transition-all duration-300"
      :style="{
        width: sidebarCollapsed ? '64px' : '220px',
        minWidth: sidebarCollapsed ? '64px' : '220px',
        background: 'var(--sidebar-bg)',
        borderRight: '1px solid var(--sidebar-border)',
        overflow: 'hidden',
      }"
    >
      <!-- Logo -->
      <div
        class="h-14 flex items-center flex-shrink-0"
        :class="sidebarCollapsed ? 'justify-center' : 'px-5 gap-3'"
        style="border-bottom: 1px solid var(--sidebar-border);"
      >
        <div class="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
          :style="{ background: themeStore.current().gradient }">
          <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
        </div>
        <span v-if="!sidebarCollapsed" class="font-bold text-sm tracking-wide whitespace-nowrap" style="color: var(--sidebar-title)">{{ systemStore.systemName }}</span>
      </div>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto overflow-x-hidden py-3"
        :class="sidebarCollapsed ? 'px-2 space-y-0.5' : 'px-3 space-y-5'">
        <div v-for="(group, gi) in nav" :key="group.group" :class="!sidebarCollapsed && 'space-y-0'">
          <p v-if="!sidebarCollapsed"
            class="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-widest whitespace-nowrap"
            style="color: var(--sidebar-group-label)">
            {{ group.group }}
          </p>
          <div v-else-if="gi > 0" class="my-2 border-t" style="border-color: rgba(255,255,255,0.08);"/>

          <div class="space-y-0.5">
            <RouterLink
              v-for="item in group.items"
              :key="item.path"
              :to="item.path"
              class="sidebar-item no-underline"
              :class="[{ active: isActive(item) }, sidebarCollapsed ? 'justify-center !px-0 py-2.5' : '']"
              @mouseenter="showTooltip($event, item.name)"
              @mouseleave="hideTooltip"
            >
              <span class="flex-shrink-0 flex items-center justify-center w-5 h-5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="navIcons[item.icon]"/>
                </svg>
              </span>
              <span v-if="!sidebarCollapsed" class="truncate">{{ item.name }}</span>
            </RouterLink>
          </div>
        </div>
      </nav>

      <!-- Collapse toggle -->
      <div class="flex-shrink-0 p-3" style="border-top: 1px solid var(--sidebar-border);">
        <button
          class="w-full flex items-center rounded-lg py-2 transition-all whitespace-nowrap"
          :class="sidebarCollapsed ? 'justify-center px-0' : 'gap-2.5 px-3'"
          style="color: var(--sidebar-text);"
          @mouseenter="(e) => (e.currentTarget as HTMLElement).style.background = 'var(--sidebar-hover)'"
          @mouseleave="(e) => (e.currentTarget as HTMLElement).style.background = 'transparent'"
          @click="sidebarCollapsed = !sidebarCollapsed; hideTooltip()"
        >
          <svg
            class="w-4 h-4 flex-shrink-0 transition-transform duration-300"
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
            :style="{ transform: sidebarCollapsed ? 'rotate(180deg)' : 'rotate(0deg)' }"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"/>
          </svg>
          <span v-if="!sidebarCollapsed" class="text-xs">收起菜单</span>
        </button>
      </div>
    </aside>

    <!-- Fixed tooltip via Teleport (avoids overflow clipping) -->
    <Teleport to="body">
      <Transition name="tooltip-fade">
        <div
          v-if="tooltip"
          class="fixed z-[9999] pointer-events-none px-2.5 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap"
          style="
            background: #1a1535;
            color: #fff;
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 4px 12px rgba(0,0,0,0.35);
            transform: translateY(-50%);
          "
          :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
        >
          <!-- Arrow -->
          <span
            class="absolute top-1/2 -translate-y-1/2"
            style="right: 100%; border: 5px solid transparent; border-right-color: #1a1535;"
          />
          {{ tooltip.name }}
        </div>
      </Transition>
    </Teleport>

    <!-- Main -->
    <div class="flex-1 flex flex-col overflow-hidden min-w-0">
      <!-- Header -->
      <header class="h-14 flex items-center justify-between px-6 flex-shrink-0"
        style="background: hsl(var(--card)); border-bottom: 1px solid hsl(var(--border));">
        <div class="flex items-center gap-2 text-sm">
          <span class="text-muted-foreground">{{ breadcrumb?.group ?? '首页' }}</span>
          <template v-if="breadcrumb?.name && breadcrumb.group !== '应用'">
            <svg class="w-3.5 h-3.5 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
            <span class="font-medium">{{ breadcrumb.name }}</span>
          </template>
        </div>

        <div class="flex items-center gap-2">
          <!-- Notification -->
          <div class="relative">
            <button
              class="relative w-8 h-8 rounded-lg flex items-center justify-center text-muted-foreground hover:bg-muted transition-colors"
              @click="toggleMessageDropdown"
            >
              <span
                v-if="unreadCount > 0"
                class="absolute -right-1 -top-1 min-w-[18px] h-[18px] px-1 rounded-full text-[10px] font-semibold flex items-center justify-center text-white"
                style="background: hsl(var(--destructive));"
              >
                {{ unreadCount > 99 ? '99+' : unreadCount }}
              </span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
              </svg>
            </button>

            <div
              v-if="messageDropdownOpen"
              class="absolute right-0 top-full mt-2 w-80 rounded-2xl border shadow-xl z-50 overflow-hidden"
              style="background: hsl(var(--card)); border-color: hsl(var(--border));"
            >
              <div class="px-4 py-3 flex items-center justify-between" style="border-bottom: 1px solid hsl(var(--border));">
                <div>
                  <p class="text-sm font-semibold">我的消息</p>
                  <p class="text-xs text-muted-foreground">{{ unreadCount }} 条未读</p>
                </div>
                <button class="text-xs font-medium" style="color: hsl(var(--primary));" @click="openMessagesPage">查看全部</button>
              </div>

              <div v-if="topMessages.length === 0" class="p-6 text-center text-sm text-muted-foreground">暂无消息</div>
              <button
                v-for="msg in topMessages"
                :key="msg.id"
                class="w-full px-4 py-3 text-left hover:bg-muted transition-colors"
                style="border-bottom: 1px solid hsl(var(--border-subtle));"
                @click="openMessage(msg)"
              >
                <div class="flex items-start gap-3">
                  <span class="mt-1 w-2 h-2 rounded-full flex-shrink-0" :style="{ background: msg.is_read ? 'hsl(var(--border-strong))' : 'hsl(var(--primary))' }" />
                  <div class="min-w-0 flex-1">
                    <div class="flex items-center justify-between gap-3">
                      <p class="text-sm font-medium truncate">{{ msg.title }}</p>
                      <span class="text-[11px] text-muted-foreground flex-shrink-0">{{ msg.created_at.slice(5, 16) }}</span>
                    </div>
                    <p class="text-xs mt-1 line-clamp-2" style="color: hsl(var(--text-2));">{{ msg.content }}</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- User card -->
          <div
            v-if="currentUser"
            class="relative"
            @mouseenter="openUserDropdown"
            @mouseleave="scheduleCloseUserDropdown"
          >
            <button
              class="flex items-center gap-2.5 pl-2 pr-3 py-1.5 rounded-xl hover:bg-muted transition-colors"
              @click="userDropdownOpen = !userDropdownOpen"
            >
              <div class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold flex-shrink-0"
                :style="{ background: themeStore.current().gradient }">
                {{ (currentUser.nickname ?? currentUser.username).charAt(0).toUpperCase() }}
              </div>
              <div class="text-left leading-tight">
                <p class="text-sm font-medium leading-none mb-0.5">{{ currentUser.nickname ?? currentUser.username }}</p>
                <p class="text-xs text-muted-foreground leading-none">{{ currentUser.email ?? '' }}</p>
              </div>
              <svg class="w-3.5 h-3.5 text-muted-foreground ml-1 flex-shrink-0 transition-transform duration-200"
                :style="{ transform: userDropdownOpen ? 'rotate(180deg)' : 'none' }"
                fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>

            <!-- Dropdown panel -->
            <div
              v-if="userDropdownOpen"
              class="absolute right-0 top-full mt-1.5 rounded-2xl shadow-xl z-50 border overflow-hidden"
              style="background: hsl(var(--card)); border-color: hsl(var(--border)); width: 240px;"
              @mouseenter="openUserDropdown"
              @mouseleave="scheduleCloseUserDropdown"
            >
              <!-- Profile header -->
              <div class="px-4 pt-4 pb-3 flex items-center gap-3"
                style="border-bottom: 1px solid hsl(var(--border));">
                <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0"
                  :style="{ background: themeStore.current().gradient }">
                  {{ (currentUser.nickname ?? currentUser.username).charAt(0).toUpperCase() }}
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-semibold truncate">{{ currentUser.nickname ?? currentUser.username }}</p>
                  <p class="text-xs text-muted-foreground truncate">{{ currentUser.email ?? '' }}</p>
                </div>
              </div>

              <!-- Dark mode toggle -->
              <div class="px-4 py-2.5 flex items-center justify-between"
                style="border-bottom: 1px solid hsl(var(--border));">
                <div class="flex items-center gap-2 text-sm">
                  <svg v-if="!themeStore.darkMode" class="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707M17.657 17.657l-.707-.707M6.343 6.343l-.707-.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/>
                  </svg>
                  <svg v-else class="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/>
                  </svg>
                  <span>{{ themeStore.darkMode ? '暗黑模式' : '明亮模式' }}</span>
                </div>
                <!-- Toggle switch -->
                <button
                  class="ds-toggle"
                  :class="{ 'ds-toggle--on': themeStore.darkMode }"
                  @click="themeStore.toggleDarkMode()"
                />
              </div>

              <!-- Sidebar style toggle -->
              <div class="px-4 py-2.5 flex items-center justify-between"
                style="border-bottom: 1px solid hsl(var(--border));">
                <div class="flex items-center gap-2 text-sm">
                  <svg class="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/>
                  </svg>
                  <span>{{ themeStore.sidebarLight ? '亮色菜单' : '暗色菜单' }}</span>
                </div>
                <button
                  class="ds-toggle"
                  :class="{ 'ds-toggle--on': themeStore.sidebarLight }"
                  @click="themeStore.toggleSidebarLight()"
                />
              </div>

              <!-- Theme colors -->
              <div class="px-4 py-3" style="border-bottom: 1px solid hsl(var(--border));">
                <p class="text-xs text-muted-foreground mb-2.5">主题颜色</p>
                <div class="grid grid-cols-6 gap-1.5">
                  <button
                    v-for="t in THEMES"
                    :key="t.id"
                    class="group flex flex-col items-center gap-1"
                    @click="themeStore.setTheme(t.id)"
                  >
                    <div
                      class="w-6 h-6 rounded-full shadow-sm transition-transform duration-150 group-hover:scale-110"
                      :style="{
                        background: t.gradient,
                        outline: themeStore.themeId === t.id ? '2px solid hsl(var(--foreground))' : '2px solid transparent',
                        outlineOffset: '2px',
                      }"
                    />
                    <span class="text-[9px] text-muted-foreground">{{ t.name }}</span>
                  </button>
                </div>
              </div>

              <!-- Actions -->
              <div class="py-1">
                <button
                  class="w-full text-left px-4 py-2.5 text-sm hover:bg-muted transition-colors flex items-center gap-2"
                  @click="goToProfile"
                >
                  <svg class="w-4 h-4 text-muted-foreground" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                  </svg>
                  个人中心
                </button>
                <button
                  class="w-full text-left px-4 py-2.5 text-sm hover:bg-muted transition-colors flex items-center gap-2 text-destructive"
                  @click="logout"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.12s ease;
}
.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
}
</style>
