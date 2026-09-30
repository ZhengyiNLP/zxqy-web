<template>
  <BaseSettingsLayout v-model="activeTab" title="设置" :groups="navGroups">

      <!-- Profile Tab -->
      <BaseSection v-if="activeTab === 'profile'" variant="card" title="个人资料">
        <BaseFormGroup label="用户名">
          <BaseInput :model-value="userStore.user?.username" disabled />
        </BaseFormGroup>
        <BaseFormGroup label="显示名称">
          <BaseInput v-model="profileForm.display_name" placeholder="输入显示名称" />
        </BaseFormGroup>
        <BaseFormGroup label="角色">
          <div class="role-tags">
            <BaseBadge v-for="role in currentUserRoles" :key="role" variant="blue">{{ role }}</BaseBadge>
            <BaseBadge v-if="currentUserRoles.length === 0" variant="gray">普通用户</BaseBadge>
          </div>
        </BaseFormGroup>
        <div class="form-actions">
          <BaseButton variant="primary" size="sm" @click="handleUpdateProfile" :disabled="profileLoading">
            {{ profileLoading ? '保存中...' : '保存修改' }}
          </BaseButton>
        </div>
      </BaseSection>

      <!-- Password Tab -->
      <BaseSection v-if="activeTab === 'password'" variant="card" title="修改密码">
        <BaseFormGroup label="当前密码">
          <BaseInput type="password" v-model="passwordForm.old_password" placeholder="输入当前密码" />
        </BaseFormGroup>
        <BaseFormGroup label="新密码">
          <BaseInput type="password" v-model="passwordForm.new_password" placeholder="输入新密码（至少6位）" />
        </BaseFormGroup>
        <BaseFormGroup label="确认新密码">
          <BaseInput type="password" v-model="passwordForm.confirm_password" placeholder="再次输入新密码" />
        </BaseFormGroup>
        <div class="form-actions">
          <BaseButton variant="primary" size="sm" @click="handleChangePassword" :disabled="passwordLoading">
            {{ passwordLoading ? '修改中...' : '修改密码' }}
          </BaseButton>
        </div>
      </BaseSection>

      <!-- Users Tab (Admin Only) -->
      <BaseSection v-if="activeTab === 'users'" title="用户管理" description="管理系统用户账号，创建新用户或删除现有用户">
        <template #actions>
          <BaseButton variant="primary" size="sm" @click="openCreateUser">
            <BaseIcon name="plus" :size="14" />
            创建用户
          </BaseButton>
        </template>

        <BaseSpinner v-if="usersLoading" size="sm" text="加载中..." centered />
        <div v-else>
          <div v-for="user in users" :key="user.id" class="user-row">
            <div class="user-info">
              <BaseAvatar :name="user.display_name || user.username" />
              <div>
                <div class="user-name">{{ user.display_name || user.username }}</div>
                <div class="user-username">@{{ user.username }}</div>
              </div>
            </div>
            <div class="user-roles">
              <template v-if="user.roles && user.roles.length > 0">
                <BaseBadge v-for="role in user.roles.slice(0, 3)" :key="role.id" variant="blue">{{ role.name }}</BaseBadge>
                <BaseBadge v-if="user.roles.length > 3" variant="gray">+{{ user.roles.length - 3 }}更多</BaseBadge>
              </template>
              <BaseBadge v-else-if="user.is_admin" variant="blue">管理员</BaseBadge>
              <BaseBadge v-else variant="gray">普通用户</BaseBadge>
            </div>
            <div class="user-actions">
              <BaseButton v-if="!isSuperAdminUser(user)" variant="ghost" size="sm" @click="openEditUser(user)"><BaseIcon name="pencil" :size="14" /> 编辑</BaseButton>
              <BaseButton v-if="!user.is_admin" variant="danger" size="sm" @click="handleDeleteUser(user)"><BaseIcon name="trash-2" :size="14" /> 删除</BaseButton>
              <span v-else class="action-placeholder"></span>
            </div>
          </div>
          <BaseEmptyState v-if="!usersLoading && users.length === 0" title="暂无用户" />
        </div>
      </BaseSection>

      <!-- Sys Config Tab (Admin Only) -->
      <BaseSection v-if="activeTab === 'configs'" title="参数设置" description="系统运行参数，修改即时生效（备注注明需重启的除外），无需修改代码">
        <template #actions>
          <BaseButton variant="primary" size="sm" @click="openCreateConfig">
            <BaseIcon name="plus" :size="14" />
            新增参数
          </BaseButton>
        </template>
        <BaseSpinner v-if="configsLoading" size="sm" text="加载中..." centered />
        <BaseCrudList v-else
          :columns="configColumns"
          :data="configs"
          row-key="id"
          :total="configs.length"
          :show-pagination="false"
          :show-refresh="false"
          :show-density-toggle="false"
        >
          <template #cell-config_value="{ row }">
            <span class="config-value-cell" :title="row.config_value">{{ row.config_value }}</span>
          </template>
          <template #cell-config_type="{ row }">
            <BaseBadge :variant="row.config_type === 'Y' ? 'blue' : 'gray'">{{ row.config_type === 'Y' ? '内置' : '自定义' }}</BaseBadge>
          </template>
          <template #cell-remark="{ row }">
            <span class="config-remark-cell" :title="row.remark">{{ row.remark }}</span>
          </template>
          <template #cell-action="{ row }">
            <div class="config-actions">
              <BaseButton variant="ghost" size="sm" @click="openEditConfig(row)"><BaseIcon name="pencil" :size="14" /> 编辑</BaseButton>
              <BaseButton v-if="row.config_type !== 'Y'" variant="danger" size="sm" @click="deleteConfig(row)"><BaseIcon name="trash-2" :size="14" /> 删除</BaseButton>
            </div>
          </template>
        </BaseCrudList>
      </BaseSection>

      <!-- Permissions Tab (Admin Only) -->
      <BaseSection v-if="activeTab === 'permissions'">
        <PermissionManagement />
      </BaseSection>

    <!-- Create User Modal -->
    <BaseModal :visible="createUserVisible" title="创建用户" @update:visible="createUserVisible = false">
      <BaseFormGroup label="用户名" required :error="newUserErrors.username">
        <BaseInput v-model="newUser.username" placeholder="输入用户名" :class="{ 'input-error': newUserErrors.username }" />
      </BaseFormGroup>
      <BaseFormGroup label="显示名称">
        <BaseInput v-model="newUser.display_name" placeholder="输入显示名称（可选）" />
      </BaseFormGroup>
      <BaseFormGroup label="密码" required :error="newUserErrors.password">
        <BaseInput type="password" v-model="newUser.password" placeholder="输入密码" :class="{ 'input-error': newUserErrors.password }" />
      </BaseFormGroup>
      <BaseFormGroup label="角色">
        <div class="role-checkboxes">
          <label v-for="role in availableRoles" :key="role.id" class="role-checkbox">
            <BaseCheckbox :model-value="newUser.role_ids.includes(role.id)" @update:model-value="toggleRole(newUser.role_ids, role.id)" />
            <span>{{ role.name }}</span>
            <span class="role-desc">{{ role.description }}</span>
          </label>
        </div>
      </BaseFormGroup>
      <template #footer>
        <BaseButton variant="ghost" @click="createUserVisible = false">取消</BaseButton>
        <BaseButton variant="primary" :disabled="createUserLoading" @click="handleCreateUser">
          {{ createUserLoading ? '创建中...' : '确认创建' }}
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Edit User Modal -->
    <BaseModal :visible="editUserVisible" :title="`编辑用户：${editingUser?.display_name || editingUser?.username}`" @update:visible="editUserVisible = false">
      <BaseFormGroup label="用户名">
        <BaseInput :model-value="editingUser?.username" disabled />
      </BaseFormGroup>
      <BaseFormGroup label="显示名称">
        <BaseInput v-model="editingUserForm.display_name" placeholder="输入显示名称" />
      </BaseFormGroup>
      <BaseFormGroup label="角色">
        <div class="role-checkboxes">
          <label v-for="role in roles" :key="role.id" class="role-checkbox">
            <BaseCheckbox :model-value="editingUserForm.role_ids.includes(role.id)" @update:model-value="toggleRole(editingUserForm.role_ids, role.id)" />
            <span>{{ role.name }}</span>
            <span class="role-desc">{{ role.description }}</span>
          </label>
        </div>
      </BaseFormGroup>
      <template #footer>
        <BaseButton variant="ghost" @click="editUserVisible = false">取消</BaseButton>
        <BaseButton variant="primary" :disabled="editUserLoading" @click="handleEditUser">
          {{ editUserLoading ? '保存中...' : '保存修改' }}
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Sys Config Modal -->
    <BaseModal :visible="configModalVisible" :title="editingSysConfig ? '编辑参数' : '新增参数'" @update:visible="configModalVisible = false">
      <BaseFormGroup label="配置名称" required>
        <BaseInput v-model="configForm.config_name" placeholder="如：系统超时时间（秒）" />
      </BaseFormGroup>
      <BaseFormGroup label="配置键" required>
        <BaseInput v-model="configForm.config_key" placeholder="如：system.timeout" :class="{ disabled: !!editingSysConfig }" :disabled="!!editingSysConfig" />
      </BaseFormGroup>
      <BaseFormGroup label="配置值">
        <BaseInput v-model="configForm.config_value" type="textarea" class="config-value-input" rows="4" placeholder="配置值（字符串）" />
      </BaseFormGroup>
      <BaseFormGroup label="备注">
        <BaseInput v-model="configForm.remark" placeholder="用途说明（可选）" />
      </BaseFormGroup>
      <template #footer>
        <BaseButton variant="ghost" @click="configModalVisible = false">取消</BaseButton>
        <BaseButton variant="primary" :disabled="configSaving || !configForm.config_name.trim() || (!editingSysConfig && !configForm.config_key.trim())" @click="saveConfig">
          {{ configSaving ? '保存中...' : '保存' }}
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Delete Confirm Modal -->
    <BaseModal :visible="deleteConfirmVisible" :title="deleteConfirmConfig.title" @update:visible="deleteConfirmVisible = false">
      <div class="delete-confirm-content">
        <BaseIcon name="alert-triangle" :size="48" color="var(--accent-red)" :stroke-width="1.5" style="margin-bottom:16px;" />
        <p>{{ deleteConfirmConfig.message }}</p>
        <p class="delete-confirm-tip">此操作不可撤销</p>
      </div>
      <template #footer>
        <BaseButton variant="ghost" @click="deleteConfirmVisible = false">取消</BaseButton>
        <BaseButton variant="danger" @click="handleDeleteConfirm">确认</BaseButton>
      </template>
    </BaseModal>

  </BaseSettingsLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from '@/utils/api'
