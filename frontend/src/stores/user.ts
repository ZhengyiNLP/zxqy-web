import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'
import { usePermissionStore } from './permission'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const username = ref<string>(localStorage.getItem('username') || '')
  const displayName = ref<string>(localStorage.getItem('displayName') || '')
  const userId = ref<number>(parseInt(localStorage.getItem('userId') || '0'))
  const isAdmin = ref<boolean>(localStorage.getItem('isAdmin') === 'true')
  const mustChangePassword = ref<boolean>(localStorage.getItem('mustChangePassword') === 'true')

  const isLoggedIn = computed(() => !!token.value)

  const user = computed(() => ({
    id: userId.value,
    username: username.value,
    display_name: displayName.value,
    is_admin: isAdmin.value
  }))

  function setUser(data: {
    token: string
    user: {
      id: number
      username: string
      display_name?: string
      is_admin: boolean
      must_change_password?: boolean
      is_super_admin?: boolean
      roles?: string[]
      permissions?: string[]
    }
  }) {
    token.value = data.token
    username.value = data.user.username
    userId.value = data.user.id
    displayName.value = data.user.display_name || data.user.username
    isAdmin.value = data.user.is_admin
    mustChangePassword.value = data.user.must_change_password || false

    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.user.username)
    localStorage.setItem('userId', String(data.user.id))
    localStorage.setItem('displayName', data.user.display_name || data.user.username)
    localStorage.setItem('isAdmin', String(data.user.is_admin))
    localStorage.setItem('mustChangePassword', String(data.user.must_change_password || false))

    // 设置权限信息
    const permissionStore = usePermissionStore()
    permissionStore.setPermissions(data.user.permissions || [])
    permissionStore.setRoles(data.user.roles || [])
    // 超级管理员判断：is_super_admin 为 true 或者 is_admin 为 true（向后兼容）
    permissionStore.setIsSuperAdmin(data.user.is_super_admin === true || data.user.is_admin === true)
  }

  function updateUser(data: { display_name?: string }) {
    if (data.display_name !== undefined) {
      displayName.value = data.display_name
      localStorage.setItem('displayName', data.display_name)
    }
  }

  function clearUser() {
    token.value = ''
    username.value = ''
    displayName.value = ''
    userId.value = 0
    isAdmin.value = false
    mustChangePassword.value = false

    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('userId')
    localStorage.removeItem('displayName')
    localStorage.removeItem('isAdmin')
    localStorage.removeItem('mustChangePassword')

    // 清除权限信息
    const permissionStore = usePermissionStore()
    permissionStore.clearPermissions()
  }

  function updateMustChangePassword(val: boolean) {
    mustChangePassword.value = val
    localStorage.setItem('mustChangePassword', String(val))
  }

  async function login(user: string, password: string) {
    const res = await api.post('/auth/login', { username: user, password })
    const data = res.data
    if (data) {
      setUser(data)
      return data
    }
    throw new Error('登录失败')
  }

  async function register(username: string, displayName: string, password: string) {
    const res = await api.post('/auth/register', {
      username,
      display_name: displayName,
      password,
    })
    const data = res.data
    if (data) {
      return data
    }
    throw new Error('注册失败')
  }

  function logout() {
    clearUser()
  }

  return {
    token,
    username,
    displayName,
    userId,
    isAdmin,
    mustChangePassword,
    isLoggedIn,
    user,
    login,
    register,
    logout,
    clearUser,
    updateUser,
    updateMustChangePassword
  }
})
