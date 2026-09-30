<template>
  <div class="app-layout">
    <!-- Top bar -->
    <div class="top-nav">
      <div class="top-nav-brand">
        <div class="logo-icon">A</div>
        <span>{{ appName }}</span>
      </div>
      <div class="top-nav-right">
        <!-- User dropdown -->
        <div class="user-dropdown-wrapper">
          <BaseButton variant="icon" class="user-trigger" @click="toggleUserMenu">
            <div class="user-avatar">{{ userStore.displayName?.charAt(0) || 'U' }}</div>
            <span class="user-name">{{ userStore.displayName }}</span>
            <BaseIcon name="chevron-down" :size="12" class="user-chevron"
              :style="{ transform: showUserMenu ? 'rotate(180deg)' : 'none', transition: 'transform 0.15s' }" />
          </BaseButton>
          <div v-if="showUserMenu" class="user-dropdown">
            <div class="dropdown-item" @click="goToSettings">
              <BaseIcon name="settings" :size="14" />
              <span>设置</span>
            </div>
            <div class="dropdown-divider"></div>
            <div class="dropdown-item dropdown-item-danger" @click="handleLogout">
              <BaseIcon name="log-out" :size="14" />
              <span>退出登录</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="main-area">
      <!-- Sidebar -->
      <BaseSidebar
        :active-key="activeMenuKey"
        :groups="sidebarGroups"
        :collapsible="true"
        @select="handleMenuSelect"
      />

      <!-- Content Area -->
      <div class="content-area">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { resetRoutes } from '@/router/index'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import BaseSidebar from '@/components/layout/BaseSidebar.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseIcon from '@/components/base/BaseIcon.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const permissionStore = usePermissionStore()

// App name - developers can customize this
const appName = '管理后台'

const currentRoute = computed(() => route.path)

// --- Icon map for sidebar items ---
// Developers should add mappings for business menu keys here
const sidebarIconMap: Record<string, string> = {
  'home': 'home',
  'settings': 'settings',
}

// --- Sidebar: fixed admin menu ---
const sidebarGroups = computed(() => {
  const menus = [
    { label: '内容管理', items: [
      { key: 'dashboard', label: '仪表盘', path: '/admin/dashboard' },
      { key: 'articles', label: '新闻管理', path: '/admin/articles' },
      { key: 'products', label: '产品管理', path: '/admin/products' },
      { key: 'categories', label: '栏目分类', path: '/admin/categories' },
      { key: 'pages', label: '单页内容', path: '/admin/pages' },
    ]},
    { label: '运营管理', items: [
      { key: 'messages', label: '留言管理', path: '/admin/messages' },
      { key: 'banners', label: '轮播图管理', path: '/admin/banners' },
      { key: 'friend-links', label: '友情链接', path: '/admin/friend-links' },
      { key: 'site-config', label: '网站设置', path: '/admin/site-config' },
    ]},
  ]
  if (permissionStore.menus?.length) {
    return [...menus, ...permissionStore.menus]
  }
  return menus
})

// Determine which sidebar item is active based on current route
const activeMenuKey = computed(() => {
  const path = currentRoute.value
  for (const group of sidebarGroups.value) {
    for (const item of (group.items || [])) {
      if (path === item.path || path.startsWith(item.path + '/')) return item.key
    }
  }
  // fallback for settings
  if (path.startsWith('/settings')) return 'settings'
  return ''
})

// Map menu key to route path
const menuPathMap = computed(() => {
  const map: Record<string, string> = {}
  for (const group of sidebarGroups.value) {
    for (const item of (group.items || [])) {
      map[item.key] = item.path
    }
  }
  return map
})

function handleMenuSelect(key: string) {
  const path = menuPathMap.value[key]
  if (path) {
    router.push(path)
  }
}

// --- User dropdown menu ---
const showUserMenu = ref(false)

function toggleUserMenu() {
  showUserMenu.value = !showUserMenu.value
}

function goToSettings() {
  showUserMenu.value = false
  router.push('/admin/site-config')
}

// Close dropdown when clicking outside
function handleClickOutside(e: MouseEvent) {
  const userWrapper = document.querySelector('.user-dropdown-wrapper')
  if (userWrapper && !userWrapper.contains(e.target as Node)) {
    showUserMenu.value = false
  }
}

// --- Logout ---
function handleLogout() {
  showUserMenu.value = false
  userStore.logout()
  resetRoutes()
  router.push('/')
}

// --- Lifecycle ---
onMounted(async () => {
  if (userStore.isLoggedIn) {
    await permissionStore.fetchMenus()
  }
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* Top navigation */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 16px;
  background: var(--bg-base);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
  z-index: var(--z-sticky);
}

.top-nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.logo-icon {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-blue-hover));
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #fff;
  font-weight: 700;
}

.top-nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* User dropdown */
.user-dropdown-wrapper {
  position: relative;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: background 0.15s;
}

.user-trigger:hover {
  background: var(--bg-hover);
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent-blue), var(--accent-blue-hover));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
}

.user-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.user-chevron {
  color: var(--text-tertiary);
}

.user-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 128px;
  width: max-content;
  background: var(--bg-base);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  z-index: var(--z-dropdown);
  overflow: hidden;
  padding: 4px;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
}

.dropdown-item:hover {
  background: var(--bg-hover);
}

.dropdown-item-danger {
  color: var(--accent-red);
}

.dropdown-item-danger:hover {
  background: var(--accent-red-muted);
}

.dropdown-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 4px 0;
}

/* Main area */
.main-area {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Content Area */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg-deep);
}
</style>
