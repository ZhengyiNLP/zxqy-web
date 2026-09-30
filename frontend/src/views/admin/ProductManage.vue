<template>
  <div>
    <el-card>
      <div class="toolbar">
        <el-select v-model="filters.categoryId" placeholder="分类筛选" clearable @change="loadList" style="width:150px">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-input v-model="filters.name" placeholder="名称搜索" clearable @keyup.enter="loadList" style="width:200px;margin-left:10px" />
        <el-button type="primary" @click="loadList" style="margin-left:10px">搜索</el-button>
        <el-button type="success" @click="openDialog()" style="margin-left:10px">新增产品</el-button>
      </div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="name" label="名称" show-overflow-tooltip min-width="150" />
        <el-table-column prop="categoryName" label="分类" width="100" />
        <el-table-column label="推荐" width="80"><template #default="{row}"><el-tag :type="row.isRecommend?'warning':'info'" size="small">{{ row.isRecommend ? '是' : '否' }}</el-tag></template></el-table-column>
        <el-table-column label="状态" width="80"><template #default="{row}"><el-tag :type="row.status?'success':'danger'" size="small">{{ row.status ? '上架' : '下架' }}</el-tag></template></el-table-column>
        <el-table-column prop="sortOrder" label="排序" width="80" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{row}">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="del(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination background layout="total, prev, pager, next" :total="total" v-model:current-page="page" :page-size="pageSize" @current-change="loadList" style="margin-top:16px" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑产品' : '新增产品'" width="700px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="分类"><el-select v-model="form.category_id"><el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" /></el-select></el-form-item>
        <el-form-item label="简述"><el-input v-model="form.short_desc" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="详情"><el-input v-model="form.description" type="textarea" :rows="5" /></el-form-item>
        <el-form-item label="主图URL"><el-input v-model="form.cover_image" /></el-form-item>
        <el-form-item label="图集">
          <div v-for="(img,i) in form.images" :key="i" style="display:flex;gap:8px;margin-bottom:8px">
            <el-input v-model="form.images[i]" placeholder="图片URL" />
            <el-button type="danger" @click="form.images.splice(i,1)" :icon="Delete" />
          </div>
          <el-button @click="form.images.push('')" size="small">添加图片</el-button>
        </el-form-item>
        <el-form-item label="参数"><el-input v-model="form.params" type="textarea" :rows="3" placeholder='JSON格式，如 [{"key":"规格","value":"100x50"}]' /></el-form-item>
        <el-form-item label="推荐"><el-switch v-model="form.is_recommend" :active-value="1" :inactive-value="0" /></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="上架" inactive-text="下架" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { adminApi } from '@/api/business'

const loading = ref(false)
const list = ref<any[]>([])
const categories = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const filters = reactive({ categoryId: undefined as any, name: '' })
const dialogVisible = ref(false)
const editing = ref<any>(null)
const form = reactive({ id: 0, name: '', category_id: 0, short_desc: '', description: '', cover_image: '', params: '', is_recommend: 0, sort_order: 0, status: 1, images: [] as string[] })

async function loadList() {
  loading.value = true
  try { const res = await adminApi.getProducts({ page: page.value, pageSize: pageSize.value, categoryId: filters.categoryId, name: filters.name || undefined }); list.value = res.data.list; total.value = res.data.total } catch {} finally { loading.value = false }
}
async function loadCategories() { const res = await adminApi.getCategories('product'); categories.value = res.data }

function openDialog(row?: any) {
  editing.value = row || null
  if (row) { Object.assign(form, row); form.images = row.images || [] } else { Object.assign(form, { id: 0, name: '', category_id: categories.value[0]?.id || 0, short_desc: '', description: '', cover_image: '', params: '', is_recommend: 0, sort_order: 0, status: 1, images: [] }) }
  dialogVisible.value = true
}

async function save() {
  if (editing.value) { await adminApi.updateProduct(form.id, form) } else { await adminApi.createProduct(form) }
  dialogVisible.value = false; loadList()
}

async function del(row: any) { await ElMessageBox.confirm(`确定删除"${row.name}"?`, '提示', { type: 'warning' }); await adminApi.deleteProduct(row.id); loadList() }

onMounted(() => { loadCategories(); loadList() })
</script>

<style scoped>.toolbar { margin-bottom: 16px; display: flex; }</style>
