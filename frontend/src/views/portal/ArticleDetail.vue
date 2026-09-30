<template>
  <div class="article-detail" v-loading="loading">
    <div class="container">
      <div class="back-bar">
        <el-button @click="$router.push('/articles')" :icon="ArrowLeft">返回列表</el-button>
      </div>
      <el-card v-if="article">
        <h1 class="title">{{ article.title }}</h1>
        <div class="meta">
          <span>发布时间：{{ formatDate(article.publishedAt) }}</span>
          <span v-if="article.source">来源：{{ article.source }}</span>
          <span>浏览量：{{ article.viewCount }}</span>
          <span v-if="article.categoryName">栏目：{{ article.categoryName }}</span>
        </div>
        <div class="content" v-html="article.content"></div>
        <div class="nav-bar">
          <el-button v-if="article.prevArticle && article.prevArticle.id" @click="goArticle(article.prevArticle.id)">上一篇：{{ article.prevArticle.title }}</el-button>
          <el-button v-if="article.nextArticle && article.nextArticle.id" @click="goArticle(article.nextArticle.id)">下一篇：{{ article.nextArticle.title }}</el-button>
        </div>
      </el-card>
      <el-empty v-if="!loading && !article" description="文章不存在" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { portalApi } from '@/api/business'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const article = ref<any>(null)

async function loadArticle(id: number) {
  loading.value = true
  try {
    const res = await portalApi.getArticleDetail(id)
    article.value = res.data
  } catch { article.value = null }
  finally { loading.value = false }
}

function goArticle(id: number) {
  router.push(`/articles/${id}`)
}

function formatDate(date?: string) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN')
}

watch(() => route.params.id, (id) => {
  if (id) loadArticle(Number(id))
}, { immediate: true })
</script>

<style scoped>
.article-detail { padding: 20px 0; min-height: 60vh; }
.container { max-width: 900px; margin: 0 auto; padding: 0 16px; }
.back-bar { margin-bottom: 16px; }
.title { font-size: 26px; color: #333; margin: 0 0 16px; }
.meta { display: flex; gap: 20px; font-size: 14px; color: #999; margin-bottom: 24px; flex-wrap: wrap; }
.content { line-height: 1.8; color: #555; }
.content :deep(img) { max-width: 100%; height: auto; }
.nav-bar { display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; flex-wrap: wrap; gap: 10px; }
@media (max-width: 768px) {
  .meta { gap: 8px; }
  .title { font-size: 20px; }
}
</style>
