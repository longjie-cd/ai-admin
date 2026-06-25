<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore, THEMES } from '@/stores/theme'
import { useSystemStore } from '@/stores/system'
import { profileApi } from '@/api/sys/profile'
import { messageApi, type Message } from '@/api/sys/message'
import type { Menu } from '@/api/sys/menu'
import type { User } from '@/api/sys/user'
import AppSidebarMenuItem from '@/components/AppSidebarMenuItem.vue'

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
const sidebarCollapsed = ref(localStorage.getItem('sidebar-collapsed') === 'true')
let userDropdownTimer: ReturnType<typeof setTimeout> | null = null

function normalizePath(path?: string) {
  if (!path) return ''
  return path.startsWith('/') ? path : `/${path}`
}

function isRouteMatch(menuPath: string, routePath: string) {
  if (!menuPath) return false
  const normalized = normalizePath(menuPath)
  if (normalized === '/') return routePath === '/'
  return routePath === normalized || routePath.startsWith(`${normalized}/`)
}

function findMenuChain(items: Menu[], routePath: string): Menu[] {
  for (const item of items) {
    const childChain = findMenuChain(item.children ?? [], routePath)
    if (childChain.length) return [item, ...childChain]
    if (isRouteMatch(item.path, routePath)) return [item]
  }
  return []
}

function isRoutablePath(path?: string) {
  const normalized = normalizePath(path)
  if (!normalized) return false
  const resolved = router.resolve(normalized)
  return resolved.matched.some(record => record.path === normalized)
}

function findDefaultTarget(item: Menu): string | null {
  const children = [...(item.children ?? [])].sort((a, b) => a.sort - b.sort)
  for (const child of children) {
    const childTarget = findDefaultTarget(child)
    if (childTarget) return childTarget
  }
  return isRoutablePath(item.path) ? normalizePath(item.path) : null
}

const apps = computed(() => [...systemStore.userMenus].sort((a, b) => a.sort - b.sort))
const currentMenuChain = computed(() => findMenuChain(apps.value, route.path))
const currentApp = computed(() => currentMenuChain.value[0] ?? null)
const sidebarMenus = computed(() =>
  [...(currentApp.value?.children ?? [])].sort((a, b) => a.sort - b.sort),
)
const showSidebar = computed(() => sidebarMenus.value.length > 0)
const brandInitial = computed(() => systemStore.systemName.trim().charAt(0) || 'A')

const headerStyle = computed(() => ({
  background: 'hsl(var(--primary))',
}))

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem('sidebar-collapsed', String(sidebarCollapsed.value))
}

async function loadCurrentUser() {
  try {
    currentUser.value = await profileApi.getProfile()
  } catch {
    currentUser.value = null
  }
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
  if (messageDropdownOpen.value) await loadMessages()
}

async function openMessagesPage() {
  messageDropdownOpen.value = false
  await router.push('/sys/message')
}

