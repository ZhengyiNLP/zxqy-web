<template>
  <div>
    <el-card v-loading="loading">
      <el-form :model="form" label-width="120px" style="max-width:600px">
        <el-form-item label="网站名称"><el-input v-model="form.site_name" /></el-form-item>
        <el-form-item label="网站Logo URL"><el-input v-model="form.site_logo" /></el-form-item>
        <el-form-item label="ICP备案号"><el-input v-model="form.icp" /></el-form-item>
        <el-form-item label="首页动态条数"><el-input-number v-model="form.home_article_count" :min="1" :max="20" /></el-form-item>
        <el-form-item label="首页产品条数"><el-input-number v-model="form.home_product_count" :min="1" :max="20" /></el-form-item>
        <el-form-item><el-button type="primary" @click="save">保存配置</el-button></el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { adminApi } from '@/api/business'

const loading = ref(false)
const form = reactive({ site_name: '', site_logo: '', icp: '', home_article_count: 6, home_product_count: 8 })

onMounted(async () => {
  loading.value = true
  try {
    const res = await adminApi.getSiteConfig()
    const data = res.data
    form.site_name = data.site_name || ''
    form.site_logo = data.site_logo || ''
    form.icp = data.icp || ''
    form.home_article_count = parseInt(data.home_article_count) || 6
    form.home_product_count = parseInt(data.home_product_count) || 8
  } catch {} finally { loading.value = false }
})

async function save() {
  await adminApi.saveSiteConfig({
    site_name: form.site_name,
    site_logo: form.site_logo,
    icp: form.icp,
    home_article_count: String(form.home_article_count),
    home_product_count: String(form.home_product_count),
  })
}
</script>
