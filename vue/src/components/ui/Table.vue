<script setup lang="ts">
defineProps<{ loading?: boolean; empty?: string }>()
</script>

<template>
  <div class="w-full overflow-auto rounded-lg border">
    <table class="w-full text-sm">
      <thead class="bg-muted/50">
        <tr>
          <slot name="head" />
        </tr>
      </thead>
      <tbody>
        <template v-if="loading">
          <tr>
            <td colspan="99" class="py-12 text-center text-muted-foreground">加载中...</td>
          </tr>
        </template>
        <template v-else>
          <slot />
          <tr v-if="!$slots.default">
            <td colspan="99" class="py-12 text-center text-muted-foreground">{{ empty ?? '暂无数据' }}</td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>
