<template>
  <div>
    <el-card>
      <div class="toolbar"><el-button type="success" @click="openDialog()">新增轮播图</el-button></div>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column label="图片" width="120"><template #default="{row}"><el-image v-if="row.imageUrl" :src="'/api'+row.imageUrl" style="width:100px;height:60px" fit="cover" /><span v-else>-</span></template></el-table-column>
        <el-table-column prop="title" label="标题" min-width="150" />
        <el-table-column prop="linkUrl" label="跳转链接" min-width="150" show-overflow-tooltip />
        <el-table-column prop="sortOrder" label="排序" width="80" />
        <el-table-column label="状态" width="80"><template #default="{row}"><el-tag :type="row.status?'success':'danger'" size="small">{{ row.status ? '启用' : '禁用' }}</el-tag></template></el-table-column>
        <el-table-column label="操作" width="150" fixed="right"><template #default="{row}"><el-button size="small" @click="openDialog(row)">编辑</el-button><el-button size="small" type="danger" @click="del(row)">删除</el-button></template></el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="editing?'编辑轮播图':'新增轮播图'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="图片URL"><el-input v-model="form.image_url" /></el-form-item>
        <el-form-item label="跳转链接"><el-input v-model="form.link_url" /></el-form-item>
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
const form = reactive({ id: 0, title: '', image_url: '', link_url: '', sort_order: 0, status: 1 })

async function loadList() { loading.value = true; try { const res = await adminApi.getBanners(); list.value = res.data } catch {} finally { loading.value = false } }
function openDialog(row?: any) { editing.value = row || null; if (row) { Object.assign(form, row) } else { Object.assign(form, { id: 0, title: '', image_url: '', link_url: '', sort_order: 0, status: 1 }) }; dialogVisible.value = true }
async function save() { const { id, ...data } = form; if (editing.value) { await adminApi.updateBanner(id, data) } else { await adminApi.createBanner(data) }; dialogVisible.value = false; loadList() }
async function del(row: any) { await ElMessageBox.confirm('确定删除该轮播图?', '提示', { type: 'warning' }); await adminApi.deleteBanner(row.id); loadList() }
onMounted(() => loadList())
</script>

<style scoped>.toolbar { margin-bottom: 16px; }</style>