import api from '../utils/api'
import { useUserStore } from '../stores/user'
import { usePermissionStore } from '../stores/permission'

import BaseSettingsLayout from '../components/composite/BaseSettingsLayout.vue'
import PermissionManagement from '../components/composite/PermissionManagement.vue'
import BaseCrudList from '@/components/composite/BaseCrudList.vue'
import BaseSection from '../components/composite/BaseSection.vue'
import BaseModal from '../components/base/BaseModal.vue'
import BaseButton from '../components/base/BaseButton.vue'
import BaseFormGroup from '../components/base/BaseFormGroup.vue'
import BaseBadge from '../components/base/BaseBadge.vue'
import BaseEmptyState from '../components/base/BaseEmptyState.vue'
import BaseAvatar from '../components/base/BaseAvatar.vue'
import BaseSpinner from '../components/base/BaseSpinner.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseCheckbox from '@/components/base/BaseCheckbox.vue'
import BaseIcon from '@/components/base/BaseIcon.vue'

const userStore = useUserStore()
const permissionStore = usePermissionStore()
const route = useRoute()
const router = useRouter()

const currentUserRoles = computed(() => {
  return permissionStore.roles || []
})

function isSuperAdminUser(user: any) {
  return user.username === 'admin'
}

const availableRoles = computed(() => {
  return roles.value.filter((r: any) => r.code !== 'super_admin')
})

