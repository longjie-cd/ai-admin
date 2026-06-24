<script setup lang="ts">
defineProps<{ loading?: boolean; empty?: string }>()
</script>

<template>
  <div class="ds-table-wrap">
    <table class="ds-table">
      <thead class="ds-table__head">
        <tr><slot name="head" /></tr>
      </thead>
      <tbody class="ds-table__body">
        <template v-if="loading">
          <tr><td colspan="99" class="ds-table__empty">加载中...</td></tr>
        </template>
        <template v-else>
          <slot />
          <tr v-if="!$slots.default">
            <td colspan="99" class="ds-table__empty">{{ empty ?? '暂无数据' }}</td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<style>
.ds-table-wrap {
  width: 100%;
  overflow-x: auto;
  border-radius: var(--table-radius);
  border: 1px solid var(--table-border);
  background: var(--card-bg);
  box-shadow: var(--card-shadow);
}
.ds-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}
.ds-table__head tr {
  background: var(--table-head-bg);
  border-bottom: 1px solid var(--table-border);
}
.ds-table__head th {
  padding: 10px 16px;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--table-head-color);
  letter-spacing: 0.02em;
  text-transform: uppercase;
  white-space: nowrap;
}
.ds-table__body tr {
  border-bottom: 1px solid hsl(var(--border-subtle));
  transition: background var(--transition-fast);
}
.ds-table__body tr:last-child { border-bottom: none; }
.ds-table__body tr:hover { background: var(--table-row-hover); }
.ds-table__body td {
  padding: 11px 16px;
  color: hsl(var(--text-1));
  vertical-align: middle;
}
.ds-table__empty {
  padding: 48px 16px;
  text-align: center;
  color: hsl(var(--text-3)) !important;
  font-size: 0.875rem;
}
</style>
