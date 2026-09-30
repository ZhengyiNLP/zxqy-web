import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: number
}

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])

  function addNotification(type: Notification['type'], title: string, message: string) {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
    notifications.value.push({
      id,
      type,
      title,
      message,
      timestamp: Date.now()
    })

    setTimeout(() => {
      removeNotification(id)
    }, 5000)

    return id
  }

  function removeNotification(id: string) {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  function success(title: string, message: string) {
    return addNotification('success', title, message)
  }

  function error(title: string, message: string) {
    return addNotification('error', title, message)
  }

  function warning(title: string, message: string) {
    return addNotification('warning', title, message)
  }

  function info(title: string, message: string) {
    return addNotification('info', title, message)
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    success,
    error,
    warning,
    info
  }
})
