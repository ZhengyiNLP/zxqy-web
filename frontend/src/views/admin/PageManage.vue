<template>
  <div>
    <el-card>
      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" min-width="150" />
        <el-table-column prop="pageKey" label="标识" width="120" />
        <el-table-column label="操作" width="100" fixed="right"><template #default="{row}"><el-button size="small" @click="openDialog(row)">编辑</el-button></template></el-table-column>
      </el-table>
    </el-card>
    <el-dialog v-model="dialogVisible" :title="`编辑页面 - ${form.title}`" width="700px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="10" /></el-form-item>
        <el-form-item v-if="form.pageKey === 'contact'" label="联系信息">
          <el-input v-model="form.extra_data" type="textarea" :rows="4" placeholder='JSON: {"address":"","phone":"","email":"","workTime":""}' />
        </el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { adminApi } from '@/api/business'

const loading = ref(false)
const list = ref<any[]>([])
const dialogVisible = ref(false)
const form = reactive({ id: 0, title: '', pageKey: '', content: '', extra_data: '' })

async function loadList() { loading.value = true; try { const res = await adminApi.getPages(); list.value = res.data } catch {} finally { loading.value = false } }
function openDialog(row: any) { Object.assign(form, row); dialogVisible.value = true }
async function save() { await adminApi.updatePage(form.id, { title: form.title, content: form.content, extra_data: form.extra_data }); dialogVisible.value = false; loadList() }
onMounted(() => loadList())
</script>
