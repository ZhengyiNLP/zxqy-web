<template>
  <div class="settings-layout">
    <BaseSidebar
      :title="title"
      :active-key="modelValue"
      :groups="visibleGroups"
      :collapsible="true"
      @select="(key: string) => $emit('update:modelValue', key)"
    />
    <div class="settings-content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseSidebar from '@/components/layout/BaseSidebar.vue'
import type { NavGroup } from '@/components/layout/BaseSidebar.vue'

export interface SettingsNavItem {
  key: string
  label: string
  icon?: string
  visible?: boolean
}

export interface SettingsNavGroup {
  label: string
  items: SettingsNavItem[]
}

const props = withDefaults(defineProps<{
  title: string
  modelValue: string
  groups: SettingsNavGroup[]
}>(), {
  title: '设置',
})

defineEmits<{
  'update:modelValue': [value: string]
}>()

const visibleGroups = computed<NavGroup[]>(() => {
  return props.groups
    .map(group => ({
      ...group,
      items: group.items.filter(item => item.visible !== false)
    }))
    .filter(group => group.items.length > 0)
})
</script>

<style scoped>
.settings-layout {
  display: flex;
  height: 100%;
  background: var(--bg-deep);
  color: var(--text-primary);
}

.settings-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

.settings-content::-webkit-scrollbar {
  width: 6px;
}

.settings-content::-webkit-scrollbar-thumb {
  background: var(--border-default);
  border-radius: 3px;
}

.settings-content::-webkit-scrollbar-thumb:hover {
  background: var(--border-emphasis);
}
</style>
