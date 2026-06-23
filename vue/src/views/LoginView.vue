<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const wallpaper = ref<{ url: string; copyright: string } | null>(null)

onMounted(async () => {
  try {
    const res = await fetch('/api/bing/wallpaper')
    const json = await res.json()
    if (json.code === 0) wallpaper.value = json.data
  } catch {
    // 壁纸加载失败时使用渐变背景兜底
  }
})

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value }),
    })
    const json = await res.json()
    if (json.code === 0) {
      auth.setToken(json.data.access_token)
      router.push('/')
    } else {
      error.value = json.detail ?? json.message ?? '登录失败'
    }
  } catch {
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <!-- 背景层 -->
  <div class="relative min-h-screen flex items-center justify-center overflow-hidden">
    <!-- Bing 壁纸 -->
    <transition name="fade">
      <div
        v-if="wallpaper"
        class="absolute inset-0 bg-cover bg-center bg-no-repeat"
        :style="{ backgroundImage: `url(${wallpaper.url})` }"
      />
    </transition>
    <!-- 无壁纸时的渐变兜底 -->
    <div
      v-if="!wallpaper"
      class="absolute inset-0 bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900"
    />
    <!-- 遮罩 -->
    <div class="absolute inset-0 bg-black/40 backdrop-blur-[2px]" />

    <!-- 登录卡片 -->
    <Card class="relative z-10 w-full max-w-sm mx-4 p-8 bg-white/10 backdrop-blur-md border-white/20 shadow-2xl">
      <div class="mb-8 text-center">
        <h1 class="text-2xl font-bold text-white tracking-tight">AI Admin</h1>
        <p class="mt-1 text-sm text-white/60">请登录以继续</p>
      </div>

      <form class="space-y-4" @submit.prevent="handleLogin">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-white/80">用户名</label>
          <Input
            v-model="username"
            placeholder="请输入用户名"
            autocomplete="username"
            class="bg-white/10 border-white/20 text-white placeholder:text-white/40 focus-visible:ring-white/50"
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium text-white/80">密码</label>
          <Input
            v-model="password"
            type="password"
            placeholder="请输入密码"
            autocomplete="current-password"
            class="bg-white/10 border-white/20 text-white placeholder:text-white/40 focus-visible:ring-white/50"
          />
        </div>

        <p v-if="error" class="text-sm text-red-400">{{ error }}</p>

        <Button
          type="submit"
          class="w-full bg-white text-slate-900 hover:bg-white/90 mt-2"
          :disabled="loading"
        >
          {{ loading ? '登录中...' : '登录' }}
        </Button>
      </form>

      <!-- 壁纸版权信息 -->
      <p
        v-if="wallpaper?.copyright"
        class="mt-6 text-center text-xs text-white/30 truncate"
        :title="wallpaper.copyright"
      >
        {{ wallpaper.copyright }}
      </p>
    </Card>
  </div>
</template>

<style scoped>
.fade-enter-active {
  transition: opacity 0.8s ease;
}
.fade-enter-from {
  opacity: 0;
}
</style>
