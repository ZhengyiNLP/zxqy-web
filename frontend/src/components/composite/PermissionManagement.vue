<template>
  <div class="permission-management">
    <div class="perm-header">
      <div class="perm-title">
        <BaseIcon name="shield" :size="18" />
        <span>角色权限管理</span>
      </div>
      <BaseButton variant="primary" size="sm" @click="openCreateRole" v-permission="'system:role:add'">
        <BaseIcon name="plus" :size="14" />
        创建角色
      </BaseButton>
    </div>

    <BaseSpinner v-if="rolesLoading" size="sm" text="加载中..." centered />
    <div v-else class="role-list">
      <div v-for="role in roles" :key="role.id" class="role-card">
        <div class="role-card-header">
          <div class="role-card-info">
            <span class="role-card-name">{{ role.name }}</span>
            <BaseBadge v-if="role.is_system" variant="gray">系统</BaseBadge>
            <BaseBadge v-if="!role.is_active" variant="red">已禁用</BaseBadge>
            <span class="role-card-code">{{ role.code }}</span>
          </div>
          <div class="role-card-actions">
            <BaseButton variant="ghost" size="sm" @click="openEditRole(role)" v-permission="'system:role:edit'">
              <BaseIcon name="pencil" :size="14" /> 编辑权限
            </BaseButton>
            <BaseButton v-if="!role.is_system" variant="danger" size="sm" @click="handleDeleteRole(role)" v-permission="'system:role:delete'">
              <BaseIcon name="trash-2" :size="14" /> 删除
            </BaseButton>
          </div>
        </div>
        <div class="role-card-desc" v-if="role.description">{{ role.description }}</div>
        <div class="role-perms">
          <BaseBadge v-for="perm in (role.permissions || [])" :key="perm.id" variant="blue">{{ perm.name }}</BaseBadge>
          <span v-if="!role.permissions || role.permissions.length === 0" class="no-perms">暂无权限</span>
        </div>
      </div>
    </div>

    <!-- Create/Edit Role Modal -->
    <BaseModal :visible="roleModalVisible" :title="editingRole ? `编辑角色：${editingRole.name}` : '创建角色'" size="wide" @update:visible="roleModalVisible = false">
      <BaseFormGroup label="角色编码" required>
        <BaseInput v-model="roleForm.code" placeholder="如：editor" :disabled="!!editingRole" />
      </BaseFormGroup>
      <BaseFormGroup label="角色名称" required>
        <BaseInput v-model="roleForm.name" placeholder="如：编辑者" />
      </BaseFormGroup>
      <BaseFormGroup label="描述">
        <BaseInput v-model="roleForm.description" placeholder="角色描述（可选）" />
      </BaseFormGroup>
      <BaseFormGroup label="权限分配">
        <div class="perm-groups">
          <div v-for="module in groupedPermissions" :key="module.name" class="perm-group">
            <div class="perm-group-header">
              <BaseCheckbox
                :model-value="isModuleAllChecked(module)"
                @update:model-value="toggleModule(module, $event)"
              />
              <span class="perm-group-name">{{ module.label }}</span>
            </div>
            <div class="perm-group-items">
              <label v-for="perm in module.items" :key="perm.id" class="perm-item">
                <BaseCheckbox
                  :model-value="roleForm.permission_ids.includes(perm.id)"
                  @update:model-value="togglePermission(perm.id, $event)"
                />
                <span>{{ perm.name }}</span>
                <span class="perm-code">{{ perm.module }}{{ perm.resource ? ':' + perm.resource : '' }}:{{ perm.action }}</span>
              </label>
            </div>
          </div>
        </div>
      </BaseFormGroup>
      <template #footer>
        <BaseButton variant="ghost" @click="roleModalVisible = false">取消</BaseButton>
        <BaseButton variant="primary" :disabled="roleSaving" @click="saveRole">
          {{ roleSaving ? '保存中...' : '保存' }}
        </BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'
import { showToast } from '@/utils/api'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseBadge from '@/components/base/BaseBadge.vue'
import BaseSpinner from '@/components/base/BaseSpinner.vue'
import BaseModal from '@/components/base/BaseModal.vue'
import BaseFormGroup from '@/components/base/BaseFormGroup.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseCheckbox from '@/components/base/BaseCheckbox.vue'
import BaseIcon from '@/components/base/BaseIcon.vue'

const roles = ref<any[]>([])
const rolesLoading = ref(false)
const allPermissions = ref<any[]>([])

