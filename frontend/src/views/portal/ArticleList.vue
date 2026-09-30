<template>
  <div class="article-list-page">
    <!-- 主体内容（与其他页面统一的简洁白底风格，无蓝色横幅） -->
    <div class="container page-body">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">新闻动态</h1>
        <p class="page-sub">了解企业最新资讯与行业动态</p>
      </div>

      <!-- 栏目分类筛选：全部 + 各分类 -->
      <div class="category-bar">
        <button
          type="button"
          class="cat-btn"
          :class="{ active: activeCategoryId === null }"
          @click="onCategoryChange(null)"
        >
          全部
        </button>
        <button
          v-for="c in categories"
          :key="c.id"
          type="button"
          class="cat-btn"
          :class="{ active: activeCategoryId === c.id }"
          @click="onCategoryChange(c.id)"
        >
          {{ c.name }}
        </button>
      </div>

      <!-- 列表骨架 -->
      <div v-if="loading" class="list-skeleton">
        <div v-for="i in 4" :key="i" class="sk-row">
          <el-skeleton-item variant="image" class="sk-cover" />
          <div class="sk-col">
            <el-skeleton-item variant="h3" class="sk-line-title" />
            <el-skeleton-item variant="text" class="sk-line" />
            <el-skeleton-item variant="text" class="sk-line short" />
          </div>
        </div>
      </div>

      <template v-else>
        <!-- 加载失败 -->
        <div v-if="error" class="error-wrap">
          <el-result icon="warning" title="新闻列表加载失败" :sub-title="error">
            <template #extra>
              <el-button type="primary" @click="reload">重新加载</el-button>
            </template>
          </el-result>
        </div>

        <!-- 暂无数据 -->
        <el-empty v-else-if="!articles.length" description="暂无相关新闻" />

        <!-- 新闻列表 -->
        <transition-group v-else name="list" tag="div" class="article-list">
          <article
            v-for="item in articles"
            :key="item.id"
            class="article-card"
            @click="goDetail(item.id)"
          >
            <div class="article-cover">
              <img v-if="item.coverImage" :src="imgUrl(item.coverImage)" :alt="item.title" />
              <div v-else class="cover-fallback">
                <span>{{ (item.title || '').slice(0, 2) }}</span>
              </div>
            </div>
            <div class="article-main">
              <div class="article-meta-top">
                <el-tag v-if="item.categoryName" size="small" effect="plain">
                  {{ item.categoryName }}
                </el-tag>
                <span class="article-date">{{ formatDate(item.publishedAt) }}</span>
              </div>
              <h2 class="article-title">{{ item.title }}</h2>
              <p class="article-summary">{{ item.summary || '暂无摘要' }}</p>
              <span class="read-more">阅读全文 →</span>
            </div>
          </article>
        </transition-group>

        <!-- 分页 -->
        <div v-if="!error && total > pageSize" class="pagination-wrap">
          <el-pagination
            background
            layout="total, prev, pager, next"
            :total="total"
            :page-size="pageSize"
            :current-page="page"
            @current-change="onPageChange"
          />
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { portalApi } from '@/api/business'

/** 栏目分类 */
interface CategoryItem {
  id: number
  name: string
  type?: string
}
/** 新闻列表项 */
interface ArticleItem {
  id: number
  title: string
  summary?: string | null
  coverImage?: string | null
  categoryName?: string | null
  publishedAt?: string | null
}
/** 分页数据结构 */
interface PageData<T> {
  list: T[]
  total: number
  page: number
  pageSize: number
}

const router = useRouter()

/** 图片相对路径加 /api 前缀 */
const imgUrl = (url: string) => (url ? '/api' + url : '')

/** 日期格式化 */
const formatDate = (date?: string | null) =>
  date ? new Date(date).toLocaleDateString('zh-CN') : ''

/** 每页条数 */
const pageSize = 10

