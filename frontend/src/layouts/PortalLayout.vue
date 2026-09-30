<template>
  <div class="portal-layout">
    <!-- ===== 顶部导航栏（固定悬浮置顶：首页未滚动时透明叠加在 banner 上，滚动后/非首页白底） ===== -->
    <header class="portal-header" :class="headerClass">
      <div class="header-inner">
        <!-- 网站 Logo + 名称 -->
        <router-link to="/" class="brand">
          <span class="brand-logo">企</span>
          <span class="brand-text">
            <span class="brand-name">{{ SITE_NAME }}</span>
            <span class="brand-slogan">专注企业综合信息服务</span>
          </span>
        </router-link>

        <!-- 桌面端横向导航菜单 -->
        <el-menu
          class="desktop-menu"
          mode="horizontal"
          :ellipsis="false"
          :default-active="activeMenu"
          router
        >
          <el-menu-item v-for="item in navItems" :key="item.path" :index="item.path">
            {{ item.label }}
          </el-menu-item>
        </el-menu>

        <!-- 右侧操作区：后台管理入口 + 移动端汉堡按钮 -->
        <div class="header-actions">
          <router-link to="/login" class="admin-entry">后台管理</router-link>
          <button
            type="button"
            class="hamburger-btn"
            aria-label="打开导航菜单"
            @click="mobileMenuVisible = true"
          >
            <span></span><span></span><span></span>
          </button>
        </div>
      </div>
    </header>

    <!-- ===== 页面内容出口（非首页时顶部留出导航高度，首页由 banner 顶到视口顶部被透明导航覆盖） ===== -->
    <main class="portal-main" :class="{ 'main-with-top': !isHome }">
      <router-view />
    </main>

    <!-- ===== 底部页脚 ===== -->
    <footer class="portal-footer">
      <div class="footer-inner">
        <div class="footer-grid">
          <!-- 品牌简介 -->
          <div class="footer-brand-col">
            <div class="footer-brand">
              <span class="brand-logo small">企</span>
              <span class="footer-brand-name">{{ SITE_NAME }}</span>
            </div>
            <p class="footer-desc">
              专业的企业综合信息服务平台，致力于为企业客户提供全方位的信息化解决方案与优质服务。
            </p>
          </div>
          <!-- 站点导航 -->
          <div class="footer-col">
            <h4>站点导航</h4>
            <router-link to="/">首页</router-link>
            <router-link to="/articles">新闻动态</router-link>
            <router-link to="/products">产品展示</router-link>
          </div>
          <!-- 企业信息 -->
          <div class="footer-col">
            <h4>企业信息</h4>
            <router-link to="/about">关于我们</router-link>
            <router-link to="/culture">企业文化</router-link>
            <router-link to="/contact">联系我们</router-link>
          </div>
        </div>

        <!-- 友情链接（来自首页聚合数据，加载失败时不展示，不影响页面渲染） -->
        <div class="friend-links" v-if="friendLinks.length">
          <span class="friend-label">友情链接：</span>
          <a
            v-for="link in friendLinks"
            :key="link.id"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
          >{{ link.name }}</a>
        </div>

        <!-- 版权信息 -->
        <div class="footer-bottom">
          <span>© {{ currentYear }} {{ SITE_NAME }} 版权所有</span>
          <router-link to="/login" class="footer-admin-link">后台管理</router-link>
        </div>
      </div>
    </footer>

    <!-- ===== 移动端抽屉导航菜单 ===== -->
    <el-drawer
      v-model="mobileMenuVisible"
      title="导航菜单"
      direction="rtl"
      size="72%"
      append-to-body
    >
      <el-menu class="drawer-menu" :default-active="activeMenu" router @select="handleMobileSelect">
        <el-menu-item v-for="item in navItems" :key="item.path" :index="item.path">
          {{ item.label }}
        </el-menu-item>
      </el-menu>
      <div class="drawer-footer">
        <router-link to="/login" class="drawer-admin-link" @click="mobileMenuVisible = false">
          后台管理登录
        </router-link>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { portalApi } from '@/api/business'

/** 站点名称（后续接入站点配置后可改为动态获取） */
const SITE_NAME = '中小企业云服务网'

/** 是否首页（首页首屏导航透明叠加在 banner 上） */
const isHome = computed(() => route.path === '/')

/** 页面滚动距离（超过阈值后导航切换为白底） */
const scrolled = ref(false)
const onScroll = () => {
  scrolled.value = window.scrollY > 40
}

