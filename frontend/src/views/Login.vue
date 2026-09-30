<template>
  <div class="login-page">
    <BaseCard class="login-card">
      <div class="login-logo">
        <div class="logo-icon">D</div>
        <span>中小企业门户管理</span>
      </div>
      <h2>欢迎使用</h2>
      <p class="subtitle">登录后开始使用系统</p>

      <BaseFormGroup label="用户名">
        <BaseInput
          v-model="form.username"
          placeholder="请输入用户名"
          @keyup.enter="handleLogin"
        />
      </BaseFormGroup>
      <BaseFormGroup label="密码">
        <div class="password-wrapper">
          <BaseInput
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
          <BaseButton
            variant="icon"
            type="button"
            class="toggle-pw"
            @click="showPassword = !showPassword"
          >
            <svg style="width:14px;height:14px;flex-shrink:0;display:inline-block;" v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            <svg style="width:14px;height:14px;flex-shrink:0;display:inline-block;" v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
          </BaseButton>
        </div>
      </BaseFormGroup>

      <BaseButton
        variant="primary"
        block
        class="login-btn"
        :disabled="loading"
        @click="handleLogin"
      >
        {{ loading ? '登录中...' : '登 录' }}
      </BaseButton>

      <div class="login-footer">
        <div class="footer-main">
          <router-link to="/register">注册新账号</router-link>
        </div>
        <div class="footer-hints">
          <span>首次登录？修改密码</span>
          <span class="footer-divider">|</span>
          <span class="forgot-pw">忘记密码？联系管理员</span>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import BaseCard from '@/components/base/BaseCard.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseFormGroup from '@/components/base/BaseFormGroup.vue'
import BaseInput from '@/components/base/BaseInput.vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const showPassword = ref(false)

const form = reactive({
  username: '',
  password: ''
})

async function handleLogin() {
  if (!form.username.trim() || !form.password.trim()) return
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    if (userStore.mustChangePassword) {
      router.push('/change-password')
    } else {
      router.push('/admin/dashboard')
    }
  } catch (error: any) {
    // Error toast handled by interceptor
  } finally {
    loading.value = false
  }
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

.password-wrapper {
  position: relative;
}

.password-wrapper :deep(.base-input) {
  padding-right: 40px;
}

.toggle-pw {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color var(--duration-fast);
}

.toggle-pw:hover {
  color: var(--text-secondary);
}

.login-btn {
  margin-top: 8px;
}

.login-footer {
  margin-top: 24px;
}

.footer-main {
  text-align: center;
  margin-bottom: 10px;
}

.footer-main a {
  color: var(--accent-blue);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
}

.footer-main a:hover {
  color: var(--accent-blue-hover);
}

.footer-hints {
  text-align: center;
  font-size: 12px;
  color: var(--text-tertiary);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(16px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.footer-divider {
  margin: 0 8px;
  color: var(--text-tertiary);
}

.forgot-pw {
  color: var(--text-tertiary);
  font-size: 11px;
}

.forgot-pw:hover {
  color: var(--text-secondary);
}
</style>
