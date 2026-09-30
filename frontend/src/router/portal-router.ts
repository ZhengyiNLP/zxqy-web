/**
 * 路由配置 - 门户前台 + 管理后台双布局
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import { resetRoutes } from './index'

// ====== 门户前台路由（公开访问）======
const portalRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/PortalLayout.vue'),
    children: [
      { path: '', name: 'PortalHome', component: () => import('@/views/portal/Home.vue') },
      { path: 'articles', name: 'ArticleList', component: () => import('@/views/portal/ArticleList.vue') },
      { path: 'articles/:id', name: 'ArticleDetail', component: () => import('@/views/portal/ArticleDetail.vue') },
      { path: 'products', name: 'ProductList', component: () => import('@/views/portal/ProductList.vue') },
      { path: 'products/:id', name: 'ProductDetail', component: () => import('@/views/portal/ProductDetail.vue') },
      { path: 'about', name: 'About', component: () => import('@/views/portal/About.vue') },
      { path: 'culture', name: 'Culture', component: () => import('@/views/portal/Culture.vue') },
      { path: 'contact', name: 'Contact', component: () => import('@/views/portal/Contact.vue') },
    ]
  }
]

// ====== 管理后台路由（需登录）======
const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    component: () => import('@/components/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'articles', name: 'AdminArticles', component: () => import('@/views/admin/ArticleManage.vue') },
      { path: 'products', name: 'AdminProducts', component: () => import('@/views/admin/ProductManage.vue') },
      { path: 'categories', name: 'AdminCategories', component: () => import('@/views/admin/CategoryManage.vue') },
      { path: 'pages', name: 'AdminPages', component: () => import('@/views/admin/PageManage.vue') },
      { path: 'messages', name: 'AdminMessages', component: () => import('@/views/admin/MessageManage.vue') },
      { path: 'banners', name: 'AdminBanners', component: () => import('@/views/admin/BannerManage.vue') },
      { path: 'friend-links', name: 'AdminFriendLinks', component: () => import('@/views/admin/FriendLinkManage.vue') },
      { path: 'site-config', name: 'AdminSiteConfig', component: () => import('@/views/admin/SiteConfig.vue') },
    ]
  }
]

// ====== 认证路由 ======
const authRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/views/ChangePassword.vue'),
    meta: { requiresAuth: true, noLayout: true }
  },
]

const allRoutes = [...portalRoutes, ...authRoutes, ...adminRoutes]

const router = createRouter({
  history: createWebHistory(),
  routes: allRoutes
})

// 导航守卫
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()

  // 门户路由和登录页直接放行
  if (to.path === '/' || to.path.startsWith('/articles') || to.path.startsWith('/products') ||
      to.path === '/about' || to.path === '/culture' || to.path === '/contact' || to.path === '/login') {
    next()
    return
  }

  // 管理后台路由需要认证
  if (to.path.startsWith('/admin')) {
    if (!userStore.isLoggedIn) {
      next('/login')
      return
    }
    if (userStore.mustChangePassword && to.path !== '/change-password') {
      next('/change-password')
      return
    }
  }

  // 改密码页需要登录
  if (to.path === '/change-password' && !userStore.isLoggedIn) {
    next('/login')
    return
  }

  next()
})

export default router
export { resetRoutes }
