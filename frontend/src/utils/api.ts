/**
 * API 请求工具
 * 
 * 基于 axios 封装，提供统一的请求/响应拦截器：
 * 
 * 请求拦截器：
 * - 自动添加 Authorization Bearer token
 * 
 * 响应拦截器：
 * - 统一处理业务状态码（code === 0 成功，否则失败）
 * - 自动弹窗通知（POST/PUT/DELETE/PATCH 操作后）
 * - 401 自动重定向到登录页
 * - 错误信息翻译（字段名映射、错误类型转换）
 * 
 * 通知规则：
 * - GET 请求：不弹通知（只是查询数据）
 * - POST/PUT/DELETE/PATCH 成功（code === 0）：弹成功通知
 * - POST/PUT/DELETE/PATCH 业务错误（code !== 0）：弹警告通知
 * - 网络错误/HTTP 错误：弹错误通知
 * 
 * 注意：页面组件不应再手动弹通知，由拦截器统一处理
 */
import axios from 'axios'
import { useUserStore } from '@/stores/user'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

let notificationStoreInstance: any = null

export function setNotificationStore(store: any) {
  notificationStoreInstance = store
}

export function notify(type: 'success' | 'error' | 'warning' | 'info', title: string, message: string) {
  if (notificationStoreInstance) {
    notificationStoreInstance[type](title, message)
  }
}

export function showToast(type: 'success' | 'error' | 'warning' | 'info', message: string) {
  const titles: Record<string, string> = {
    success: '操作成功',
    error: '操作失败',
    warning: '提示',
    info: '信息'
  }
  if (notificationStoreInstance) {
    notificationStoreInstance[type](titles[type], message)
  }
}

function translateFieldName(field: string): string {
  const fieldMap: Record<string, string> = {
    'username': '用户名',
    'password': '密码',
    'display_name': '显示名称',
    'email': '邮箱',
    'name': '名称',
    'description': '描述',
    'role_ids': '角色',
    'content': '内容',
    'title': '标题',
    'date': '日期',
    'body': '请求体',
    'page': '页码',
    'size': '每页数量'
  }
  return fieldMap[field] || field
}

function translateErrorMessage(item: any): string {
  const type = item.type || ''
  const loc = item.loc || []
  const field = loc.length > 1 ? loc[1] : ''
  const fieldName = translateFieldName(field)
  
  const ctx = item.ctx || {}
  
  if (type.includes('string_too_short')) {
    const minLen = ctx.min_length || 0
    return `${fieldName}至少需要${minLen}个字符`
  }
  if (type.includes('string_too_long')) {
    const maxLen = ctx.max_length || 0
    return `${fieldName}最多允许${maxLen}个字符`
  }
  if (type.includes('value_error')) {
    return `${fieldName}格式不正确`
  }
  if (type.includes('type_error')) {
    return `${fieldName}类型不正确`
  }
  if (type.includes('missing')) {
    return `${fieldName}是必填项`
  }
  if (type.includes('not_in')) {
    return `${fieldName}值无效`
  }
  if (type.includes('regex')) {
    return `${fieldName}格式不符合要求`
  }
  if (type.includes('email')) {
    return `${fieldName}不是有效的邮箱地址`
  }
  if (type.includes('password')) {
    return `${fieldName}不符合安全要求`
  }
  if (type.includes('user_not_found')) {
    return '用户不存在'
  }
  if (type.includes('wrong_password')) {
    return '密码错误'
  }
  if (type.includes('duplicate')) {
    return `${fieldName}已存在`
  }
  if (type.includes('foreign_key')) {
    return `${fieldName}关联的数据不存在`
  }
  if (type.includes('permission')) {
    return '没有权限执行此操作'
  }
  
  return item.msg || item.detail || '操作失败'
}

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      ;(config as any)._tokenUsed = token
    }
    // FormData 上传必须让浏览器自动带 multipart 边界，
    // 否则默认的 application/json 会让后端解析不到表单字段
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

let isRedirecting = false

api.interceptors.response.use(
  (response) => {
    const method = (response.config?.method || '').toUpperCase()
    const writeMethods = ['POST', 'PUT', 'DELETE', 'PATCH']
    
    // 写操作：在解包前检查业务状态码，自动弹通知
    if (writeMethods.includes(method)) {
      const data = response.data
      if (data && typeof data === 'object') {
        if (data.code !== undefined) {
          if (data.code === 0) {
            const message = data.message || '操作成功'
            notify('success', '操作成功', message)
          } else {
            const message = data.message || '操作失败'
            notify('warning', '提示', message)
          }
        } else {
          notify('success', '操作成功', '操作成功')
        }
      }
    }

    // 统一解包：将 response.data 从 {code, data, message} 替换为实际业务数据
    // 这样页面中使用 res.data 即可直接拿到业务数据，无需 res.data.data
    const body = response.data
    if (body && typeof body === 'object' && 'code' in body && 'data' in body) {
      response.data = body.data
    }

    return response
  },
  (error) => {
    const method = (error.config?.method || '').toUpperCase()
    const writeMethods = ['POST', 'PUT', 'DELETE', 'PATCH']
    
    if (writeMethods.includes(method)) {
      if (error.response?.data) {
        const data = error.response.data
        let message = '操作失败'
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            message = data.detail.map((item: any) => translateErrorMessage(item)).join(', ')
          } else if (typeof data.detail === 'string') {
            message = data.detail
          } else if (typeof data.detail === 'object') {
            message = translateErrorMessage(data.detail)
          }
        } else if (data.message) {
          message = data.message
        } else {
          message = JSON.stringify(data)
        }
        notify('error', '操作失败', message)
      } else {
        notify('error', '操作失败', '请求失败')
      }
    }
    if (error.response?.status === 401) {
      const url = error.config?.url || ''
      if (url.includes('/auth/login') || url.includes('/auth/register')) {
        return Promise.reject(error)
      }

      const tokenUsed = (error.config as any)?._tokenUsed
      const currentToken = localStorage.getItem('token')

      if (tokenUsed && currentToken && tokenUsed !== currentToken) {
        return Promise.reject(error)
      }

      if (!isRedirecting) {
        isRedirecting = true
        const userStore = useUserStore()
        userStore.clearUser()
        notify('error', '登录已过期', '请重新登录')
        setTimeout(() => {
          window.location.href = '/login'
          isRedirecting = false
        }, 100)
      }
    }
    return Promise.reject(error)
  }
)

export default api

/**
 * 给 HTML 中的 /api/uploads/ 图片 URL 追加 token 查询参数
 * 用于 v-html 渲染的 <img> 标签（无法携带 Authorization 头）
 */
export function addTokenToUploadUrls(html: string): string {
  const token = localStorage.getItem('token')
  if (!token || !html) return html
  return html.replace(/(\/api\/uploads\/[^"'\s>]+)/g, `$1?token=${token}`)
}
