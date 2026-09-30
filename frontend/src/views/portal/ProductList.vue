<template>
  <div class="product-list">
    <div class="container">
      <h1 class="page-title">产品展示</h1>
      <div class="filter-bar">
        <el-radio-group v-model="activeCategory" @change="loadProducts">
          <el-radio-button :value="0">全部</el-radio-button>
          <el-radio-button v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</el-radio-button>
        </el-radio-group>
      </div>
      <el-row :gutter="20" v-loading="loading">
        <el-col :xs="12" :sm="8" :md="6" v-for="p in products" :key="p.id" class="product-col">
          <el-card shadow="hover" class="product-card" @click="$router.push(`/products/${p.id}`)">
            <div class="product-img">
              <el-image :src="imgUrl(p.coverImage)" fit="cover" lazy>
                <template #error><div class="img-placeholder">暂无图片</div></template>
              </el-image>
            </div>
            <div class="product-info">
              <h3 class="name">{{ p.name }}</h3>
              <p class="desc">{{ p.shortDesc }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-empty v-if="!loading && products.length === 0" description="暂无产品" />
      <div class="pagination" v-if="total > 0">
        <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize" v-model:current-page="page" @current-change="loadProducts" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { portalApi } from '@/api/business'

const categories = ref<any[]>([])
const products = ref<any[]>([])
const loading = ref(false)
const activeCategory = ref(0)
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)

const imgUrl = (url: string) => url ? '/api' + url : ''

async function loadCategories() {
  const res = await portalApi.getCategories('product')
  categories.value = res.data
}

async function loadProducts() {
  loading.value = true
  try {
    const res = await portalApi.getProducts({
      page: page.value, pageSize: pageSize.value,
      categoryId: activeCategory.value || undefined,
    })
    products.value = res.data.list
    total.value = res.data.total
  } catch { products.value = [] }
  finally { loading.value = false }
}

onMounted(() => {
  loadCategories()
  loadProducts()
})
</script>

<style scoped>
.product-list { padding: 20px 0; }
.container { max-width: 1200px; margin: 0 auto; padding: 0 16px; }
.page-title { font-size: 24px; color: #333; margin: 0 0 20px; }
.filter-bar { margin-bottom: 24px; }
.product-col { margin-bottom: 20px; }
.product-card { cursor: pointer; transition: transform 0.2s; }
.product-card:hover { transform: translateY(-4px); }
.product-img { height: 200px; overflow: hidden; }
.product-img .el-image { width: 100%; height: 100%; }
.img-placeholder { display: flex; align-items: center; justify-content: center; height: 200px; background: #f5f5f5; color: #ccc; font-size: 14px; }
.product-info { padding: 8px 0; }
.name { font-size: 16px; color: #333; margin: 0 0 6px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.desc { font-size: 13px; color: #999; margin: 0; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
.pagination { text-align: center; margin-top: 30px; }
</style>
