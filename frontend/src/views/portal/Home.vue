<template>
  <div class="home-page">
    <!-- ===== 加载骨架（API 未返回前先渲染骨架，保证页面可用） ===== -->
    <div v-if="loading" class="home-skeleton">
      <div class="sk-hero">
        <el-skeleton-item variant="image" class="sk-hero-img" />
      </div>
      <div class="container sk-section">
        <el-skeleton-item variant="h1" class="sk-title" />
        <el-skeleton animated :rows="2" class="sk-rows" />
      </div>
      <div class="container sk-section">
        <el-skeleton-item variant="h1" class="sk-title" />
        <el-skeleton animated :rows="3" class="sk-rows" />
      </div>
    </div>

    <!-- ===== 加载失败提示（页面仍能独立渲染） ===== -->
    <div v-else-if="error" class="container error-wrap">
      <el-result icon="warning" title="首页数据加载失败" :sub-title="error">
        <template #extra>
          <el-button type="primary" @click="loadHome">重新加载</el-button>
        </template>
      </el-result>
    </div>

    <!-- ===== 正常内容 ===== -->
    <template v-else>
      <!-- 轮播图区域 -->
      <section class="hero-section">
        <el-carousel
          v-if="banners.length"
          class="hero-carousel"
          :interval="5000"
          arrow="hover"
          height="100%"
        >
          <el-carousel-item v-for="banner in banners" :key="banner.id">
            <div
              class="banner-item"
              :class="{ clickable: !!banner.linkUrl }"
              @click="onBannerClick(banner)"
            >
              <img
                v-if="banner.imageUrl"
                class="banner-img"
                :src="imgUrl(banner.imageUrl)"
                :alt="banner.title || '轮播图'"
              />
              <div
                v-if="banner.title"
                class="banner-caption"
                :class="{ centered: !banner.imageUrl }"
              >
                {{ banner.title }}
              </div>
            </div>
          </el-carousel-item>
        </el-carousel>
        <!-- 无轮播图时的默认展示：清新天蓝渐变 + 柔光光斑 + 巨字标语 -->
        <div v-else class="hero-placeholder">
          <div class="hero-slogan">
            <h1>聚焦企业 · 服务为您</h1>
            <p>专业的企业综合信息服务平台</p>
            <span class="hero-divider"></span>
          </div>
        </div>
      </section>

      <!-- 最新动态区域 -->
      <section class="section news-section">
        <div class="container">
          <div class="section-header">
            <h2 class="section-title">新闻动态</h2>
            <span class="section-en">News</span>
            <router-link class="more-link" to="/articles">查看更多 →</router-link>
          </div>
          <el-empty v-if="!latestArticles.length" description="暂无新闻动态" />
          <el-row v-else :gutter="24" class="news-grid">
            <el-col
              v-for="item in latestArticles.slice(0, 6)"
              :key="item.id"
              :xs="24"
              :sm="12"
            >
              <div class="news-card" @click="goArticle(item.id)">
                <div class="news-date-badge">
                  <span class="date-day">{{ dateParts(item.publishedAt).day }}</span>
                  <span class="date-ym">{{ dateParts(item.publishedAt).ym }}</span>
                </div>
                <div class="news-info">
                  <h3 class="news-title">{{ item.title }}</h3>
                  <p class="news-summary">{{ item.summary || '暂无摘要' }}</p>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </section>

      <!-- 产品展示区域 -->
      <section class="section product-section">
        <div class="container">
          <div class="section-header">
            <h2 class="section-title">产品展示</h2>
            <span class="section-en">Products</span>
            <router-link class="more-link" to="/products">查看更多 →</router-link>
          </div>
          <el-empty v-if="!recommendProducts.length" description="暂无推荐产品" />
          <el-row v-else :gutter="24" class="product-grid">
            <el-col
              v-for="p in recommendProducts"
              :key="p.id"
              :xs="12"
              :sm="8"
              :md="6"
            >
              <div class="product-card" @click="goProduct(p.id)">
                <div class="product-cover">
                  <img v-if="p.coverImage" :src="imgUrl(p.coverImage)" :alt="p.name" />
                  <div v-else class="cover-placeholder">
                    <span>{{ p.name.slice(0, 2) }}</span>
                  </div>
                </div>
                <div class="product-info">
                  <h3 class="product-name">{{ p.name }}</h3>
                  <p class="product-desc">{{ p.shortDesc || '—' }}</p>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { portalApi } from '@/api/business'
/** 轮播图项 */
interface BannerItem {
  id: number
  title?: string
  imageUrl: string
  linkUrl?: string
}
/** 新闻简要信息 */
interface ArticleBrief {
  id: number
  title: string
  summary?: string | null
  coverImage?: string | null
  publishedAt?: string | null
}
/** 产品简要信息 */
interface ProductBrief {
  id: number
  name: string
  shortDesc?: string | null
  coverImage?: string | null
}
/** 首页聚合数据 */
interface HomeData {
  banners?: BannerItem[]
  latestArticles?: ArticleBrief[]
  recommendProducts?: ProductBrief[]
  aboutSummary?: string
}

