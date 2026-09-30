<template>
  <div class="contact-page" v-loading="loading">
    <div class="container">
      <el-card v-if="pageData">
        <h1 class="title">{{ pageData.title }}</h1>
        <el-row :gutter="40">
          <el-col :xs="24" :md="12">
            <div class="contact-info">
              <h3>联系方式</h3>
              <div class="info-item" v-if="contact.address"><el-icon><Location /></el-icon><span>{{ contact.address }}</span></div>
              <div class="info-item" v-if="contact.phone"><el-icon><Phone /></el-icon><span>{{ contact.phone }}</span></div>
              <div class="info-item" v-if="contact.email"><el-icon><Message /></el-icon><span>{{ contact.email }}</span></div>
              <div class="info-item" v-if="contact.workTime"><el-icon><Clock /></el-icon><span>{{ contact.workTime }}</span></div>
            </div>
          </el-col>
          <el-col :xs="24" :md="12">
            <div class="message-form">
              <h3>在线留言</h3>
              <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
                <el-form-item label="姓名" prop="name">
                  <el-input v-model="form.name" placeholder="请输入您的姓名" />
                </el-form-item>
                <el-form-item label="电话" prop="phone">
                  <el-input v-model="form.phone" placeholder="请输入联系电话" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="form.email" placeholder="请输入邮箱（选填）" />
                </el-form-item>
                <el-form-item label="内容" prop="content">
                  <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请输入留言内容" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="submitForm" :loading="submitting">提交留言</el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import type { FormInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { Location, Phone, Message, Clock } from '@element-plus/icons-vue'
import { portalApi } from '@/api/business'

const loading = ref(false)
const submitting = ref(false)
const pageData = ref<any>(null)
const formRef = ref<FormInstance>()

const form = reactive({ name: '', phone: '', email: '', content: '' })
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$|^\d{3,4}-?\d{7,8}$/, message: '电话格式不正确', trigger: 'blur' },
  ],
  content: [{ required: true, message: '请输入留言内容', trigger: 'blur' }],
}

const contact = computed(() => {
  if (!pageData.value?.extraData) return {}
  try { return JSON.parse(pageData.value.extraData) } catch { return {} }
})

async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      await portalApi.submitMessage(form)
      ElMessage.success('留言成功，我们会尽快与您联系')
      formRef.value?.resetFields()
    } catch { /* 拦截器已处理 */ }
    finally { submitting.value = false }
  })
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await portalApi.getPage('contact')
    pageData.value = res.data
  } catch { pageData.value = null }
  finally { loading.value = false }
})
</script>

<style scoped>
.contact-page { padding: 20px 0; }
.container { max-width: 900px; margin: 0 auto; padding: 0 16px; }
.title { font-size: 26px; color: #333; margin: 0 0 24px; }
.contact-info h3, .message-form h3 { font-size: 18px; margin: 0 0 20px; color: #333; }
.info-item { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; font-size: 15px; color: #555; }
.info-item .el-icon { color: #409eff; font-size: 18px; }
@media (max-width: 768px) {
  .contact-info { margin-bottom: 30px; }
}
</style>