/** 导航样式：首页未滚动=透明叠加；其余情况=白底实色 */
const headerClass = computed(() => ({
  'header-transparent': isHome.value && !scrolled.value,
  'header-solid': !isHome.value || scrolled.value,
}))

/** 友情链接数据结构 */
interface FriendLink {
  id: number
  name: string
  url: string
}

const route = useRoute()
/** 友情链接列表（仅页脚展示） */
const friendLinks = ref<FriendLink[]>([])
/** 移动端抽屉菜单展开状态 */
const mobileMenuVisible = ref(false)
/** 当前年份（页脚版权用） */
const currentYear = new Date().getFullYear()

/** 顶部导航菜单项 */
const navItems = [
  { path: '/', label: '首页' },
  { path: '/articles', label: '新闻动态' },
  { path: '/products', label: '产品展示' },
  { path: '/about', label: '关于我们' },
  { path: '/culture', label: '企业文化' },
  { path: '/contact', label: '联系我们' },
]

/** 当前高亮菜单：详情页（如 /articles/1）也高亮对应上级栏目 */
const activeMenu = computed(() => {
  const path = route.path
  if (path === '/') return '/'
  const match = navItems
    .filter((item) => item.path !== '/')
    .find((item) => path === item.path || path.startsWith(item.path + '/'))
  return match ? match.path : path
})

/** 移动端抽屉菜单选中后自动收起 */
const handleMobileSelect = () => {
  mobileMenuVisible.value = false
}

/** 加载友情链接（失败静默处理，页面仍可正常渲染） */
const loadFriendLinks = async () => {
  try {
    const res = await portalApi.getHome()
    friendLinks.value = (res.data?.friendLinks as FriendLink[]) || []
  } catch {
    friendLinks.value = []
  }
}

