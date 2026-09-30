<template>
  <div class="base-crud-list">
    <!-- Tab bar -->
    <div v-if="tabs && tabs.length > 1" class="crud-tabs">
      <BaseButton
        v-for="tab in tabs"
        :key="tab.key"
        variant="ghost"
        class="crud-tab"
        :class="{ active: activeTab === tab.key }"
        @click="$emit('update:activeTab', tab.key)"
      >
        {{ tab.label }}
        <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
      </BaseButton>
    </div>

    <!-- Search + Toolbar (合并为一行) -->
    <div class="crud-header" v-if="hasSearchOrToolbar">
      <div class="crud-header-left">
        <template v-for="field in (searchFields || [])" :key="field.key">
          <div class="search-field">
            <label class="search-label">{{ field.label }}:</label>
            <BaseSelect
              v-if="field.type === 'select'"
              :model-value="searchModel[field.key]"
              @update:model-value="$emit('update:searchModel', { ...searchModel, [field.key]: $event })"
              :options="field.options || []"
              size="sm"
              :placeholder="field.placeholder || '请选择'"
            />
            <BaseCalendarPicker
              v-else-if="field.type === 'date'"
              :model-value="searchModel[field.key]"
              @update:model-value="$emit('update:searchModel', { ...searchModel, [field.key]: $event })"
              size="sm"
              :placeholder="field.placeholder || '选择日期'"
            />
            <BaseInput
              v-else
              size="sm"
              class="search-input"
              :model-value="searchModel[field.key]"
              @update:model-value="$emit('update:searchModel', { ...searchModel, [field.key]: $event })"
              :placeholder="field.placeholder || '请输入'"
              @keydown.enter="$emit('search', searchModel)"
            />
          </div>
        </template>
        <div class="search-actions" v-if="searchFields && searchFields.length > 0">
          <BaseButton size="sm" variant="primary" @click="$emit('search', searchModel)">
            <BaseIcon name="search" :size="14" />
            搜索
          </BaseButton>
          <BaseButton size="sm" variant="ghost" @click="onResetSearch">
            <BaseIcon name="rotate-ccw" :size="14" />
            重置
          </BaseButton>
        </div>
        <!-- 批量操作按钮 -->
        <div class="toolbar-batch" v-if="toolbarActions && toolbarActions.length > 0">
          <template v-for="action in toolbarActions" :key="action.key">
            <BaseButton
              size="sm"
              :variant="action.variant || 'ghost'"
              :disabled="action.needSelection && selectedIds.length === 0"
              @click="$emit('toolbar-action', action.key, selectedIds)"
            >
              {{ action.label }}
            </BaseButton>
          </template>
          <slot name="toolbar-left" />
        </div>
      </div>
      <div class="crud-header-right">
        <slot name="toolbar-right" />
        <BaseButton v-if="showRefresh" variant="icon" title="刷新" @click="$emit('refresh')">
          <BaseIcon name="refresh-cw" :size="14" />
        </BaseButton>
        <BaseButton v-if="showDensityToggle" variant="icon" title="密度" @click="cycleDensity">
          <BaseIcon name="list" :size="14" />
        </BaseButton>
      </div>
    </div>

    <!-- Table -->
    <BaseTable
      :columns="columns"
      :data="data"
      :row-key="rowKey"
      :selectable="selectable"
      :density="density"
      v-model="selectedIds"
      @sort-change="onSortChange"
      @selection-change="onSelectionChange"
    >
      <template v-for="(_, slotName) in $slots" :key="slotName" v-slot:[slotName]="slotProps">
        <slot :name="slotName" v-bind="slotProps ?? {}" />
      </template>
    </BaseTable>

    <!-- Pagination -->
    <BasePagination
      v-if="showPagination && total > 0"
      :total="total"
      :page="page"
      :page-size="pageSize"
      :page-sizes="pageSizes"
      @update:page="$emit('update:page', $event)"
      @update:page-size="$emit('update:pageSize', $event)"
      @change="$emit('page-change', $event[0], $event[1])"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import BaseTable from '../base/BaseTable.vue'
import BasePagination from './BasePagination.vue'
import BaseButton from '../base/BaseButton.vue'
import BaseSelect from '../base/BaseSelect.vue'
import BaseInput from '../base/BaseInput.vue'
import BaseCalendarPicker from '../base/BaseCalendarPicker.vue'
import BaseIcon from '../base/BaseIcon.vue'