async function openMessage(msg: Message) {
  messageDropdownOpen.value = false
  if (!msg.is_read) {
    try {
      await messageApi.update(msg.id, { is_read: true })
      msg.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch {
      // ignore
    }
  }
  if (msg.link) {
    await router.push(msg.link)
  } else {
    await router.push('/sys/message')
  }
}

async function goToProfile() {
  userDropdownOpen.value = false
  await router.push('/profile')
}

function logout() {
  systemStore.clearUserMenus()
  auth.logout()
  router.push('/login')
}

async function navigateToMenu(menu: Menu) {
  const target = findDefaultTarget(menu)
  if (!target || target === route.path) return
  await router.push(target)
}

async function navigateToApp(app: Menu) {
  await navigateToMenu(app)
}

onMounted(async () => {
  themeStore.init()
  await Promise.all([
    systemStore.fetchSystemName(),
    systemStore.fetchSystemLogo(),
    systemStore.fetchUserMenus(),
    loadCurrentUser(),
    loadMessages(),
  ])
})

onBeforeUnmount(() => {
  if (userDropdownTimer) clearTimeout(userDropdownTimer)
})
</script>

<template>
  <div class="flex h-screen flex-col overflow-hidden bg-[hsl(var(--background))]">
    <header class="relative z-20 text-white" :style="headerStyle">
      <div class="flex h-[55px] items-center gap-4 px-5">
        <div class="flex min-w-[180px] items-center gap-3">
          <img
            v-if="systemStore.systemLogo"
            :src="systemStore.systemLogo"
            :alt="systemStore.systemName"
            class="h-9 max-w-[140px] object-contain"
          >
          <div
            v-else
            class="flex h-10 w-10 items-center justify-center rounded-2xl text-base font-bold text-white shadow-sm"
            :style="{ background: themeStore.current().gradient }"
          >
            {{ brandInitial }}
          </div>
          <div class="min-w-0">
            <p class="truncate text-base font-semibold tracking-[0.08em] text-white">{{ systemStore.systemName }}</p>
          </div>
        </div>

        <div class="flex min-w-0 flex-1 items-center gap-2 overflow-x-auto py-2">
          <button
            v-for="app in apps"
            :key="app.id"
            class="px-3 py-2 text-sm transition-all"
            :class="currentApp?.id === app.id ? 'text-white font-bold' : 'text-white/60 font-medium hover:text-white'"
            @click="navigateToApp(app)"
          >
            <span class="whitespace-nowrap">{{ app.name }}</span>
          </button>
        </div>

        <div class="flex items-center gap-2">
          <div class="relative">
            <button
              class="relative flex h-10 w-10 items-center justify-center rounded-2xl bg-white/8 text-white/90 transition hover:bg-white/14"
              @click="toggleMessageDropdown"
            >
              <span
                v-if="unreadCount > 0"
                class="absolute -right-1 -top-1 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-semibold text-white"
              >
                {{ unreadCount > 99 ? '99+' : unreadCount }}
              </span>
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>

            <div
              v-if="messageDropdownOpen"
              class="absolute right-0 top-full z-50 mt-2 w-80 overflow-hidden rounded-3xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] text-[hsl(var(--foreground))] shadow-2xl"
            >
              <div class="flex items-center justify-between border-b border-[hsl(var(--border))] px-4 py-3">
                <div>
                  <p class="text-sm font-semibold">我的消息</p>
                  <p class="text-xs text-[hsl(var(--muted-foreground))]">{{ unreadCount }} 条未读</p>
                </div>
                <button class="text-xs font-medium text-[hsl(var(--primary))]" @click="openMessagesPage">查看全部</button>
              </div>

              <div v-if="topMessages.length === 0" class="p-6 text-center text-sm text-[hsl(var(--muted-foreground))]">暂无消息</div>
              <button
                v-for="msg in topMessages"
                :key="msg.id"
                class="w-full border-b border-[hsl(var(--border-subtle))] px-4 py-3 text-left transition hover:bg-[hsl(var(--bg-hover))]"
                @click="openMessage(msg)"
              >
                <div class="flex items-start gap-3">
                  <span class="mt-1 h-2 w-2 flex-shrink-0 rounded-full" :style="{ background: msg.is_read ? 'hsl(var(--border-strong))' : 'hsl(var(--primary))' }" />
                  <div class="min-w-0 flex-1">
                    <div class="flex items-center justify-between gap-3">
                      <p class="truncate text-sm font-medium">{{ msg.title }}</p>
                      <span class="flex-shrink-0 text-[11px] text-[hsl(var(--muted-foreground))]">{{ msg.created_at.slice(5, 16) }}</span>
                    </div>
                    <p class="mt-1 line-clamp-2 text-xs text-[hsl(var(--text-2))]">{{ msg.content }}</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          <div
            v-if="currentUser"
            class="relative"
            @mouseenter="openUserDropdown"
            @mouseleave="scheduleCloseUserDropdown"
          >
            <button
              class="flex items-center gap-2 rounded-2xl bg-white/8 px-2.5 py-1.5 text-left transition hover:bg-white/14"
              @click="userDropdownOpen = !userDropdownOpen"
            >
              <div
                class="flex h-9 w-9 items-center justify-center rounded-full text-sm font-semibold text-white"
                :style="{ background: themeStore.current().gradient }"
              >
                {{ (currentUser.nickname ?? currentUser.username).charAt(0).toUpperCase() }}
              </div>
              <div class="hidden sm:block">
                <p class="max-w-[120px] truncate text-sm font-medium text-white">{{ currentUser.nickname ?? currentUser.username }}</p>
                <p class="max-w-[120px] truncate text-xs text-white/60">{{ currentUser.email ?? '' }}</p>
              </div>
              <svg class="h-3.5 w-3.5 text-white/60 transition-transform" :style="{ transform: userDropdownOpen ? 'rotate(180deg)' : 'none' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            <div
              v-if="userDropdownOpen"
              class="absolute right-0 top-full z-50 mt-2 w-64 overflow-hidden rounded-3xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] text-[hsl(var(--foreground))] shadow-2xl"
              @mouseenter="openUserDropdown"
              @mouseleave="scheduleCloseUserDropdown"
            >
              <div class="flex items-center gap-3 border-b border-[hsl(var(--border))] px-4 pb-3 pt-4">
                <div
                  class="flex h-10 w-10 items-center justify-center rounded-full font-semibold text-white"
                  :style="{ background: themeStore.current().gradient }"
                >
                  {{ (currentUser.nickname ?? currentUser.username).charAt(0).toUpperCase() }}
                </div>
                <div class="min-w-0">
                  <p class="truncate text-sm font-semibold">{{ currentUser.nickname ?? currentUser.username }}</p>
                  <p class="truncate text-xs text-[hsl(var(--muted-foreground))]">{{ currentUser.email ?? '' }}</p>
                </div>
              </div>

              <div class="border-b border-[hsl(var(--border))] px-4 py-3">
                <p class="mb-2 text-xs text-[hsl(var(--muted-foreground))]">主题颜色</p>
                <div class="grid grid-cols-6 gap-2">
                  <button
                    v-for="t in THEMES"
                    :key="t.id"
                    class="group flex flex-col items-center gap-1"
                    @click="themeStore.setTheme(t.id)"
                  >
                    <div
                      class="h-6 w-6 rounded-full shadow-sm transition-transform group-hover:scale-110"
                      :style="{
                        background: t.gradient,
                        outline: themeStore.themeId === t.id ? '2px solid hsl(var(--foreground))' : '2px solid transparent',
                        outlineOffset: '2px',
                      }"
                    />
                    <span class="text-[9px] text-[hsl(var(--muted-foreground))]">{{ t.name }}</span>
                  </button>
                </div>
              </div>

              <div class="border-b border-[hsl(var(--border))] px-4 py-3">
                <button class="flex w-full items-center justify-between text-sm" @click="themeStore.toggleDarkMode()">
                  <span>{{ themeStore.darkMode ? '暗黑模式' : '明亮模式' }}</span>
                  <span class="rounded-full px-2 py-0.5 text-xs" :class="themeStore.darkMode ? 'bg-[hsl(var(--primary)/0.12)] text-[hsl(var(--primary))]' : 'bg-[hsl(var(--bg-sunken))] text-[hsl(var(--text-3))]'">
                    {{ themeStore.darkMode ? '开启' : '关闭' }}
                  </span>
                </button>
              </div>

              <div class="py-2">
                <button
                  class="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm transition hover:bg-[hsl(var(--bg-hover))]"
                  @click="goToProfile"
                >
                  <svg class="h-4 w-4 text-[hsl(var(--muted-foreground))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  个人中心
                </button>
                <button
                  class="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm text-rose-500 transition hover:bg-[hsl(var(--bg-hover))]"
                  @click="logout"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <div class="flex min-h-0 flex-1 bg-[linear-gradient(180deg,hsl(var(--background))_0%,hsl(var(--bg-surface))_100%)]">
      <aside
        v-if="showSidebar"
        class="flex flex-shrink-0 flex-col border-r border-[hsl(var(--border-subtle))] bg-[hsl(var(--card))] transition-all duration-200"
        :class="sidebarCollapsed ? 'w-[72px]' : 'w-[240px]'"
      >
        <div class="border-b border-[hsl(var(--border-subtle))] py-4" :class="sidebarCollapsed ? 'px-3 text-center' : 'px-5'">
          <p v-if="!sidebarCollapsed" class="truncate text-base font-semibold text-[hsl(var(--text-1))]">{{ currentApp?.name }}</p>
          <p v-else class="text-sm font-semibold text-[hsl(var(--text-1))]">{{ currentApp?.name.slice(0, 1) }}</p>
        </div>

        <div class="flex-1 overflow-y-auto px-3 py-4">
          <div class="space-y-1">
            <AppSidebarMenuItem
              v-for="item in sidebarMenus"
              :key="item.id"
              :item="item"
              :current-path="route.path"
              :collapsed="sidebarCollapsed"
              @navigate="navigateToMenu"
            />
          </div>
        </div>

        <div class="border-t border-[hsl(var(--border-subtle))] p-3">
          <button
            class="flex w-full items-center rounded-xl text-sm text-[hsl(var(--text-2))] transition hover:bg-[hsl(var(--bg-hover))] hover:text-[hsl(var(--text-1))]"
            :class="sidebarCollapsed ? 'justify-center px-2 py-2.5' : 'gap-2 px-3 py-2.5'"
            :title="sidebarCollapsed ? '展开菜单' : '收起菜单'"
            @click="toggleSidebar"
          >
            <svg
              class="h-4 w-4 flex-shrink-0 transition-transform"
              :style="{ transform: sidebarCollapsed ? 'rotate(180deg)' : 'rotate(0deg)' }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
            </svg>
            <span v-if="!sidebarCollapsed">收起菜单</span>
          </button>
        </div>
      </aside>

      <main class="min-w-0 flex-1 overflow-y-auto p-5">
        <RouterView />
      </main>
    </div>
  </div>
</template>