onMounted(() => {
  loadFriendLinks()
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
/* ===== 整体骨架 ===== */
.portal-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg-deep, #f7f8fa);
}
.portal-main {
  flex: 1;
}

/* ===== 顶部导航栏（固定悬浮置顶） ===== */
.portal-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 500;
  transition: background 0.3s ease, box-shadow 0.3s ease;
}
/* 实色状态（非首页 / 首页已滚动）：白底深色文字 */
.portal-header.header-solid {
  background: #ffffff;
  border-bottom: 1px solid var(--border-subtle, #e5e6eb);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
/* 透明状态（首页首屏）：叠加在 banner 上，白色文字（蓝调轻遮罩保证可读性） */
.portal-header.header-transparent {
  background: linear-gradient(180deg, rgba(9, 84, 158, 0.38), rgba(9, 84, 158, 0) 100%);
  border-bottom: none;
  box-shadow: none;
}
.portal-main.main-with-top {
  padding-top: 64px;
}
.header-inner {
  max-width: 1200px;
  height: 64px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 网站标识 */
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  text-decoration: none;
}
.brand-logo {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #2563eb, #60a5fa);
  color: #ffffff;
  font-size: 20px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.35);
}
.brand-logo.small {
  width: 32px;
  height: 32px;
  font-size: 16px;
  border-radius: 8px;
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.25;
}
.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary, #1f2329);
  transition: color 0.3s;
}
.brand-slogan {
  font-size: 11px;
  color: var(--text-tertiary, #8f959e);
  letter-spacing: 1px;
  transition: color 0.3s;
}
/* 透明导航下品牌文字白色 */
.header-transparent .brand-name {
  color: #ffffff;
}
.header-transparent .brand-slogan {
  color: rgba(255, 255, 255, 0.75);
}
.header-transparent .brand-logo {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
}

/* 桌面端横向菜单：覆盖默认横向菜单样式 */
.desktop-menu {
  flex: 1;
  justify-content: center;
  border-bottom: none !important;
  background: transparent !important;
}
.desktop-menu :deep(.el-menu-item) {
  height: 64px;
  line-height: 64px;
  /* bug 修复：显式声明内边距，防止菜单文字粘连 */
  padding: 0 26px;
  margin: 0;
  border-radius: 0;
  border-bottom: 3px solid transparent;
  border-top-color: transparent !important;
  color: var(--text-primary, #1f2329);
  font-size: 15px;
  white-space: nowrap;
  transition: color 0.3s;
}
.desktop-menu :deep(.el-menu-item:hover) {
  background: transparent !important;
  color: var(--accent-blue, #3b82f6) !important;
}
.desktop-menu :deep(.el-menu-item.is-active) {
  background: transparent !important;
  color: var(--accent-blue, #3b82f6) !important;
  border-bottom-color: var(--accent-blue, #3b82f6);
  font-weight: 600;
}
/* 透明导航下菜单项白色，高亮项白色+白色底边 */
.header-transparent .desktop-menu :deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.92) !important;
}
.header-transparent .desktop-menu :deep(.el-menu-item:hover) {
  color: #ffffff !important;
  background: rgba(255, 255, 255, 0.16) !important;
}
.header-transparent .desktop-menu :deep(.el-menu-item.is-active) {
  color: #ffffff !important;
  border-bottom-color: #ffffff;
  font-weight: 600;
}

/* 右侧操作区 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}
.admin-entry {
  padding: 6px 16px;
  border: 1px solid var(--border-default, #dee0e3);
  border-radius: 999px;
  font-size: 13px;
  color: var(--text-secondary, #646a73);
  white-space: nowrap;
  text-decoration: none;
  transition: all 0.2s;
}
.admin-entry:hover {
  color: var(--accent-blue, #3b82f6);
  border-color: var(--accent-blue, #3b82f6);
}
/* 透明导航下后台入口白色描边 */
.header-transparent .admin-entry {
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.6);
}
.header-transparent .admin-entry:hover {
  color: #ffffff;
  border-color: #ffffff;
  background: rgba(255, 255, 255, 0.15);
}
/* 移动端汉堡按钮（默认隐藏） */
.hamburger-btn {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 38px;
  height: 38px;
  padding: 8px;
  background: transparent;
  border: 1px solid var(--border-default, #dee0e3);
  border-radius: 8px;
  cursor: pointer;
}
.hamburger-btn span {
  display: block;
  width: 100%;
  height: 2px;
  background: var(--text-primary, #1f2329);
  border-radius: 2px;
  transition: all 0.2s;
}
/* 透明导航下汉堡按钮白色 */
.header-transparent .hamburger-btn {
  border-color: rgba(255, 255, 255, 0.5);
}
.header-transparent .hamburger-btn span {
  background: #ffffff;
}

/* ===== 底部页脚 ===== */
.portal-footer {
  background: #1d2330;
  color: rgba(255, 255, 255, 0.65);
}
.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 16px 24px;
}
.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 32px;
}
.footer-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.footer-brand-name {
  font-size: 17px;
  font-weight: 600;
  color: #ffffff;
}
.footer-desc {
  font-size: 13px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.45);
  margin: 0;
}
.footer-col {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.footer-col h4 {
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 6px;
}
.footer-col a {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  text-decoration: none;
  transition: color 0.2s;
  width: fit-content;
}
.footer-col a:hover {
  color: #ffffff;
}

/* 友情链接 */
.friend-links {
  margin-top: 36px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 13px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px 20px;
  align-items: center;
}
.friend-label {
  color: rgba(255, 255, 255, 0.4);
}
.friend-links a {
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  transition: color 0.2s;
}
.friend-links a:hover {
  color: #ffffff;
}

/* 版权信息 */
.footer-bottom {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
  flex-wrap: wrap;
  gap: 8px;
}
.footer-admin-link {
  color: rgba(255, 255, 255, 0.4);
  text-decoration: none;
  transition: color 0.2s;
}
.footer-admin-link:hover {
  color: #ffffff;
}

/* ===== 移动端抽屉菜单 ===== */
.drawer-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  border-radius: 8px;
}
.drawer-footer {
  margin-top: 20px;
  padding: 0 12px;
}
.drawer-admin-link {
  display: block;
  text-align: center;
  padding: 11px 0;
  border: 1px solid var(--border-default, #dee0e3);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-secondary, #646a73);
  text-decoration: none;
  transition: all 0.2s;
}
.drawer-admin-link:hover {
  color: var(--accent-blue, #3b82f6);
  border-color: var(--accent-blue, #3b82f6);
}

/* ===== 响应式 ===== */
@media (max-width: 991px) {
  .desktop-menu {
    display: none;
  }
  .hamburger-btn {
    display: flex;
  }
  .brand-slogan {
    display: none;
  }
  .brand-name {
    font-size: 16px;
  }
}
@media (max-width: 767px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
  .footer-bottom {
    justify-content: center;
    text-align: center;
  }
}
</style>