const roleModalVisible = ref(false)
const editingRole = ref<any>(null)
const roleForm = ref({ code: '', name: '', description: '', permission_ids: [] as number[] })
const roleSaving = ref(false)

// Group permissions by module
const groupedPermissions = computed(() => {
  const groups: Record<string, any> = {}
  for (const perm of allPermissions.value) {
    if (!groups[perm.module]) {
      groups[perm.module] = { name: perm.module, label: perm.module, items: [] }
    }
    groups[perm.module].items.push(perm)
  }
  return Object.values(groups)
})

function isModuleAllChecked(module: any): boolean {
  return module.items.every((p: any) => roleForm.value.permission_ids.includes(p.id))
}

function toggleModule(module: any, checked: boolean) {
  for (const perm of module.items) {
    const idx = roleForm.value.permission_ids.indexOf(perm.id)
    if (checked && idx === -1) {
      roleForm.value.permission_ids.push(perm.id)
    } else if (!checked && idx > -1) {
      roleForm.value.permission_ids.splice(idx, 1)
    }
  }
}

function togglePermission(permId: number, checked: boolean) {
  const idx = roleForm.value.permission_ids.indexOf(permId)
  if (checked && idx === -1) {
    roleForm.value.permission_ids.push(permId)
  } else if (!checked && idx > -1) {
    roleForm.value.permission_ids.splice(idx, 1)
  }
}

async function loadRoles() {
  rolesLoading.value = true
  try {
    const res = await api.get('/permissions/roles')
    roles.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    console.error('Load roles error:', e)
  } finally {
    rolesLoading.value = false
  }
}

async function loadPermissions() {
  try {
    const res = await api.get('/permissions/permissions')
    allPermissions.value = Array.isArray(res.data) ? res.data : []
  } catch (e) {
    console.error('Load permissions error:', e)
  }
}

function openCreateRole() {
  editingRole.value = null
  roleForm.value = { code: '', name: '', description: '', permission_ids: [] }
  loadPermissions()
  roleModalVisible.value = true
}

function openEditRole(role: any) {
  editingRole.value = role
  roleForm.value = {
    code: role.code,
    name: role.name,
    description: role.description || '',
    permission_ids: (role.permissions || []).map((p: any) => p.id)
  }
  loadPermissions()
  roleModalVisible.value = true
}

async function saveRole() {
  if (!roleForm.value.code.trim() || !roleForm.value.name.trim()) {
    showToast('warning', '请填写角色编码和名称')
    return
  }
  roleSaving.value = true
  try {
    if (editingRole.value) {
      await api.put(`/permissions/roles/${editingRole.value.id}`, {
        name: roleForm.value.name,
        description: roleForm.value.description,
        permission_ids: roleForm.value.permission_ids
      })
    } else {
      await api.post('/permissions/roles', {
        code: roleForm.value.code,
        name: roleForm.value.name,
        description: roleForm.value.description,
        permission_ids: roleForm.value.permission_ids
      })
    }
    roleModalVisible.value = false
    loadRoles()
  } catch (e) {
  } finally {
    roleSaving.value = false
  }
}

function handleDeleteRole(role: any) {
  if (!confirm(`确定要删除角色「${role.name}」吗？`)) return
  api.delete(`/permissions/roles/${role.id}`).then(() => {
    loadRoles()
  }).catch(() => {})
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped>
.permission-management {
  padding: 0;
}

.perm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.perm-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.role-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.role-card {
  padding: 16px;
  background: var(--bg-base);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.role-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.role-card-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-card-name {
  font-size: 14px;
  font-weight: 600;
}

.role-card-code {
  font-size: 12px;
  color: var(--text-tertiary);
  font-family: monospace;
}

.role-card-actions {
  display: flex;
  gap: 6px;
}

.role-card-desc {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 8px;
}

.role-perms {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.no-perms {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* Permission groups */
.perm-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.perm-group {
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 10px;
}

.perm-group-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border-subtle);
}

.perm-group-name {
  font-size: 14px;
  font-weight: 600;
  text-transform: capitalize;
}

.perm-group-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 6px;
}

.perm-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
}

.perm-item:hover {
  background: var(--bg-hover);
}

.perm-item span:first-of-type {
  font-size: 13px;
  color: var(--text-primary);
}

.perm-code {
  font-size: 11px;
  color: var(--text-tertiary);
  font-family: monospace;
}
</style>
