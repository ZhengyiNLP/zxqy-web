<template>
  <div class="home-page">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-text">
        <h2>{{ greeting }}，{{ userStore.displayName || '管理员' }}！</h2>
        <p>{{ today }}，欢迎使用 DevFlow 全栈模板</p>
      </div>
      <div class="welcome-badges">
        <BaseBadge variant="blue">FastAPI + Vue3</BaseBadge>
        <BaseBadge variant="gray">v1.0.0</BaseBadge>
      </div>
    </div>

    <!-- 快捷入口 -->
    <div class="entry-grid">
      <div v-for="item in entries" :key="item.key" class="entry-card" @click="go(item.path)">
        <div class="entry-icon" :style="{ background: item.bg }">
          <BaseIcon :name="item.icon" :size="20" color="#ffffff" />
        </div>
        <div class="entry-info">
          <div class="entry-title">{{ item.label }}</div>
          <div class="entry-desc">{{ item.desc }}</div>
        </div>
      </div>
    </div>

    <!-- 技术栈 -->
    <div class="tech-grid">
      <div class="tech-card">
        <div class="tech-card-header">
          <BaseIcon name="database" :size="16" />
          <span>后端技术</span>
        </div>
        <div class="tech-tags">
          <span v-for="t in backendTech" :key="t" class="tech-tag">{{ t }}</span>
        </div>
      </div>
      <div class="tech-card">
        <div class="tech-card-header">
          <BaseIcon name="code" :size="16" />
          <span>前端技术</span>
        </div>
        <div class="tech-tags">
          <span v-for="t in frontendTech" :key="t" class="tech-tag tech-tag-primary">{{ t }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import BaseIcon from '@/components/base/BaseIcon.vue'
import BaseBadge from '@/components/base/BaseBadge.vue'

const router = useRouter()
const userStore = useUserStore()

const entries = [
  { key: 'settings', label: '设置中心', desc: '个人资料 / 修改密码', icon: 'settings', path: '/settings/profile', bg: 'linear-gradient(135deg, var(--accent-blue), var(--accent-blue-hover))' },
  { key: 'users', label: '用户管理', desc: '管理系统用户账号', icon: 'users', path: '/settings/users', bg: 'linear-gradient(135deg, #00b42a, #27c346)' },
  { key: 'configs', label: '参数设置', desc: '系统运行参数配置', icon: 'sliders-horizontal', path: '/settings/configs', bg: 'linear-gradient(135deg, #ff7d00, #ff9a3d)' },
  { key: 'permissions', label: '权限管理', desc: '角色与权限分配', icon: 'shield', path: '/settings/permissions', bg: 'linear-gradient(135deg, #7c3aed, #9a5cff)' },
  { key: 'register', label: '注册新账号', desc: '开放注册新用户', icon: 'user-plus', path: '/register', bg: 'linear-gradient(135deg, #f53f3f, #f87171)' },
]

const backendTech = ['FastAPI', 'Uvicorn', 'SQLAlchemy', 'Pydantic', 'JWT', 'BCrypt', 'uv']

const frontendTech = ['Vue 3', 'Vite', 'TypeScript', 'Element Plus', 'Pinia', 'Vue Router', 'Axios']

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const today = computed(() => {
  const now = new Date()
  const days = ['日', '一', '二', '三', '四', '五', '六']
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日 星期${days[now.getDay()]}`
})

function go(path: string) {
  router.push(path)
}
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

/* 欢迎横幅 */
.welcome-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 28px 32px;
  border-radius: var(--radius-lg);
  background: linear-gradient(120deg, #1e2a3a, #2d4a7a);
  color: #fff;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.welcome-banner::after {
  content: '';
  position: absolute;
  right: -60px;
  top: -60px;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, color-mix(in srgb, var(--accent-blue) 45%, transparent), transparent 70%);
}

.welcome-text h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.welcome-text p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.welcome-badges {
  display: flex;
  gap: 8px;
  position: relative;
  z-index: 1;
}

/* 快捷入口 */
.entry-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}

.entry-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: var(--bg-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
}

.entry-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-emphasis);
  box-shadow: var(--shadow-md);
}

.entry-icon {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.entry-info {
  flex: 1;
  min-width: 0;
}

.entry-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 3px;
}

.entry-desc {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* 技术栈 */
.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 12px;
}

.tech-card {
  padding: 16px 20px;
  background: var(--bg-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

.tech-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.tech-card-header .base-icon {
  color: var(--accent-blue);
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tech-tag {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border-subtle);
}

.tech-tag-primary {
  background: var(--accent-blue-muted);
  color: var(--accent-blue);
  border-color: transparent;
}
</style>
