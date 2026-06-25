<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { announcementApi, type Announcement } from '@/api/sys/announcement'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'

const route = useRoute()
const router = useRouter()
const announcement = ref<Announcement | null>(null)
const loading = ref(false)

onMounted(async () => {
  const id = Number(route.params.id)
  if (!id) return
  loading.value = true
  try {
    announcement.value = await announcementApi.get(id)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-3xl mx-auto space-y-4">
    <Button variant="outline" size="sm" @click="router.back()">返回</Button>

    <Card class="p-6">
      <div v-if="loading" class="py-12 text-center" style="color: hsl(var(--text-3))">加载中...</div>
      <div v-else-if="!announcement" class="py-12 text-center" style="color: hsl(var(--text-3))">公告不存在</div>
      <div v-else>
        <h1 class="text-2xl font-bold mb-4">{{ announcement.title }}</h1>
        <div class="flex items-center gap-4 text-xs mb-6" style="color: hsl(var(--text-3))">
          <span>发布时间：{{ announcement.created_at }}</span>
          <span v-if="announcement.push_message" class="px-2 py-0.5 rounded-full font-medium" style="background: rgba(59,130,246,0.1); color: #3B82F6;">已推送消息</span>
        </div>
        <div class="text-sm leading-7 whitespace-pre-wrap" style="color: hsl(var(--text-1))">{{ announcement.content }}</div>
      </div>
    </Card>
  </div>
</template>
