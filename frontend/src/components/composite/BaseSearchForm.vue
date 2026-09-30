<template>
  <div class="base-search-form" v-if="fields.length > 0">
    <div class="search-fields">
      <template v-for="field in visibleFields" :key="field.key">
        <div class="search-field">
          <label class="search-label">{{ field.label }}:</label>
          <BaseSelect
            v-if="field.type === 'select'"
            :model-value="modelValue[field.key]"
            @update:model-value="onFieldChange(field.key, $event)"
            :options="field.options || []"
            size="sm"
            :placeholder="field.placeholder || '请选择'"
          />
          <input
            v-else
            type="text"
            class="search-input"
            :value="modelValue[field.key]"
            @input="onFieldChange(field.key, ($event.target as HTMLInputElement).value)"
            :placeholder="field.placeholder || '请输入'"
            @keyup.enter="$emit('search', modelValue)"
          />
        </div>
      </template>
    </div>
    <div class="search-actions">
      <BaseButton size="sm" variant="primary" @click="$emit('search', modelValue)">
        <BaseIcon name="search" :size="14" />
        搜索
      </BaseButton>
      <BaseButton size="sm" variant="ghost" @click="onReset">
        <BaseIcon name="rotate-ccw" :size="14" />
        重置
      </BaseButton>
      <button v-if="fields.length > 3" class="toggle-expand" @click="expanded = !expanded">
        {{ expanded ? '收起 ↑' : '展开 ↓' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import BaseButton from '../base/BaseButton.vue'
import BaseIcon from '../base/BaseIcon.vue'
import BaseSelect from '../base/BaseSelect.vue'

interface SearchField {
  key: string
  label: string
  type: 'input' | 'select' | 'date' | 'daterange'
  options?: { label: string; value: any }[]
  placeholder?: string
}

const props = defineProps<{
  fields: SearchField[]
  modelValue: Record<string, any>
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
  'search': [params: Record<string, any>]
  'reset': []
}>()

const expanded = ref(false)

const visibleFields = computed(() => {
  if (expanded.value || props.fields.length <= 3) return props.fields
  return props.fields.slice(0, 3)
})

function onFieldChange(key: string, value: any) {
  emit('update:modelValue', { ...props.modelValue, [key]: value })
}

function onReset() {
  const reset: Record<string, any> = {}
  props.fields.forEach(f => { reset[f.key] = undefined })
  emit('update:modelValue', reset)
  emit('reset')
}
</script>

<style scoped>
.base-search-form {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-base, #fff);
  border-radius: var(--radius-md);
  margin-bottom: 12px;
  gap: 12px;
  flex-wrap: wrap;
}

.search-fields {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  flex: 1;
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
  padding: 4px 8px;
  font-size: 13px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm, 4px);
  outline: none;
  height: var(--control-height-sm);
  box-sizing: border-box;
  width: 160px;
  background: var(--bg-base, #fff);
  color: var(--text-primary);
}
.search-input:focus {
  border-color: var(--accent-blue);
}

.search-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.toggle-expand {
  background: none;
  border: none;
  color: var(--accent-blue);
  font-size: 12px;
  cursor: pointer;
  padding: 4px 8px;
}
.toggle-expand:hover {
  text-decoration: underline;
}
</style>
