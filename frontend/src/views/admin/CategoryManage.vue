<template>
  <div>
    <el-card>
      <div class="toolbar"><el-button type="success" @click="openDialog()">新增分类</el-button></div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="type" label="类型" width="100"><template #default="{row}"><el-tag :type="row.type==='article'?'':'success'" size="small">{{ row.type === 'article' ? '新闻' : '产品' }}</el-tag></template></el-table-column>
        <el-table-column prop="sortOrder" label="排序" width="80" />
        <el-table-column label="状态" width="80"><template #default="{row}"><el-tag :type="row.status?'success':'danger'" size="small">{{ row.status ? '启用' : '禁用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="150" fixed="right"><template #default="{row}"><el-button size="small" @click="openDialog(row)">编辑</el-button><el-button size="small" type="danger" @click="del(row)">删除</el-button></template></el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="editing?'编辑分类':'新增分类'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="类型"><el-radio-group v-model="form.type"><el-radio value="article">新闻</el-radio><el-radio value="product">产品</el-radio></el-radio-group></el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
        <el-form-item label="状态"><el-switch v-model="form.status" :active-value="1" :inactive-value="0" /></el-form-item>
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
const dialogVisible = ref(false)
const editing = ref<any>(null)
const form = reactive({ id: 0, name: '', type: 'article', sort_order: 0, status: 1 })

async function loadList() { loading.value = true; try { const res = await adminApi.getCategories(); list.value = res.data } catch {} finally { loading.value = false } }
function openDialog(row?: any) { editing.value = row || null; if (row) { Object.assign(form, row) } else { Object.assign(form, { id: 0, name: '', type: 'article', sort_order: 0, status: 1 }) }; dialogVisible.value = true }
async function save() { if (editing.value) { await adminApi.updateCategory(form.id, form) } else { await adminApi.createCategory(form) }; dialogVisible.value = false; loadList() }
async function del(row: any) { await ElMessageBox.confirm(`确定删除"${row.name}"?`, '提示', { type: 'warning' }); await adminApi.deleteCategory(row.id); loadList() }
onMounted(() => loadList())
</script>

<style scoped>.toolbar { margin-bottom: 16px; }</style>
