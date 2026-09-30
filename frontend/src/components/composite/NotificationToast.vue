<template>
  <Teleport to="body">
    <TransitionGroup name="notification" tag="div" class="notification-container">
      <div
        v-for="n in notifications"
        :key="n.id"
        class="notification-toast"
        :class="n.type"
        @click="removeNotification(n.id)"
      >
        <div class="notification-icon">
          <span v-if="n.type === 'success'">&#10003;</span>
          <span v-else-if="n.type === 'error'">!</span>
          <span v-else-if="n.type === 'warning'">!</span>
          <span v-else>i</span>
        </div>
        <div class="notification-content">
          <div class="notification-title">{{ n.title }}</div>
          <div class="notification-message" v-if="n.message">{{ n.message }}</div>
        </div>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup lang="ts">
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()
const { notifications, removeNotification } = notificationStore
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.notification-toast {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-width: 280px;
  max-width: 400px;
  padding: 12px 16px;
  background: var(--bg-base, #fff);
  border: 1px solid var(--border-subtle, #e5e6eb);
  border-radius: var(--radius-md, 8px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  cursor: pointer;
  pointer-events: auto;
  transition: all 0.2s;
}

.notification-toast:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.16);
}

.notification-toast.success {
  border-left: 3px solid #10b981;
}
.notification-toast.error {
  border-left: 3px solid #ef4444;
}
.notification-toast.warning {
  border-left: 3px solid #f59e0b;
}
.notification-toast.info {
  border-left: 3px solid #3b82f6;
}

.notification-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 1px;
}

.notification-toast.success .notification-icon {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}
.notification-toast.error .notification-icon {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}
.notification-toast.warning .notification-icon {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}
.notification-toast.info .notification-icon {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #1f2329);
}

.notification-message {
  font-size: 13px;
  color: var(--text-secondary, #646a73);
  margin-top: 2px;
  word-break: break-word;
}

.notification-enter-active {
  transition: all 0.3s ease;
}
.notification-leave-active {
  transition: all 0.2s ease;
}
.notification-enter-from {
  opacity: 0;
  transform: translateX(60px);
}
.notification-leave-to {
  opacity: 0;
  transform: translateX(60px);
}
</style>
