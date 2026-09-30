<template>
  <div class="login-page">
    <BaseCard class="login-card">
      <div class="login-logo">
        <div class="logo-icon">D</div>
        <span>DevFlow 全栈模板</span>
      </div>
      <h2>首次登录请修改密码</h2>
      <p class="subtitle">为保障账号安全，请设置新密码</p>

      <BaseFormGroup label="当前密码">
        <BaseInput
          v-model="form.oldPassword"
          type="password"
          placeholder="请输入当前密码"
          @keyup.enter="handleChange"
        />
      </BaseFormGroup>
      <BaseFormGroup label="新密码" hint="至少 6 位">
        <BaseInput
          v-model="form.newPassword"
          type="password"
          placeholder="请输入新密码"
          @keyup.enter="handleChange"
        />
      </BaseFormGroup>
      <BaseFormGroup label="确认新密码">
        <BaseInput
          v-model="form.confirmPassword"
          type="password"
          placeholder="请再次输入新密码"
          @keyup.enter="handleChange"
        />
      </BaseFormGroup>

      <BaseButton
        variant="primary"
        block
        class="login-btn"
        :disabled="loading"
        @click="handleChange"
      >
        {{ loading ? '修改中...' : '确认修改' }}
      </BaseButton>

      <div class="login-footer">
        <a href="javascript:void(0)" @click="goLogin">← 返回登录</a>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { resetRoutes } from '@/router/index'
import { useUserStore } from '@/stores/user'
import api, { showToast } from '@/utils/api'
import BaseCard from '@/components/base/BaseCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseFormGroup from '@/components/base/BaseFormGroup.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

async function handleChange() {
  if (!form.oldPassword || !form.newPassword || !form.confirmPassword) {
    showToast('warning', '请填写所有密码字段')
    return
  }
  if (form.newPassword.length < 6) {
    showToast('warning', '密码长度不能少于6位')
    return
  }
  if (form.newPassword !== form.confirmPassword) {
    showToast('warning', '两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    await api.post('/auth/change-password', {
      old_password: form.oldPassword,
      new_password: form.newPassword
    })
    userStore.updateMustChangePassword(false)
    // 密码修改成功后，重新登录
    userStore.logout()
    resetRoutes()
    router.push('/login')
  } catch (error: any) {
    // 拦截器已处理错误通知，此处记录日志用于调试
    console.warn('密码修改失败:', error?.response?.data?.message || error?.message)
  } finally {
    loading.value = false
  }
}

function goLogin() {
  router.push('/login')
}
</script>

<style scoped>
.login-page {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: var(--bg-deep);
}

.login-page::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, color-mix(in srgb, var(--accent-blue) 6%, transparent) 0%, transparent 70%);
  top: -200px;
  right: -100px;
  pointer-events: none;
}

.login-page::after {
  content: '';
  position: absolute;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.04) 0%, transparent 70%);
  bottom: -200px;
  left: -100px;
  pointer-events: none;
}

.login-card {
  width: 380px;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 40px;
  box-shadow: var(--shadow-lg), var(--shadow-glow);
  position: relative;
  z-index: var(--z-base);
  animation: slideUp var(--duration-slow) var(--ease-out);
}

.login-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 32px;
}

.login-logo .logo-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-blue-hover));
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: var(--text-inverse);
  font-weight: 700;
  box-shadow: 0 4px 16px color-mix(in srgb, var(--accent-blue) 20%, transparent);
}

.login-logo span {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.login-card h2 {
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 6px;
  color: var(--text-primary);
}

.login-card .subtitle {
  text-align: center;
  color: var(--text-tertiary);
  font-size: 13px;
  margin-bottom: 28px;
}

.login-btn {
  margin-top: 8px;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.login-footer a {
  color: var(--accent-blue);
  text-decoration: none;
}

.login-footer a:hover {
  color: var(--accent-blue-hover);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
