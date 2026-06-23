<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { profileApi } from '@/api/sys/profile'
import type { User } from '@/api/sys/user'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const currentUser = ref<User | null>(null)
const userDropdownOpen = ref(false)

const nav = [
  {
    group: '系统管理',
    items: [
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

const activeGroup = computed(() =>
  nav.find(g => g.items.some(i => route.path.startsWith(i.path)))?.group
)

async function loadCurrentUser() {
  try {
    currentUser.value = await profileApi.getProfile()
  } catch {
    // ignore
  }
}

function goToProfile() {
  router.push('/profile')
  userDropdownOpen.value = false
}

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(loadCurrentUser)
</script>

<template>
  <div class="flex h-screen bg-background overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-56 flex-shrink-0 flex flex-col border-r bg-muted/30">
      <div class="h-14 flex items-center px-5 border-b font-bold text-base tracking-tight">
        AI Admin
      </div>
      <nav class="flex-1 overflow-y-auto py-3 px-2 space-y-4">
        <div v-for="group in nav" :key="group.group">
          <p class="px-3 mb-1 text-xs font-medium text-muted-foreground uppercase tracking-wider">
            {{ group.group }}
          </p>
          <RouterLink
            v-for="item in group.items"
            :key="item.path"
            :to="item.path"
            class="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors"
            :class="route.path.startsWith(item.path)
              ? 'bg-primary text-primary-foreground'
              : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'"
          >
            <!-- user -->
            <svg v-if="item.icon === 'user'" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <!-- team -->
            <svg v-else-if="item.icon === 'team'" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <!-- role -->
            <svg v-else-if="item.icon === 'role'" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <!-- permission -->
            <svg v-else-if="item.icon === 'permission'" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
            </svg>
            <!-- dict -->
            <svg v-else-if="item.icon === 'dict'" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            <!-- api -->
            <svg v-else-if="item.icon === 'api'" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <!-- menu -->
            <svg v-else-if="item.icon === 'menu'" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
            </svg>
            <!-- fallback -->
            <svg v-else class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {{ item.name }}
          </RouterLink>
        </div>
      </nav>
      <div class="p-3 border-t">
        <button
          class="w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
          @click="logout"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          退出登录
        </button>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="h-14 flex items-center justify-between px-6 border-b bg-background flex-shrink-0">
        <span class="text-sm text-muted-foreground">
          {{ activeGroup ?? '首页' }}
          <template v-if="$route.meta.title"> / <span class="text-foreground font-medium">{{ $route.meta.title }}</span></template>
        </span>

        <!-- User info -->
        <div v-if="currentUser" class="relative">
          <button
            class="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm hover:bg-muted transition-colors"
            @click="userDropdownOpen = !userDropdownOpen"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>{{ currentUser.nickname ?? currentUser.username }}</span>
          </button>
          <div
            v-if="userDropdownOpen"
            class="absolute right-0 mt-2 w-48 bg-background border rounded-lg shadow-lg z-10"
          >
            <button
              class="w-full text-left px-4 py-2 text-sm hover:bg-muted first:rounded-t-md transition-colors"
              @click="goToProfile"
            >
              个人中心
            </button>
            <button
              class="w-full text-left px-4 py-2 text-sm hover:bg-muted last:rounded-b-md text-destructive transition-colors"
              @click="logout"
            >
              退出登录
            </button>
          </div>
        </div>
      </header>
      <main class="flex-1 overflow-y-auto p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
