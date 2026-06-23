<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Button from '@/components/ui/Button.vue'

const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-background flex flex-col items-center justify-center gap-6">
    <h1 class="text-4xl font-bold tracking-tight">AI Admin</h1>
    <p class="text-muted-foreground">欢迎回来，登录成功</p>
    <Button variant="outline" @click="logout">退出登录</Button>
  </div>
</template>
