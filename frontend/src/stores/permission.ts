import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const usePermissionStore = defineStore('permission', () => {
  const permissions = ref<string[]>([])
  const roles = ref<string[]>([])
  const isSuperAdmin = ref(false)
  const menus = ref<any[]>([])

  function setPermissions(perms: string[]) {
    permissions.value = perms
    localStorage.setItem('permissions', JSON.stringify(perms))
  }

  function setRoles(roleList: string[]) {
    roles.value = roleList
    localStorage.setItem('roles', JSON.stringify(roleList))
  }

  function setIsSuperAdmin(isSuper: boolean) {
    isSuperAdmin.value = isSuper
    localStorage.setItem('isSuperAdmin', JSON.stringify(isSuper))
  }

  async function fetchMenus() {
    const res = await api.get('/menus')
    menus.value = res.data || []
  }

  function hasPermission(perm: string): boolean {
    // 超级管理员拥有所有权限
    if (isSuperAdmin.value) return true
    return permissions.value.includes(perm)
  }

  function hasAnyPermission(perms: string[]): boolean {
    if (isSuperAdmin.value) return true
    return perms.some(p => permissions.value.includes(p))
  }

  function hasAllPermissions(perms: string[]): boolean {
    if (isSuperAdmin.value) return true
    return perms.every(p => permissions.value.includes(p))
  }

  function clearPermissions() {
    permissions.value = []
    roles.value = []
    isSuperAdmin.value = false
    menus.value = []
    localStorage.removeItem('permissions')
    localStorage.removeItem('roles')
    localStorage.removeItem('isSuperAdmin')
  }

  // 初始化时从 localStorage 恢复
  function init() {
    const storedPerms = localStorage.getItem('permissions')
    const storedRoles = localStorage.getItem('roles')
    const storedIsSuperAdmin = localStorage.getItem('isSuperAdmin')

    if (storedPerms) {
      try {
        permissions.value = JSON.parse(storedPerms)
      } catch {
        permissions.value = []
      }
    }

    if (storedRoles) {
      try {
        roles.value = JSON.parse(storedRoles)
      } catch {
        roles.value = []
      }
    }

    if (storedIsSuperAdmin) {
      try {
        isSuperAdmin.value = JSON.parse(storedIsSuperAdmin)
      } catch {
        isSuperAdmin.value = false
      }
    }
  }

  return {
    permissions,
    roles,
    isSuperAdmin,
    menus,
    setPermissions,
    setRoles,
    setIsSuperAdmin,
    fetchMenus,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    clearPermissions,
    init
  }
})
