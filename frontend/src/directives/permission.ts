import type { Directive, DirectiveBinding } from 'vue'
import { usePermissionStore } from '@/stores/permission'

/**
 * 权限指令 v-permission
 * 
 * 用法：
 * - 单个权限：v-permission="'project:create'"
 * - 多个权限（满足任一）：v-permission="['project:update', 'project:delete']"
 * - 多个权限（全部满足）：v-permission="{ all: ['project:read', 'project:create'] }"
 */
export const vPermission: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    checkPermission(el, binding)
  },
  updated(el: HTMLElement, binding: DirectiveBinding) {
    checkPermission(el, binding)
  }
}

function checkPermission(el: HTMLElement, binding: DirectiveBinding) {
  const { value } = binding
  const permissionStore = usePermissionStore()

  if (!value) return

  let hasPermission = false

  if (typeof value === 'string') {
    // 单个权限字符串
    hasPermission = permissionStore.hasPermission(value)
  } else if (Array.isArray(value)) {
    // 权限数组，满足任一即可
    hasPermission = permissionStore.hasAnyPermission(value)
  } else if (typeof value === 'object' && value !== null) {
    if (value.all && Array.isArray(value.all)) {
      // 需要满足所有权限
      hasPermission = permissionStore.hasAllPermissions(value.all)
    } else if (value.any && Array.isArray(value.any)) {
      // 满足任一权限
      hasPermission = permissionStore.hasAnyPermission(value.any)
    }
  }

  if (!hasPermission) {
    // 使用 CSS 隐藏元素，保存原始 display 以便恢复
    if (!el.hasAttribute('data-permission-hidden')) {
      el.setAttribute('data-permission-hidden', 'true')
      el.setAttribute('data-original-display', el.style.display || '')
    }
    el.style.display = 'none'
  } else {
    // 有权限时恢复原始 display
    if (el.hasAttribute('data-permission-hidden')) {
      const originalDisplay = el.getAttribute('data-original-display') || ''
      el.style.display = originalDisplay
      el.removeAttribute('data-permission-hidden')
      el.removeAttribute('data-original-display')
    }
  }
}

// 辅助函数：在 setup 中使用
export function usePermission() {
  const permissionStore = usePermissionStore()

  return {
    hasPermission: permissionStore.hasPermission,
    hasAnyPermission: permissionStore.hasAnyPermission,
    hasAllPermissions: permissionStore.hasAllPermissions
  }
}
