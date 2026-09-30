<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :xs="12" :sm="6" v-for="card in statCards" :key="card.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-card class="recent-card" v-loading="loading">
      <template #header><span>最近留言</span></template>
      <div v-if="messages.length === 0" class="empty-text">暂无留言</div>
      <div v-for="msg in messages" :key="msg.id" class="msg-item">
        <div class="msg-header">
          <span class="msg-name">{{ msg.name }}</span>
          <span class="msg-phone">{{ msg.phone }}</span>
          <el-tag :type="msg.isRead ? 'info' : 'danger'" size="small">{{ msg.isRead ? '已读' : '未读' }}</el-tag>
          <span class="msg-time">{{ formatTime(msg.createdAt) }}</span>
        </div>
        <div class="msg-content">{{ msg.content }}</div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/business'

const loading = ref(false)
const messages = ref<any[]>([])

const statCards = ref([
  { label: '新闻总数', value: 0 },
  { label: '产品总数', value: 0 },
  { label: '未读留言', value: 0 },
  { label: '轮播图数', value: 0 },
])

function formatTime(t?: string) { return t ? new Date(t).toLocaleString('zh-CN') : '' }

onMounted(async () => {
  loading.value = true
  try {
    const res = await adminApi.getDashboard()
    const data = res.data
    messages.value = data.recentMessages || []
    statCards.value[0].value = data.articleCount
    statCards.value[1].value = data.productCount
    statCards.value[2].value = data.unreadMessageCount
    statCards.value[3].value = data.bannerCount
  } catch {}
  finally { loading.value = false }
})
</script>

<style scoped>
.stat-card { text-align: center; margin-bottom: 16px; }
.stat-value { font-size: 32px; font-weight: bold; color: #409eff; }
.stat-label { font-size: 14px; color: #999; margin-top: 4px; }
.recent-card { margin-top: 10px; }
.empty-text { color: #999; text-align: center; padding: 20px; }
.msg-item { padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
.msg-item:last-child { border-bottom: none; }
.msg-header { display: flex; align-items: center; gap: 12px; margin-bottom: 6px; }
.msg-name { font-weight: bold; font-size: 14px; }
.msg-phone { color: #666; font-size: 13px; }
.msg-time { color: #999; font-size: 12px; margin-left: auto; }
.msg-content { font-size: 14px; color: #555; line-height: 1.6; }
</style>
