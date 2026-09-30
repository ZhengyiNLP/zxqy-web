<template>
  <div class="base-tabs">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      class="base-tab"
      :class="{ active: modelValue === tab.value }"
      @click="$emit('update:modelValue', tab.value)"
    >{{ tab.label }}</button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: string
  tabs: Array<{ value: string; label: string }>
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<style scoped>
.base-tabs { display: flex; gap: 4px; padding: 4px; background: var(--bg-elevated); border-radius: var(--radius-md); }
.base-tab { padding: 8px 16px; border: none; background: transparent; color: var(--text-secondary); font-size: 13px; font-weight: 500; cursor: pointer; border-radius: var(--radius-sm); transition: all 0.15s; font-family: inherit; }
.base-tab:hover { color: var(--text-primary); background: var(--bg-hover); }
.base-tab.active { background: var(--bg-base); color: var(--accent-blue); box-shadow: var(--shadow-sm); }
</style>
