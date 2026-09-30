<template>
  <div class="product-detail" v-loading="loading">
    <div class="container">
      <div class="back-bar">
        <el-button @click="$router.push('/products')" :icon="ArrowLeft">返回列表</el-button>
      </div>
      <el-card v-if="product">
        <div class="product-main">
          <div class="gallery">
            <el-image :src="imgUrl(mainImage)" fit="contain" class="main-image" :preview-src-list="allImages.map(imgUrl)" :preview-teleported="true">
              <template #error><div class="img-placeholder">暂无图片</div></template>
            </el-image>
            <div class="thumbs" v-if="allImages.length > 1">
              <div v-for="(img, i) in allImages" :key="i" class="thumb" :class="{ active: mainImage === img }" @click="mainImage = img">
                <el-image :src="imgUrl(img)" fit="cover" />
              </div>
            </div>
          </div>
          <div class="info">
            <h1 class="name">{{ product.name }}</h1>
            <p v-if="product.shortDesc" class="short-desc">{{ product.shortDesc }}</p>
            <p v-if="product.categoryName" class="category">分类：{{ product.categoryName }}</p>
            <div v-if="parsedParams && parsedParams.length" class="params-table">
              <h3>产品参数</h3>
              <el-descriptions :column="1" border>
                <el-descriptions-item v-for="p in parsedParams" :key="p.key" :label="p.key">{{ p.value }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </div>
        <el-divider />
        <div class="description">
          <h3>产品详情</h3>
          <div class="content" v-html="product.description"></div>
        </div>
      </el-card>
      <el-empty v-if="!loading && !product" description="产品不存在" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { portalApi } from '@/api/business'

const route = useRoute()
const loading = ref(true)
const product = ref<any>(null)
const mainImage = ref('')

const allImages = computed(() => {
  if (!product.value) return []
  const imgs = [...(product.value.images || [])]
  if (product.value.coverImage && !imgs.includes(product.value.coverImage)) {
    imgs.unshift(product.value.coverImage)
  }
  return imgs
})

const parsedParams = computed(() => {
  if (!product.value?.params) return []
  try { return JSON.parse(product.value.params) } catch { return [] }
})

const imgUrl = (url: string) => url ? '/api' + url : ''

async function loadProduct(id: number) {
  loading.value = true
  try {
    const res = await portalApi.getProductDetail(id)
    product.value = res.data
    mainImage.value = res.data.coverImage || (res.data.images?.[0] || '')
  } catch { product.value = null }
  finally { loading.value = false }
}

watch(() => route.params.id, (id) => {
  if (id) loadProduct(Number(id))
}, { immediate: true })
</script>

<style scoped>
.product-detail { padding: 20px 0; min-height: 60vh; }
.container { max-width: 1000px; margin: 0 auto; padding: 0 16px; }
.back-bar { margin-bottom: 16px; }
.product-main { display: flex; gap: 30px; }
.gallery { width: 400px; flex-shrink: 0; }
.main-image { width: 400px; height: 400px; border: 1px solid #eee; }
.img-placeholder { display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; background: #f5f5f5; color: #ccc; }
.thumbs { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.thumb { width: 60px; height: 60px; border: 2px solid #eee; cursor: pointer; }
.thumb.active { border-color: #409eff; }
.thumb .el-image { width: 100%; height: 100%; }
.info { flex: 1; }
.name { font-size: 24px; color: #333; margin: 0 0 12px; }
.short-desc { font-size: 15px; color: #666; margin: 0 0 10px; }
.category { font-size: 14px; color: #999; margin: 0 0 20px; }
.params-table { margin-top: 20px; }
.params-table h3 { font-size: 16px; margin: 0 0 10px; }
.description { margin-top: 10px; }
.description h3 { font-size: 18px; margin: 0 0 16px; }
.content { line-height: 1.8; color: #555; }
.content :deep(img) { max-width: 100%; height: auto; }
@media (max-width: 768px) {
  .product-main { flex-direction: column; }
  .gallery { width: 100%; }
  .main-image { width: 100%; height: 300px; }
}
</style>