// 设置页面图标映射
const settingsIconMap: Record<string, string> = {
  'profile': 'user',
  'password': 'lock',
  'users': 'users',
  'configs': 'sliders-horizontal',
  'permissions': 'shield',
}

// Nav groups for BaseSettingsLayout - 从后端菜单数据构建
const navGroups = computed(() => {
  const settingsMenu = permissionStore.menus
    .flatMap(g => (g.items || []))
    .find(item => item.key === 'settings')

  const children = settingsMenu?.children || []

  const personalItems = children
    .filter((item: any) => !item.permission)
    .map((item: any) => ({
      key: item.key,
      label: item.label,
      icon: settingsIconMap[item.key] || '',
      visible: true
    }))

  const globalItems = children
    .filter((item: any) => !!item.permission)
    .map((item: any) => ({
      key: item.key,
      label: item.label,
      icon: settingsIconMap[item.key] || '',
      visible: true
    }))

  const groups: any[] = []

  if (personalItems.length > 0) {
    groups.push({
      label: '个人设置',
      items: personalItems
    })
  }

  if (globalItems.length > 0) {
    groups.push({
      label: '全局设置',
      items: globalItems
    })
  }

  return groups
})

// Active tab with URL sync
const activeTab = ref(route.params.tab || 'profile')

watch(() => route.params.tab, (newTab) => {
  if (newTab && newTab !== activeTab.value) {
    activeTab.value = newTab
  }
})