const categories = ref<CategoryItem[]>([])
const activeCategoryId = ref<number | null>(null)
const articles = ref<ArticleItem[]>([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)
const error = ref('')

/** 加载新闻分类（加载失败则仅显示「全部」，不影响列表渲染） */
const loadCategories = async () => {
  try {
    const res = await portalApi.getCategories('article')
    categories.value = (res.data as CategoryItem[]) || []
  } catch {
    categories.value = []
  }
}

/** 加载新闻列表 */
const loadArticles = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await portalApi.getArticles({
      page: page.value,
      pageSize,
      categoryId: activeCategoryId.value ?? undefined,
    })
    const data = res.data as PageData<ArticleItem>
    if (!data || !Array.isArray(data.list)) {
      throw new Error('数据加载失败')
    }
    articles.value = data.list
    total.value = data.total || 0
  } catch (e: any) {
    articles.value = []
    total.value = 0
    error.value = e?.message || '加载失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

/** 切换分类：重置页码并重新加载 */
const onCategoryChange = (id: number | null) => {
  if (activeCategoryId.value === id) return
  activeCategoryId.value = id
  page.value = 1
  loadArticles()
}

/** 切换分页并回到页面顶部 */
const onPageChange = (p: number) => {
  page.value = p
  loadArticles()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

/** 重新加载（分类 + 列表） */
const reload = () => {
  loadCategories()
  loadArticles()
}

const goDetail = (id: number) => router.push(`/articles/${id}`)

onMounted(() => {
  loadCategories()
  loadArticles()
})
</script>

<style scoped>
/* ===== 页面标题（与产品展示/关于我们页面风格统一） ===== */
.page-header {
  padding: 36px 0 4px;
}
.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #1f2329);
  margin: 0 0 8px;
}
.page-sub {
  font-size: 14px;
  color: var(--text-tertiary, #8f959e);
  margin: 0;
}
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

.page-body {
  padding: 0 16px 72px;
}

/* ===== 分类筛选条 ===== */
.category-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 24px;
  padding: 16px;
  background: #ffffff;
  border: 1px solid var(--border-subtle, #e5e6eb);
  border-radius: 12px;
}
.cat-btn {
  padding: 8px 20px;
  border: 1px solid var(--border-default, #dee0e3);
  border-radius: 999px;
  background: #ffffff;
  color: var(--text-secondary, #646a73);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.cat-btn:hover {
  color: var(--accent-blue, #3b82f6);
  border-color: var(--accent-blue, #3b82f6);
}
.cat-btn.active {
  background: var(--accent-blue, #3b82f6);
  border-color: var(--accent-blue, #3b82f6);
  color: #ffffff;
  font-weight: 500;
}

/* ===== 列表骨架 ===== */
.list-skeleton .sk-row {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: #ffffff;
  border: 1px solid var(--border-subtle, #e5e6eb);
  border-radius: 12px;
  margin-bottom: 16px;
}
.sk-cover {
  width: 200px;
  height: 130px;
  border-radius: 8px;
  flex-shrink: 0;
}
.sk-col {
  flex: 1;
  padding-top: 6px;
}
.sk-line-title {
  width: 55%;
  height: 20px;
  margin-bottom: 14px;
}
.sk-line {
  width: 92%;
  height: 14px;
  margin-bottom: 10px;
}
.sk-line.short {
  width: 40%;
}

/* ===== 新闻卡片列表 ===== */
.article-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.article-card {
  display: flex;
  gap: 20px;
  padding: 20px;
  background: #ffffff;
  border: 1px solid var(--border-subtle, #e5e6eb);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s;
}
.article-card:hover {
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0, 0, 0, 0.08));
  transform: translateY(-2px);
}
.article-cover {
  flex-shrink: 0;
  width: 220px;
  aspect-ratio: 16 / 10;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-elevated, #f0f2f5);
}
.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.35s;
}
.article-card:hover .article-cover img {
  transform: scale(1.05);
}
/* 无封面时显示标题字样的色块 */
.cover-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(96, 165, 250, 0.18));
}
.cover-fallback span {
  font-size: 30px;
  font-weight: 700;
  color: var(--accent-blue, #3b82f6);
  opacity: 0.65;
}
.article-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.article-meta-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.article-date {
  font-size: 13px;
  color: var(--text-tertiary, #8f959e);
}
.article-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #1f2329);
  margin: 0 0 10px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color 0.2s;
}
.article-card:hover .article-title {
  color: var(--accent-blue, #3b82f6);
}
.article-summary {
  flex: 1;
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary, #646a73);
  margin: 0 0 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.read-more {
  align-self: flex-start;
  font-size: 13px;
  color: var(--text-tertiary, #8f959e);
  transition: color 0.2s;
}
.article-card:hover .read-more {
  color: var(--accent-blue, #3b82f6);
}

/* 列表过渡动画 */
.list-enter-active,
.list-leave-active {
  transition: all 0.25s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* ===== 分页 ===== */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

/* ===== 错误 / 空态 ===== */
.error-wrap {
  padding: 30px 0;
}

/* ===== 响应式：移动端封面图缩小、卡片纵向排列 ===== */
@media (max-width: 768px) {
  .page-header {
    padding: 20px 0 0;
  }
  .page-title {
    font-size: 22px;
  }
  .article-cover {
    width: 120px;
  }
  .article-card {
    padding: 14px;
    gap: 14px;
  }
  .article-title {
    font-size: 15px;
  }
  .article-summary {
    font-size: 13px;
    -webkit-line-clamp: 2;
    line-clamp: 2;
  }
  .read-more {
    display: none;
  }
  .sk-cover {
    width: 110px;
    height: 74px;
  }
}
@media (max-width: 480px) {
  .article-card {
    flex-direction: column;
  }
  .article-cover {
    width: 100%;
  }
}
</style>
