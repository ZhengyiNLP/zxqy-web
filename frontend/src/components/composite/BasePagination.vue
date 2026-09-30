<template>
  <div class="base-pagination" v-if="total > 0">
    <span class="pagination-total">共 {{ total }} 条</span>
    <div class="pagination-controls">
      <BaseButton variant="ghost" size="sm" class="page-btn" :disabled="page <= 1" @click="changePage(page - 1)">‹</BaseButton>
      <template v-for="p in displayedPages" :key="p">
        <span v-if="p === '...'" class="page-ellipsis">...</span>
        <BaseButton v-else variant="ghost" size="sm" class="page-btn" :class="{ active: p === page }" @click="changePage(p as number)">{{ p }}</BaseButton>
      </template>
      <BaseButton variant="ghost" size="sm" class="page-btn" :disabled="page >= totalPages" @click="changePage(page + 1)">›</BaseButton>
    </div>
    <div class="pagination-size" v-if="showSizeChanger">
      <BaseSelect
        :model-value="pageSize"
        @update:model-value="changeSize"
        :options="pageSizeOptions"
        size="sm"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseButton from '../base/BaseButton.vue'
import BaseSelect from '../base/BaseSelect.vue'

const props = withDefaults(defineProps<{
  total: number
  page: number
  pageSize: number
  pageSizes?: number[]
  showSizeChanger?: boolean
}>(), {
  pageSizes: () => [10, 20, 50],
  showSizeChanger: true,
})

const emit = defineEmits<{
  'update:page': [value: number]
  'update:pageSize': [value: number]
  'change': [page: number, pageSize: number]
}>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))

const pageSizeOptions = computed(() =>
  props.pageSizes.map(s => ({ value: s, label: `${s}条/页` }))
)

const displayedPages = computed(() => {
  const total = totalPages.value
  const current = props.page
  const pages: (number | string)[] = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    const start = Math.max(2, current - 1)
    const end = Math.min(total - 1, current + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

function changePage(p: number) {
  if (p < 1 || p > totalPages.value || p === props.page) return
  emit('update:page', p)
  emit('change', p, props.pageSize)
}

function changeSize(s: number) {
  emit('update:pageSize', s)
  emit('update:page', 1)
  emit('change', 1, s)
}
</script>

<style scoped>
.base-pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 12px 0;
  font-size: 13px;
  color: var(--text-secondary);
}

.pagination-total {
  color: var(--text-tertiary);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.page-btn {
  min-width: 28px;
  height: var(--control-height-sm);
  padding: 0 6px;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.page-btn.active {
  background: var(--accent-blue);
  color: #fff;
  border-color: var(--accent-blue);
}
.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-ellipsis {
  padding: 0 4px;
  color: var(--text-tertiary);
}
</style>