watch(activeTab, (newTab) => {
  const currentTab = route.params.tab
  if (currentTab !== newTab) {
    router.push('/settings/' + newTab)
  }
})

// Profile
const profileForm = ref({ display_name: '' })
const profileLoading = ref(false)

// Password
const passwordForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const passwordLoading = ref(false)

// Users (admin)
const users = ref<any[]>([])
const usersLoading = ref(false)
const createUserVisible = ref(false)
const createUserLoading = ref(false)
const newUser = ref({ username: '', display_name: '', password: '', role_ids: [] as number[] })
const newUserErrors = ref<any>({})
const roles = ref<any[]>([])
const editUserVisible = ref(false)
const editUserLoading = ref(false)
const editingUser = ref<any>(null)
const editingUserForm = ref({ display_name: '', role_ids: [] as number[] })

// ===== 系统参数（sys_config） =====
const configs = ref<any[]>([])
const configsLoading = ref(false)
const configModalVisible = ref(false)
const editingSysConfig = ref<any>(null)
const configForm = ref({ config_name: '', config_key: '', config_value: '', remark: '' })
const configSaving = ref(false)

const configColumns = [
  { key: 'config_name', label: '配置名称', width: '160px' },
  { key: 'config_key', label: '配置键', width: '220px' },
  { key: 'config_value', label: '配置值' },
  { key: 'config_type', label: '类型', width: '70px' },
  { key: 'remark', label: '备注', width: '200px' },
  { key: 'action', label: '操作', width: '130px' },
]

async function loadConfigs() {
  configsLoading.value = true
  try {
    const res = await api.get('/settings/sys-configs')
    configs.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    console.error('Failed to load configs', e)
  } finally {
    configsLoading.value = false
  }
}

function openCreateConfig() {
  editingSysConfig.value = null
  configForm.value = { config_name: '', config_key: '', config_value: '', remark: '' }
  configModalVisible.value = true
}

function openEditConfig(row: any) {
  editingSysConfig.value = row
  configForm.value = {
    config_name: row.config_name,
    config_key: row.config_key,
    config_value: row.config_value || '',
    remark: row.remark || '',
  }
  configModalVisible.value = true
}

async function saveConfig() {
  configSaving.value = true
  try {
    if (editingSysConfig.value) {
      await api.put(`/settings/sys-configs/${editingSysConfig.value.id}`, {
        config_name: configForm.value.config_name,
        config_value: configForm.value.config_value,
        remark: configForm.value.remark,
      })
    } else {
      await api.post('/settings/sys-configs', { ...configForm.value })
    }
    configModalVisible.value = false
    loadConfigs()
  } catch { /* 拦截器已弹提示 */ } finally {
    configSaving.value = false
  }
}

function deleteConfig(row: any) {
  showDeleteConfirm('确认删除', `确定要删除参数「${row.config_name}」吗？`, async () => {
    await api.delete(`/settings/sys-configs/${row.id}`)
    loadConfigs()
  })
}

// Delete confirm
const deleteConfirmVisible = ref(false)
const deleteConfirmConfig = ref<any>({ title: '', message: '', onConfirm: null })

function showDeleteConfirm(title: string, message: string, onConfirm: any) {
  deleteConfirmConfig.value = { title, message, onConfirm }
  deleteConfirmVisible.value = true
}

async function handleDeleteConfirm() {
  const config = deleteConfirmConfig.value
  if (config.onConfirm) {
    try {
      await config.onConfirm()
    } catch (e) {
    }
  }
  deleteConfirmVisible.value = false
  deleteConfirmConfig.value = { title: '', message: '', onConfirm: null }
}

// Load data when tab changes
watch(activeTab, (tab) => {
  if (tab === 'users') { loadUsers(); loadRoles() }
  if (tab === 'configs') loadConfigs()
  if (tab === 'profile') {
    profileForm.value.display_name = userStore.user?.display_name || ''
  }
})

// Load users
async function loadUsers() {
  usersLoading.value = true
  try {
    const res = await api.get('/users')
    const data = res.data
    users.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('Load users error:', e)
  } finally {
    usersLoading.value = false
  }
}

// Load roles
async function loadRoles() {
  try {
    const res = await api.get('/permissions/roles')
    const data = res.data
    roles.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('加载角色失败', e)
  }
}

function openCreateUser() {
  newUser.value = { username: '', display_name: '', password: '', role_ids: [] }
  loadRoles()
  createUserVisible.value = true
}

