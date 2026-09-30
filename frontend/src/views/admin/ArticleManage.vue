<template>
  <div>
    <el-card>
      <div class="toolbar">
        <el-select v-model="filters.categoryId" placeholder="栏目筛选" clearable @change="loadList" style="width:150px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-input v-model="filters.title" placeholder="标题搜索" clearable @clear="loadList" @keyup.enter="loadList" style="width:200px;margin-left:10px" />
        <el-button type="primary" @click="loadList" style="margin-left:10px">搜索</el-button>
        <el-button type="success" @click="openDialog()" style="margin-left:10px">新增新闻</el-button>
      </div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" show-overflow-tooltip min-width="200" />
        <el-table-column prop="categoryName" label="栏目" width="120" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{row}"><el-tag :type="row.status==='published'?'success':'info'" size="small">{{ row.status === 'published' ? '已发布' : '草稿' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="publishedAt" label="发布时间" width="160">
          <template #default="{row}">{{ row.publishedAt ? new Date(row.publishedAt).toLocaleString('zh-CN') : '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{row}">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" :type="row.status==='published'?'warning':'success'" @click="toggleStatus(row)">{{ row.status === 'published' ? '撤回' : '发布' }}</el-button>
            <el-button size="small" type="danger" @click="del(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination background layout="total, prev, pager, next" :total="total" v-model:current-page="page" :page-size="pageSize" @current-change="loadList" style="margin-top:16px" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑新闻' : '新增新闻'" width="700px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="栏目"><el-select v-model="form.category_id" placeholder="选择栏目"><el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" /></el-select></el-form-item>
        <el-form-item label="摘要"><el-input v-model="form.summary" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="正文"><el-input v-model="form.content" type="textarea" :rows="6" /></el-form-item>
        <el-form-item label="封面图"><el-input v-model="form.cover_image" placeholder="图片URL" /></el-form-item>
        <el-form-item label="来源"><el-input v-model="form.source" /></el-form-item>
        <el-form-item label="状态"><el-radio-group v-model="form.status"><el-radio value="draft">草稿</el-radio><el-radio value="published">发布</el-radio></el-radio-group></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/business'

const loading = ref(false)
const list = ref<any[]>([])
const categories = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const filters = reactive({ categoryId: undefined as any, title: '' })
const dialogVisible = ref(false)
const editing = ref<any>(null)
const form = reactive({ id: 0, title: '', category_id: 0, summary: '', content: '', cover_image: '', source: '', status: 'draft' })

async function loadList() {
  loading.value = true
  try {
    const res = await adminApi.getArticles({ page: page.value, pageSize: pageSize.value, categoryId: filters.categoryId, title: filters.title || undefined })
    list.value = res.data.list; total.value = res.data.total
  } catch {} finally { loading.value = false }
}

async function loadCategories() { const res = await adminApi.getCategories('article'); categories.value = res.data }

function openDialog(row?: any) {
  editing.value = row || null
  if (row) { Object.assign(form, row) } else { Object.assign(form, { id: 0, title: '', category_id: categories.value[0]?.id || 0, summary: '', content: '', cover_image: '', source: '', status: 'draft' }) }
  dialogVisible.value = true
}

async function save() {
  if (editing.value) { await adminApi.updateArticle(form.id, form) } else { await adminApi.createArticle(form) }
  dialogVisible.value = false; loadList()
}

async function del(row: any) { await ElMessageBox.confirm(`确定删除"${row.title}"?`, '提示', { type: 'warning' }); await adminApi.deleteArticle(row.id); loadList() }

async function toggleStatus(row: any) { await adminApi.updateArticleStatus(row.id, row.status === 'published' ? 'draft' : 'published'); loadList() }

onMounted(() => { loadCategories(); loadList() })
</script>

<style scoped>.toolbar { margin-bottom: 16px; display: flex; }</style>