const router = useRouter()

const loading = ref(true)
const error = ref('')
const home = ref<HomeData>({})

/** 图片相对路径加 /api 前缀 */
const imgUrl = (url: string) => (url ? '/api' + url : '')

/** 各区块数据（缺省为空，保证页面可独立渲染） */
const banners = computed(() => home.value.banners || [])
const latestArticles = computed(() => home.value.latestArticles || [])
const recommendProducts = computed(() => home.value.recommendProducts || [])

/** 日期拆分为「日」和「年-月」，用于新闻卡片角标展示 */
const dateParts = (d?: string | null) => {
  if (!d) return { day: '--', ym: '' }
  const dt = new Date(d)
  if (Number.isNaN(dt.getTime())) return { day: '--', ym: '' }
  return {
    day: String(dt.getDate()).padStart(2, '0'),
    ym: `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}`,
  }
}

/** 轮播图点击跳转：内站路由跳转，外链新窗口打开 */
const onBannerClick = (banner: BannerItem) => {
  if (!banner.linkUrl) return
  if (/^https?:\/\//i.test(banner.linkUrl)) {
    window.open(banner.linkUrl, '_blank', 'noopener,noreferrer')
  } else {
    router.push(banner.linkUrl)
  }
}

const goArticle = (id: number) => router.push(`/articles/${id}`)
const goProduct = (id: number) => router.push(`/products/${id}`)

/** 加载首页聚合数据 */
const loadHome = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await portalApi.getHome()
    home.value = (res.data as HomeData) || {}
  } catch (e: any) {
    error.value = e?.message || '网络异常，请检查网络后重试'
  } finally {
    loading.value = false
  }
}

onMounted(loadHome)
</script>

<style scoped>
.home-page {
  background: var(--bg-deep, #f7f8fa);
}

/* 通用容器与区块 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}
.section {
  padding: 60px 0;
}
.section-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 32px;
}
.section-title {
  position: relative;
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary, #1f2329);
  padding-left: 14px;
  margin: 0;
}
.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 5px;
  height: 22px;
  border-radius: 3px;
  background: linear-gradient(180deg, #2563eb, #60a5fa);
}
.section-en {
  font-size: 13px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: var(--text-tertiary, #8f959e);
}
.more-link {
  margin-left: auto;
  font-size: 13px;
  color: var(--text-secondary, #646a73);
  text-decoration: none;
  transition: color 0.2s;
}
.more-link:hover {
  color: var(--accent-blue, #3b82f6);
}

/* ===== 骨架屏 ===== */
.sk-hero {
  height: 440px;
}
.sk-hero-img {
  width: 100%;
  height: 100%;
  border-radius: 0;
}
.sk-section {
  padding: 40px 16px;
}
.sk-title {
  width: 180px;
  height: 28px;
  margin-bottom: 20px;
}
.sk-rows {
  margin-top: 8px;
}
.error-wrap {
  padding: 80px 16px;
}

/* ===== 轮播图 ===== */
.hero-carousel {
  height: 440px;
}
/* 轮播指示器：改为简约短横线样式（当前页更长更实，其余半透明细线） */
.hero-carousel :deep(.el-carousel__indicators) {
  gap: 10px;
}
.hero-carousel :deep(.el-carousel__indicator) {
  padding: 12px 4px;
}
.hero-carousel :deep(.el-carousel__indicator .el-carousel__button) {
  width: 26px;
  height: 3px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.45);
  opacity: 1;
}
.hero-carousel :deep(.el-carousel__indicator.is-active .el-carousel__button) {
  width: 40px;
  background: #ffffff;
}
/* 覆盖 el-carousel 默认 300px 高度，改为随外层容器自适应（响应式） */
.hero-carousel :deep(.el-carousel__container) {
  height: 100% !important;
}
.banner-item {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  /* 无图 banner 底色：清新天蓝渐变（与 hero-placeholder 一致） */
  background: linear-gradient(125deg, #d9ecfb 0%, #aad6f6 34%, #74baf1 68%, #4fa8e9 100%);
}
.banner-item::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 640px 380px at 76% 18%, rgba(255, 255, 255, 0.55) 0%, rgba(255, 255, 255, 0) 62%),
    radial-gradient(ellipse 520px 320px at 12% 88%, rgba(255, 255, 255, 0.34) 0%, rgba(255, 255, 255, 0) 60%);
}
.banner-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  position: relative;
  z-index: 1;
}
.banner-item.clickable {
  cursor: pointer;
}
.banner-caption {
  position: absolute;
  left: 6%;
  bottom: 22%;
  max-width: 88%;
  z-index: 2;
  color: #ffffff;
  font-size: clamp(20px, 3.2vw, 34px);
  font-weight: 700;
  line-height: 1.4;
  overflow-wrap: break-word;
  text-shadow: 0 2px 14px rgba(30, 100, 170, 0.45);
}
.banner-caption.centered {
  left: 0;
  right: 0;
  bottom: auto;
  top: 50%;
  transform: translateY(-50%);
  text-align: center;
}
/* 无轮播数据时的默认展示：清新天蓝渐变 + 柔光光斑 + 居中巨字 */
.hero-placeholder {
  position: relative;
  height: 440px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  text-align: center;
  overflow: hidden;
  background: linear-gradient(125deg, #d9ecfb 0%, #aad6f6 34%, #74baf1 68%, #4fa8e9 100%);
}
/* 弥散柔光：大范围光雾营造天空感，不用 blur 避免发脏 */
.hero-placeholder::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(ellipse 640px 380px at 76% 18%, rgba(255, 255, 255, 0.55) 0%, rgba(255, 255, 255, 0) 62%),
    radial-gradient(ellipse 520px 320px at 12% 88%, rgba(255, 255, 255, 0.34) 0%, rgba(255, 255, 255, 0) 60%);
}
.hero-slogan {
  position: relative;
  z-index: 1;
  padding: 0 16px;
}
.hero-placeholder h1 {
  font-size: 40px;
  font-weight: 700;
  letter-spacing: 6px;
  margin: 0 0 14px;
  color: #ffffff;
  text-shadow: 0 2px 18px rgba(30, 100, 170, 0.45);
}
.hero-placeholder p {
  font-size: 16px;
  opacity: 0.95;
  letter-spacing: 3px;
  margin: 0;
  color: #ffffff;
  text-shadow: 0 1px 8px rgba(30, 100, 170, 0.35);
}
.hero-divider {
  display: block;
  width: 56px;
  height: 3px;
  margin: 22px auto 0;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 1px 6px rgba(30, 100, 170, 0.3);
}

