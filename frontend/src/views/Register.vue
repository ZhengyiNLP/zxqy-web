<template>
  <div class="login-page">
    <BaseCard class="login-card">
      <div class="login-logo">
        <div class="logo-icon">D</div>
        <span>DevFlow 全栈模板</span>
      </div>
      <h2>创建账号</h2>
      <p class="subtitle">注册新账号开始使用系统</p>

      <form @submit.prevent="handleRegister">
        <BaseFormGroup
          label="用户名"
          :error="errors.username"
          :hint="checking.username ? '检查中...' : ''"
        >
          <BaseInput
            v-model="form.username"
            :class="{ 'input-error': errors.username }"
            placeholder="2-50个字符"
            @blur="checkUsername"
          />
          <span v-if="!errors.username && !checking.username && form.username && usernameAvailable" class="field-success">✓ 可用</span>
        </BaseFormGroup>

        <BaseFormGroup
          label="显示名称"
          :error="errors.displayName"
          :hint="checking.displayName ? '检查中...' : ''"
        >
          <BaseInput
            v-model="form.displayName"
            :class="{ 'input-error': errors.displayName }"
            placeholder="全局唯一，用于展示"
            @blur="checkDisplayName"
          />
          <span v-if="!errors.displayName && !checking.displayName && form.displayName && displayNameAvailable" class="field-success">✓ 可用</span>
        </BaseFormGroup>

        <BaseFormGroup label="密码" :error="errors.password" hint="至少 6 位">
          <BaseInput
            v-model="form.password"
            type="password"
            :class="{ 'input-error': errors.password }"
            placeholder="请输入密码"
          />
        </BaseFormGroup>

        <BaseFormGroup label="确认密码" :error="errors.confirmPassword">
          <BaseInput
            v-model="form.confirmPassword"
            type="password"
            :class="{ 'input-error': errors.confirmPassword }"
            placeholder="再次输入密码"
          />
        </BaseFormGroup>

        <BaseAlert v-if="submitError" variant="error" class="submit-error">{{ submitError }}</BaseAlert>

        <BaseButton type="submit" variant="primary" block :disabled="loading">
          {{ loading ? '注册中...' : '注 册' }}
        </BaseButton>
      </form>

      <div class="login-footer">
        已有账号？<router-link to="/login">返回登录</router-link>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import api from '@/utils/api'
import BaseCard from '@/components/base/BaseCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseFormGroup from '@/components/base/BaseFormGroup.vue'
import BaseAlert from '@/components/base/BaseAlert.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({
  username: '',
  displayName: '',
  password: '',
  confirmPassword: '',
})

const errors = reactive({
  username: '',
  displayName: '',
  password: '',
  confirmPassword: '',
})

const checking = reactive({
  username: false,
  displayName: false,
})

const usernameAvailable = ref(false)
const displayNameAvailable = ref(false)
const loading = ref(false)
const submitError = ref('')

async function checkUsername() {
  if (!form.username || form.username.length < 2) {
    errors.username = '用户名至少2个字符'
    usernameAvailable.value = false
    return
  }
  errors.username = ''
  checking.username = true
  try {
    const res = await api.get(`/auth/check-username?username=${encodeURIComponent(form.username)}`)
    if (res.data.available) {
      usernameAvailable.value = true
      errors.username = ''
    } else {
      usernameAvailable.value = false
      errors.username = '用户名已存在'
    }
  } catch {
    // ignore
  } finally {
    checking.username = false
  }
}

async function checkDisplayName() {
  if (!form.displayName || form.displayName.length < 2) {
    errors.displayName = '显示名至少2个字符'
    displayNameAvailable.value = false
    return
  }
  errors.displayName = ''
  checking.displayName = true
  try {
    const res = await api.get(`/auth/check-display-name?display_name=${encodeURIComponent(form.displayName)}`)
    if (res.data.available) {
      displayNameAvailable.value = true
      errors.displayName = ''
    } else {
      displayNameAvailable.value = false
      errors.displayName = '显示名已被使用'
    }
  } catch {
    // ignore
  } finally {
    checking.displayName = false
  }
}

async function handleRegister() {
  // Validate
  errors.username = ''
  errors.displayName = ''
  errors.password = ''
  errors.confirmPassword = ''
  submitError.value = ''

  if (!form.username || form.username.length < 2) {
    errors.username = '用户名至少2个字符'
    return
  }
  if (!form.displayName || form.displayName.length < 2) {
    errors.displayName = '显示名至少2个字符'
    return
  }
  if (!form.password || form.password.length < 6) {
    errors.password = '密码至少6位'
    return
  }
  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = '两次密码不一致'
    return
  }

  loading.value = true
  try {
    await userStore.register(form.username, form.displayName, form.password)
    router.push('/login?registered=1')
  } catch (e: any) {
    submitError.value = e.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: var(--bg-deep);
  padding: 20px 0;
  box-sizing: border-box;
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

:deep(.base-input.input-error) {
  border-color: var(--accent-red);
}

.field-success {
  font-size: 12px;
  color: var(--accent-green);
  margin-top: 4px;
  display: block;
}

.submit-error {
  margin-bottom: 16px;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 13px;
  color: var(--text-secondary);
}

.login-footer a {
  color: var(--accent-blue);
  text-decoration: none;
  font-weight: 500;
}

.login-footer a:hover {
  color: var(--accent-blue-hover);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
