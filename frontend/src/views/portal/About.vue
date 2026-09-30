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
import { ref, onMounted } from 'vue'
import { portalApi } from '@/api/business'

/** 固定加载"关于我们"单页内容（与 Culture.vue 保持一致的硬编码模式） */
const PAGE_KEY = 'about'
const loading = ref(false)
const pageData = ref<any>(null)

onMounted(async () => {
  loading.value = true
  try {
    const res = await portalApi.getPage(PAGE_KEY)
    pageData.value = res.data
  } catch { pageData.value = null }
  finally { loading.value = false }
})
</script>

<style scoped>
.page-content { padding: 20px 0; min-height: 60vh; }
.container { max-width: 900px; margin: 0 auto; padding: 0 16px; }
.title { font-size: 26px; color: #333; margin: 0 0 24px; }
.content { line-height: 1.8; color: #555; }
.content :deep(img) { max-width: 100%; height: auto; }
</style>