interface Column {
  key: string
  label: string
  width?: string
  minWidth?: string
  maxWidth?: string
  sortable?: boolean
  ellipsis?: boolean
  align?: 'left' | 'center' | 'right'
  fixed?: 'left' | 'right'
}

interface SearchField {
  key: string
  label: string
  type: 'input' | 'select' | 'date' | 'daterange'
  options?: { label: string; value: any }[]
  placeholder?: string
}

interface ToolbarAction {
  key: string
  label: string
  variant?: 'primary' | 'danger' | 'ghost'
  needSelection?: boolean
}

interface Tab {
  key: string
  label: string
  count?: number
}

const props = withDefaults(defineProps<{
  columns: Column[]
  data: any[]
  rowKey?: string
  selectable?: boolean
  density?: 'compact' | 'default' | 'loose'
  loading?: boolean
  // Search
  searchFields?: SearchField[]
  searchModel?: Record<string, any>
  // Toolbar
  toolbarActions?: ToolbarAction[]
  showRefresh?: boolean
  showColumnSetting?: boolean
  showDensityToggle?: boolean
  // Pagination
  total?: number
  page?: number
  pageSize?: number
  pageSizes?: number[]
  showPagination?: boolean
  // Tab
  tabs?: Tab[]
  activeTab?: string
}>(), {
  rowKey: 'id',
  selectable: false,
  density: 'default',
  loading: false,
  searchFields: () => [],
  searchModel: () => ({}),
  toolbarActions: () => [],
  showRefresh: true,
  showColumnSetting: false,
  showDensityToggle: true,
  total: 0,
  page: 1,
  pageSize: 10,
  pageSizes: () => [10, 20, 50],
  showPagination: true,
  activeTab: '',
})

const emit = defineEmits<{
  'update:searchModel': [value: Record<string, any>]
  'update:page': [value: number]
  'update:pageSize': [value: number]
  'update:activeTab': [value: string]
  'search': [params: Record<string, any>]
  'reset': []
  'page-change': [page: number, pageSize: number]
  'selection-change': [ids: (string | number)[]]
  'sort-change': [key: string, order: 'asc' | 'desc' | null]
  'toolbar-action': [actionKey: string, selectedIds: (string | number)[]]
  'refresh': []
}>()

const selectedIds = ref<(string | number)[]>([])
const density = ref<'compact' | 'default' | 'loose'>('default')

const hasSearchOrToolbar = computed(() =>
  (props.searchFields && props.searchFields.length > 0) ||
  (props.toolbarActions && props.toolbarActions.length > 0) ||
  props.showRefresh || props.showColumnSetting || props.showDensityToggle
)

function onResetSearch() {
  const reset: Record<string, any> = {}
  ;(props.searchFields || []).forEach(f => { reset[f.key] = undefined })
  emit('update:searchModel', reset)
  emit('reset')
}

function onSelectionChange(ids: (string | number)[]) {
  selectedIds.value = ids
  emit('selection-change', ids)
}

function onSortChange(key: string, order: 'asc' | 'desc' | null) {
  emit('sort-change', key, order)
}

function cycleDensity() {
  const order: ('compact' | 'default' | 'loose')[] = ['compact', 'default', 'loose']
  const idx = order.indexOf(density.value)
  density.value = order[(idx + 1) % order.length]
}
</script>

<style scoped>
.base-crud-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

/* Tab bar */
.crud-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 0;
}

.crud-tab {
  /* 标签页：无边框纯文字风格，选中态与内容区同色一体 */
  border: none !important;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
  background: transparent !important;
  padding: 8px 16px;
  font-size: 14px;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}
.crud-tab:hover {
  color: var(--text-primary);
  background: var(--bg-hover) !important;
}
.crud-tab.active {
  color: var(--accent-blue);
  font-weight: 600;
  background: var(--bg-base) !important;
  position: relative;
  z-index: 1;
}

.tab-count {
  font-size: 11px;
  background: var(--bg-elevated);
  color: var(--text-tertiary);
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 400;
}
.crud-tab.active .tab-count {
  background: rgba(59, 130, 246, 0.1);
  color: var(--accent-blue);
}

/* Search + Toolbar merged header */
.crud-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: var(--bg-base, #fff);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  margin-bottom: 8px;
  gap: 12px;
  flex-wrap: wrap;
}

.crud-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  flex: 1;
}

.crud-header-right {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.search-field {
  display: flex;
  align-items: center;
  gap: 4px;
}

.search-label {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.search-input {
  width: 140px;
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.toolbar-batch {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 8px;
  padding-left: 8px;
  border-left: 1px solid var(--border-subtle);
}


</style>
