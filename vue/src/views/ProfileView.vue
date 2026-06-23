<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { profileApi } from '@/api/sys/profile'
import type { User } from '@/api/sys/user'
import Card from '@/components/ui/Card.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Dialog from '@/components/ui/Dialog.vue'

const user = ref<User | null>(null)
const loading = ref(false)
const form = ref({ nickname: '', email: '' })
const passwordForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const editDialogOpen = ref(false)
const passwordDialogOpen = ref(false)
const submitting = ref(false)

async function loadProfile() {
  loading.value = true
  try {
    user.value = await profileApi.getProfile()
    form.value = { nickname: user.value?.nickname ?? '', email: user.value?.email ?? '' }
  } finally {
    loading.value = false
  }
}

function openEditDialog() {
  if (user.value) {
    form.value = { nickname: user.value.nickname ?? '', email: user.value.email ?? '' }
  }
  editDialogOpen.value = true
}

function openPasswordDialog() {
  passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  passwordDialogOpen.value = true
}

async function submitProfile() {
  submitting.value = true
  try {
    user.value = await profileApi.updateProfile(form.value)
    editDialogOpen.value = false
  } finally {
    submitting.value = false
  }
}

async function submitPassword() {
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    alert('新密码与确认密码不一致')
    return
  }
  submitting.value = true
  try {
    await profileApi.changePassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
    })
    passwordDialogOpen.value = false
    alert('密码修改成功')
  } finally {
    submitting.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div v-if="loading" class="text-center py-12 text-muted-foreground">加载中...</div>
  <div v-else class="max-w-2xl space-y-4">
    <h1 class="text-2xl font-bold">个人中心</h1>

    <!-- 基本信息 -->
    <Card class="p-6">
      <h2 class="text-lg font-semibold mb-4">基本信息</h2>
      <div class="space-y-3">
        <div class="flex items-center gap-12">
          <span class="text-muted-foreground w-20">用户名</span>
          <span class="font-medium">{{ user?.username }}</span>
        </div>
        <div class="flex items-center gap-12">
          <span class="text-muted-foreground w-20">昵称</span>
          <span>{{ user?.nickname ?? '-' }}</span>
        </div>
        <div class="flex items-center gap-12">
          <span class="text-muted-foreground w-20">邮箱</span>
          <span>{{ user?.email ?? '-' }}</span>
        </div>
        <div class="flex items-center gap-12">
          <span class="text-muted-foreground w-20">状态</span>
          <span :class="user?.disabled ? 'text-destructive' : 'text-green-600'">
            {{ user?.disabled ? '禁用' : '正常' }}
          </span>
        </div>
      </div>
      <div class="mt-6 flex gap-2">
        <Button @click="openEditDialog">编辑信息</Button>
        <Button variant="outline" @click="openPasswordDialog">修改密码</Button>
      </div>
    </Card>

    <!-- 角色和团队 -->
    <Card class="p-6">
      <h2 class="text-lg font-semibold mb-4">关联信息</h2>
      <div class="space-y-3">
        <div class="flex items-center gap-12">
          <span class="text-muted-foreground w-20">角色数</span>
          <span class="font-medium">{{ user?.role_ids.length ?? 0 }}</span>
        </div>
        <div class="flex items-center gap-12">
          <span class="text-muted-foreground w-20">所属团队</span>
          <span>{{ user?.team_id ? `#${user.team_id}` : '无' }}</span>
        </div>
      </div>
    </Card>
  </div>

  <!-- 编辑信息对话框 -->
  <Dialog :open="editDialogOpen" title="编辑个人信息" :loading="submitting"
    @update:open="editDialogOpen = $event" @confirm="submitProfile">
    <div class="space-y-3">
      <div class="space-y-1">
        <label class="text-sm font-medium">昵称</label>
        <Input v-model="form.nickname" placeholder="请输入昵称" />
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium">邮箱</label>
        <Input v-model="form.email" type="email" placeholder="请输入邮箱地址" />
      </div>
    </div>
  </Dialog>

  <!-- 修改密码对话框 -->
  <Dialog :open="passwordDialogOpen" title="修改密码" :loading="submitting"
    @update:open="passwordDialogOpen = $event" @confirm="submitPassword">
    <div class="space-y-3">
      <div class="space-y-1">
        <label class="text-sm font-medium">旧密码 *</label>
        <Input v-model="passwordForm.old_password" type="password" placeholder="请输入旧密码" />
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium">新密码 *</label>
        <Input v-model="passwordForm.new_password" type="password" placeholder="请输入新密码" />
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium">确认密码 *</label>
        <Input v-model="passwordForm.confirm_password" type="password" placeholder="请再次输入新密码" />
      </div>
    </div>
  </Dialog>
</template>