async function handleCreateUser() {
  newUserErrors.value = {}
  if (!newUser.value.username) newUserErrors.value.username = '请输入用户名'
  if (!newUser.value.password) newUserErrors.value.password = '请输入密码'
  if (Object.keys(newUserErrors.value).length > 0) return

  createUserLoading.value = true
  try {
    await api.post('/users', {
      ...newUser.value,
      role_ids: newUser.value.role_ids.length > 0 ? newUser.value.role_ids : null
    })
    createUserVisible.value = false
    newUser.value = { username: '', display_name: '', password: '', role_ids: [] }
    loadUsers()
  } catch (e) {
  } finally {
    createUserLoading.value = false
  }
}

function openEditUser(user: any) {
  editingUser.value = user
  editingUserForm.value = {
    display_name: user.display_name || '',
    role_ids: (user.roles || []).map((r: any) => r.id)
  }
  loadRoles()
  editUserVisible.value = true
}

function toggleRole(roleIds: number[], roleId: number) {
  const index = roleIds.indexOf(roleId)
  if (index > -1) {
    roleIds.splice(index, 1)
  } else {
    roleIds.push(roleId)
  }
}

async function handleEditUser() {
  editUserLoading.value = true
  try {
    await api.put('/users/' + editingUser.value.id, {
      display_name: editingUserForm.value.display_name,
      role_ids: editingUserForm.value.role_ids.length > 0 ? editingUserForm.value.role_ids : null
    })
    editUserVisible.value = false
    loadUsers()
  } catch (e) {
  } finally {
    editUserLoading.value = false
  }
}

function handleDeleteUser(user: any) {
  showDeleteConfirm('确认删除', '确定要删除用户「' + user.username + '」吗？', async () => {
    await api.delete('/users/' + user.id)
    loadUsers()
  })
}

// Update profile
async function handleUpdateProfile() {
  profileLoading.value = true
  try {
    await api.put('/users/me', { display_name: profileForm.value.display_name })
    userStore.updateUser({ display_name: profileForm.value.display_name })
  } catch (e) {
  } finally {
    profileLoading.value = false
  }
}

// Change password
async function handleChangePassword() {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password) {
    showToast('warning', '请填写完整')
    return
  }
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    showToast('warning', '两次密码不一致')
    return
  }
  if (passwordForm.value.new_password.length < 6) {
    showToast('warning', '密码至少6位')
    return
  }
  passwordLoading.value = true
  try {
    await api.put('/users/me/password', { old_password: passwordForm.value.old_password, new_password: passwordForm.value.new_password })
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (e) {
  } finally {
    passwordLoading.value = false
  }
}

// Init
onMounted(() => {
  profileForm.value.display_name = userStore.user?.display_name || ''
  if (activeTab.value === 'users') loadUsers()
})
</script>

<style scoped>
/* User List */
.user-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
  transition: border-color var(--duration-fast);
}
.user-row:hover {
  border-color: var(--border-emphasis);
  box-shadow: var(--shadow-sm);
}
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}
.user-name {
  font-size: 14px;
  font-weight: 500;
}
.user-username {
  font-size: 12px;
  color: var(--text-tertiary);
}
.user-roles {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  flex-wrap: wrap;
  margin-right: 12px;
}
.user-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  width: 140px;
  justify-content: flex-end;
}
.action-placeholder {
  width: 44px;
}

.role-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.role-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.role-checkbox {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--duration-fast);
}
.role-checkbox:hover {
  border-color: var(--accent-blue);
  background: var(--bg-hover);
}
.role-checkbox :deep(.base-checkbox-input) {
  margin-top: 2px;
  flex-shrink: 0;
}
.role-checkbox span:first-of-type {
  font-size: 14px;
  font-weight: 500;
  flex-shrink: 0;
}
.role-desc {
  font-size: 12px;
  color: var(--text-tertiary);
  flex: 1;
}

:deep(.base-input.disabled) {
  background: var(--bg-deep);
  color: var(--text-tertiary);
  cursor: not-allowed;
}

/* 系统参数 */
.config-value-cell,
.config-remark-cell {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.config-value-cell {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
}

.config-actions {
  display: flex;
  gap: 6px;
}

:deep(.config-value-input) {
  resize: vertical;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.6;
}

.delete-confirm-content {
  text-align: center;
  padding: 24px 0;
}
.delete-confirm-content .base-icon {
  display: block;
  margin: 0 auto 16px;
}
.delete-confirm-content p {
  font-size: 14px;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}
.delete-confirm-tip {
  font-size: 12px;
  color: var(--text-tertiary) !important;
}

.form-actions {
  margin-top: 8px;
}
</style>