/* ===== 新闻动态 ===== */
.news-section {
  background: var(--bg-deep, #f7f8fa);
}
.news-grid :deep(.el-col) {
  margin-bottom: 20px;
}
.news-card {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  height: 100%;
  padding: 20px;
  background: #ffffff;
  border: 1px solid var(--border-subtle, #e5e6eb);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s;
}
.news-card:hover {
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0, 0, 0, 0.08));
  transform: translateY(-3px);
}
.news-date-badge {
  flex-shrink: 0;
  width: 64px;
  height: 64px;
  border-radius: 10px;
  background: rgba(59, 130, 246, 0.1);
  color: var(--accent-blue, #3b82f6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1px;
}
.date-day {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.1;
}
.date-ym {
  font-size: 11px;
  opacity: 0.75;
}
.news-info {
  flex: 1;
  min-width: 0;
}
.news-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #1f2329);
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color 0.2s;
}
.news-card:hover .news-title {
  color: var(--accent-blue, #3b82f6);
}
.news-summary {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-tertiary, #8f959e);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* ===== 产品精选 ===== */
.product-section {
  background: #ffffff;
}
.product-grid :deep(.el-col) {
  margin-bottom: 24px;
}
.product-card {
  background: #ffffff;
  border: 1px solid var(--border-subtle, #e5e6eb);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s;
}
.product-card:hover {
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0, 0, 0, 0.08));
  transform: translateY(-4px);
}
.product-cover {
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: var(--bg-elevated, #f0f2f5);
}
.product-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.35s;
}
.product-card:hover .product-cover img {
  transform: scale(1.05);
}
.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(96, 165, 250, 0.18));
}
.cover-placeholder span {
  font-size: 28px;
  font-weight: 700;
  color: var(--accent-blue, #3b82f6);
  opacity: 0.65;
}
.product-info {
  padding: 14px 16px;
}
.product-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #1f2329);
  margin: 0 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.product-card:hover .product-name {
  color: var(--accent-blue, #3b82f6);
}
.product-desc {
  font-size: 12px;
  color: var(--text-tertiary, #8f959e);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .section {
    padding: 40px 0;
  }
  .section-title {
    font-size: 21px;
  }
  .hero-carousel,
  .hero-placeholder,
  .sk-hero {
    height: 260px;
  }
  .banner-caption {
    font-size: 20px;
  }
  .hero-placeholder h1 {
    font-size: 22px;
    letter-spacing: 3px;
  }
  .hero-placeholder p {
    font-size: 13px;
  }
  .hero-divider {
    width: 40px;
    margin-top: 14px;
  }
  .news-card {
    padding: 14px;
    gap: 12px;
  }
  .news-date-badge {
    width: 52px;
    height: 52px;
  }
  .date-day {
    font-size: 18px;
  }
  .hero-carousel :deep(.el-carousel__indicator .el-carousel__button) {
    width: 18px;
  }
  .hero-carousel :deep(.el-carousel__indicator.is-active .el-carousel__button) {
    width: 28px;
  }
}
</style>
