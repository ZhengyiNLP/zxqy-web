<template>
  <div class="page-content" v-loading="loading">
    <div class="container">
      <el-card v-if="pageData">
        <h1 class="title">{{ pageData.title }}</h1>
        <div class="content" v-html="pageData.content"></div>
      </el-card>
      <el-empty v-if="!loading && !pageData" description="页面不存在" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { portalApi } from '@/api/business'

const props = defineProps<{ pageKey: string }>()
const loading = ref(false)
const pageData = ref<any>(null)

async function loadPage() {
  loading.value = true
  try {
    const res = await portalApi.getPage(props.pageKey)
    pageData.value = res.data
  } catch { pageData.value = null }
  finally { loading.value = false }
}

watch(() => props.pageKey, () => loadPage(), { immediate: true })
</script>

<style scoped>
.page-content { padding: 20px 0; min-height: 60vh; }
.container { max-width: 900px; margin: 0 auto; padding: 0 16px; }
.title { font-size: 26px; color: #333; margin: 0 0 24px; }
.content { line-height: 1.8; color: #555; }
.content :deep(img) { max-width: 100%; height: auto; }
</style>
