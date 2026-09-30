import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router/portal-router'
import './style.css'
import { vPermission } from './directives/permission'
import { usePermissionStore } from './stores/permission'
import { useNotificationStore } from './stores/notification'
import { setNotificationStore } from './utils/api'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.directive('permission', vPermission)

const permissionStore = usePermissionStore()
permissionStore.init()

const notificationStore = useNotificationStore()
setNotificationStore(notificationStore)

app.mount('#app')
