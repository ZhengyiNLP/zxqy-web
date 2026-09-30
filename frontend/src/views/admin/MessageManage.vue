<template>
  <div>
    <el-card>
      <div class="toolbar">
        <el-select v-model="filters.isRead" placeholder="状态筛选" clearable @change="loadList" style="width:120px">
          <el-option label="未读" :value="0" /><el-option label="已读" :value="1" />
        </el-select>
      </div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="email" label="邮箱" width="180" show-overflow-tooltip />
        <el-table-column prop="content" label="留言内容" show-overflow-tooltip min-width="200" />
        <el-table-column label="时间" width="160"><template #default="{row}">{{ row.createdAt ? new Date(row.createdAt).toLocaleString('zh-CN') : '' }}</template></el-table-column>
        <el-table-column label="状态" width="80"><template #default="{row}"><el-tag :type="row.isRead?'info':'danger'" size="small">{{ row.isRead ? '已读' : '未读' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{row}">
            <el-button size="small" @click="viewDetail(row)">查看</el-button>
            <el-button v-if="!row.isRead" size="small" type="success" @click="markRead(row)">标为已读</el-button>
            <el-button size="small" type="danger" @click="del(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination background layout="total, prev, pager, next" :total="total" v-model:current-page="page" :page-size="pageSize" @current-change="loadList" style="margin-top:16px" />
    </el-card>
    <el-dialog v-model="dialogVisible" title="留言详情" width="500px">
      <el-descriptions :column="1" border v-if="detail">
        <el-descriptions-item label="姓名">{{ detail.name }}</el-descriptions-item>
        <el-descriptions-item label="电话">{{ detail.phone }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ detail.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="内容">{{ detail.content }}</el-descriptions-item>
        <el-descriptions-item label="时间">{{ detail.createdAt ? new Date(detail.createdAt).toLocaleString('zh-CN') : '' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/business'

const loading = ref(false)
const list = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const filters = reactive({ isRead: undefined as any })
const dialogVisible = ref(false)
const detail = ref<any>(null)

async function loadList() { loading.value = true; try { const res = await adminApi.getMessages({ page: page.value, pageSize: pageSize.value, isRead: filters.isRead }); list.value = res.data.list; total.value = res.data.total } catch {} finally { loading.value = false } }
async function viewDetail(row: any) { const res = await adminApi.getMessage(row.id); detail.value = res.data; dialogVisible.value = true; if (!row.isRead) { await adminApi.markMessageRead(row.id); loadList() } }
async function markRead(row: any) { await adminApi.markMessageRead(row.id); loadList() }
async function del(row: any) { await ElMessageBox.confirm('确定删除该留言?', '提示', { type: 'warning' }); await adminApi.deleteMessage(row.id); loadList() }
onMounted(() => loadList())
</script>

<style scoped>.toolbar { margin-bottom: 16px; }</style>
