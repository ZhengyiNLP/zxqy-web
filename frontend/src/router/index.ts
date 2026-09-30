/**
 * 动态路由配置
 * 
 * 借鉴 RuoYi 框架，采用「后端驱动菜单 + 前端动态路由」模式：
 * 
 * 核心流程：
 * 1. 用户登录 → 请求后端 GET /api/menus 获取权限菜单树
 * 2. 根据菜单树动态 router.addRoute() 注册路由
 * 3. 无权限的页面不存在于路由表，用户看不到也访问不到
 * 
 * 路由结构：
 * - 静态路由：login/register/change-password/403（始终可用）
 * - 动态路由：根据用户权限从后端获取后注册到 Layout 下
 * 
 * 导航守卫逻辑：
 * 1. 公开路由直接放行（但已登录用户会重定向到首页）
 * 2. 未登录用户重定向到登录页
 * 3. 首次访问 → 加载菜单 → 动态注册路由 → 重新导航
 * 4. 路由权限检查 → 无权限重定向到 403
 */
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'

// 静态路由 - 始终可用，无需权限
const staticRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('@/views/ChangePassword.vue'),
    meta: { requiresAuth: true, noLayout: true }
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/Forbidden.vue'),
    meta: { requiresAuth: true, noLayout: true }
  },
  {
    path: '/',
    component: () => import('@/components/Layout.vue'),
    name: 'Layout',
    meta: { requiresAuth: true },
    children: []  // 动态路由将在这里添加
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: staticRoutes
})

// 动态路由映射表 - key -> 路由定义
// 开发者在此添加业务路由，key 需与后端 ALL_MENUS 中的 item.key 对应
const dynamicRouteMap: Record<string, RouteRecordRaw> = {
  'home': { path: 'home', name: 'Home', component: () => import('@/views/Home.vue'), meta: {} },
  'settings': { path: 'settings/:tab?', name: 'Settings', component: () => import('@/views/Settings.vue'), meta: {} },
}

// 记录已添加的动态路由名称，便于清理
let addedRouteNames: string[] = []
let routesInitialized = false

// 获取第一个可用菜单项的路径（后端菜单 path 自带前导斜杠，避免拼出 //daily）
function getFirstMenuPath(menus: any[]): string {
  if (menus.length > 0 && menus[0].items?.length > 0) {
    const p = menus[0].items[0].path
    return p.startsWith('/') ? p : '/' + p
  }
  return '/settings/profile'
}

// 根据后端菜单数据动态添加路由
export function addDynamicRoutes(menus: any[]) {
  // 提取菜单中所有路由 key
  const routeKeys = new Set<string>()
  for (const group of menus) {
    for (const item of group.items || []) {
      routeKeys.add(item.key)
    }
  }

  // 添加对应的动态路由到 Layout 下
  for (const key of routeKeys) {
    if (dynamicRouteMap[key]) {
      router.addRoute('Layout', dynamicRouteMap[key])
      addedRouteNames.push(dynamicRouteMap[key].name as string)
    }
  }

  // 添加默认首页重定向
  const firstPath = getFirstMenuPath(menus)
  router.addRoute('Layout', {
    path: '',
    name: 'LayoutDefaultRedirect',
    redirect: firstPath
  })
  addedRouteNames.push('LayoutDefaultRedirect')

  // 添加 catch-all 重定向（必须在最后添加）
  router.addRoute({
    path: '/:pathMatch(.*)*',
    name: 'CatchAllRedirect',
    redirect: firstPath
  })
  addedRouteNames.push('CatchAllRedirect')

  routesInitialized = true
}

// 重置动态路由状态（用于登出时）
export function resetRoutes() {
  // 移除所有动态添加的路由
  for (const name of addedRouteNames) {
    try {
      router.removeRoute(name)
    } catch {
      // 忽略不存在的路由
    }
  }
  addedRouteNames = []
  routesInitialized = false
}

// 导航守卫
router.beforeEach(async (to, _from, next) => {
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()

  // 公开路由
  if (to.meta.requiresAuth === false) {
    if (userStore.isLoggedIn && !userStore.mustChangePassword) {
      // 登录后访问公开页面，重定向到首页
      if (!routesInitialized) {
        await permissionStore.fetchMenus()
        addDynamicRoutes(permissionStore.menus)
      }
      next(getFirstMenuPath(permissionStore.menus))
    } else if (userStore.isLoggedIn && userStore.mustChangePassword) {
      next('/change-password')
    } else {
      next()
    }
    return
  }

  // 检查认证
  if (!userStore.isLoggedIn) {
    next('/login')
    return
  }

  // 检查是否必须修改密码
  if (userStore.mustChangePassword && to.path !== '/change-password') {
    next('/change-password')
    return
  }

  // 必须改密码的用户：直接放行改密页，跳过菜单/动态路由加载
  // （后端在改密前会拦截 /api/menus 等接口，加载必然失败，否则会被踢回登录页卡死）
  if (userStore.mustChangePassword && to.path === '/change-password') {
    next()
    return
  }

  // 如果动态路由尚未加载，获取菜单并添加路由
  if (!routesInitialized && userStore.isLoggedIn) {
    try {
      await permissionStore.fetchMenus()
      addDynamicRoutes(permissionStore.menus)
      // 注意：必须按 path 重新导航，不能用 { ...to }（其中 name 已被解析，
      // 按 name 导航会绕过 '' 子路由的重定向，导致登录后停在空白 Layout）
      next({ path: to.path, query: to.query, hash: to.hash, replace: true })
      return
    } catch (e) {
      console.error('Failed to load menus:', e)
      next('/login')
      return
    }
  }

  // 检查目标路由的权限
  const requiredPermissions = to.meta.permissions as string[] | undefined
  if (requiredPermissions && requiredPermissions.length > 0) {
    const hasPermission = permissionStore.hasAnyPermission(requiredPermissions)
    if (!hasPermission) {
      next('/403')
      return
    }
  }

  next()
})

export default router
