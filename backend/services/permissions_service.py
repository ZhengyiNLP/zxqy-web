"""
权限管理服务层

功能描述：
- 角色 CRUD 操作
- 权限过滤与匹配
- 动态菜单生成（根据用户权限过滤 ALL_MENUS）

关键依赖：
- sqlalchemy.orm.Session
- models.Permission/Role/RolePermission/UserRole/User
- permission_middleware.get_user_permissions/has_permission
"""
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from utils.response import ok, fail
from models import Role, Permission, RolePermission, UserRole, User


def get_permissions(db: Session, module: Optional[str] = None) -> List[dict]:
    """获取所有权限列表"""
    query = db.query(Permission).filter(Permission.is_active == True)

    if module:
        query = query.filter(Permission.module == module)

    permissions = query.order_by(Permission.module, Permission.action).all()
    return [
        {
            "id": p.id,
            "module": p.module,
            "resource": p.resource,
            "action": p.action,
            "name": p.name,
            "description": p.description,
            "is_active": p.is_active,
            "created_at": p.created_at,
        }
        for p in permissions
    ]


def get_modules(db: Session) -> List[str]:
    """获取所有权限模块列表"""
    modules = db.query(Permission.module).distinct().all()
    return [m[0] for m in modules]


def _build_role_dict(role: Role) -> dict:
    """将角色对象转换为字典"""
    permissions = []
    for rp in role.role_permissions:
        if rp.permission:
            permissions.append({
                "id": rp.permission.id,
                "module": rp.permission.module,
                "resource": rp.permission.resource,
                "action": rp.permission.action,
                "name": rp.permission.name,
                "description": rp.permission.description,
                "is_active": rp.permission.is_active,
                "created_at": rp.permission.created_at,
            })

    return {
        "id": role.id,
        "code": role.code,
        "name": role.name,
        "description": role.description,
        "is_system": role.is_system,
        "is_active": role.is_active,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
        "permissions": permissions,
    }


def get_roles(db: Session, include_system: bool = True) -> List[dict]:
    """获取角色列表"""
    query = db.query(Role).options(
        joinedload(Role.role_permissions).joinedload(RolePermission.permission)
    ).filter(Role.is_active == True)

    if not include_system:
        query = query.filter(Role.is_system == False)

    roles = query.order_by(Role.is_system.desc(), Role.name).all()
    return [_build_role_dict(role) for role in roles]


def get_role(db: Session, role_id: int) -> Optional[dict]:
    """获取角色详情"""
    role = db.query(Role).options(
        joinedload(Role.role_permissions).joinedload(RolePermission.permission)
    ).filter(Role.id == role_id).first()

    if not role:
        return None

    return _build_role_dict(role)


def create_role(db: Session, code: str, name: str, description: Optional[str], permission_ids: List[int]) -> dict:
    """创建新角色"""
    existing_role = db.query(Role).filter(Role.code == code).first()
    if existing_role:
        return None, "角色编码已存在"

    role = Role(
        code=code,
        name=name,
        description=description,
        is_system=False
    )
    db.add(role)
    db.flush()

    if permission_ids:
        for perm_id in permission_ids:
            permission = db.query(Permission).filter(Permission.id == perm_id).first()
            if not permission:
                return None, f"权限ID {perm_id} 不存在"

            role_perm = RolePermission(role_id=role.id, permission_id=perm_id)
            db.add(role_perm)

    db.commit()
    db.refresh(role)
    return _build_role_dict(role), None


def update_role(db: Session, role_id: int, name: Optional[str], description: Optional[str],
               is_active: Optional[bool], permission_ids: Optional[List[int]]) -> tuple:
    """更新角色信息"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        return None, "角色不存在"

    if role.is_system and permission_ids is not None:
        return None, "系统预置角色的权限不能修改"

    if name is not None:
        role.name = name
    if description is not None:
        role.description = description
    if is_active is not None:
        role.is_active = is_active

    if not role.is_system and permission_ids is not None:
        db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()

        for perm_id in permission_ids:
            permission = db.query(Permission).filter(Permission.id == perm_id).first()
            if not permission:
                return None, f"权限ID {perm_id} 不存在"

            role_perm = RolePermission(role_id=role_id, permission_id=perm_id)
            db.add(role_perm)

    db.commit()
    db.refresh(role)
    return _build_role_dict(role), None


def delete_role(db: Session, role_id: int) -> tuple:
    """删除角色"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        return False, "角色不存在"

    if role.is_system:
        return False, "系统预置角色不能删除"

    user_count = db.query(UserRole).filter(UserRole.role_id == role_id).count()
    if user_count > 0:
        return False, f"该角色正在被 {user_count} 个用户使用，不能删除"

    db.delete(role)
    db.commit()
    return True, None


def get_user_roles(db: Session, user_id: int) -> tuple:
    """获取用户的角色列表"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None, "用户不存在"

    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()

    result = []
    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        if role:
            result.append({
                "id": ur.id,
                "user_id": ur.user_id,
                "role_id": ur.role_id,
                "role_code": role.code,
                "role_name": role.name,
                "created_at": ur.created_at,
            })

    return result, None


def assign_user_role(db: Session, user_id: int, role_id: int) -> tuple:
    """为用户分配角色"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False, "用户不存在"

    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        return False, "角色不存在"

    existing = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()

    if existing:
        return False, "用户已拥有该角色"

    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    db.commit()

    return True, None


def remove_user_role(db: Session, user_id: int, role_id: int) -> tuple:
    """移除用户的角色"""
    user_role = db.query(UserRole).filter(
        UserRole.user_id == user_id,
        UserRole.role_id == role_id
    ).first()

    if not user_role:
        return False, "用户角色关系不存在"

    role = db.query(Role).filter(Role.id == role_id).first()
    if role and role.is_system and role.code == "super_admin":
        super_admin_count = db.query(UserRole).join(Role).filter(
            Role.code == "super_admin"
        ).count()

        if super_admin_count <= 1:
            return False, "不能移除最后一个超级管理员的角色"

    db.delete(user_role)
    db.commit()
    return True, None


def get_my_permissions(db: Session, current_user: User) -> dict:
    """获取当前用户的权限信息"""
    from permission_middleware import get_user_permissions

    permissions = get_user_permissions(current_user, db)

    user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
    roles = []
    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        if role:
            roles.append({
                "id": role.id,
                "code": role.code,
                "name": role.name,
            })

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
        "is_super_admin": current_user.is_super_admin,
        "roles": roles,
        "permissions": list(permissions),
    }


# ============ 系统菜单树定义 ============
# 菜单结构：分组 → 菜单项 → 子菜单（可选）
# 权限控制：
# - permission: 单个权限标识，None 表示始终可见
# - _any_permissions: 满足任一权限即显示
# - 子菜单：只有当至少一个子菜单可见时，父菜单才显示
#
# ⚠️ 添加业务菜单时在下方列表中添加即可，后端会自动按权限过滤

ALL_MENUS = [
    {
        "key": "home",
        "label": "首页",
        "items": [
            {
                "key": "home",
                "label": "欢迎首页",
                "path": "/home",
                "icon": "home",
                "permission": None,
            },
        ],
    },
    {
        "key": "management",
        "label": "管理",
        "items": [
            {
                "key": "settings",
                "label": "设置",
                "path": "/settings/profile",
                "icon": "gear",
                "permission": None,
                "children": [
                    {
                        "key": "profile",
                        "label": "个人资料",
                        "path": "/settings/profile",
                        "permission": None,
                    },
                    {
                        "key": "password",
                        "label": "修改密码",
                        "path": "/settings/password",
                        "permission": None,
                    },
                    {
                        "key": "users",
                        "label": "用户管理",
                        "path": "/settings/users",
                        "permission": "system:user:list",
                    },
                    {
                        "key": "configs",
                        "label": "参数设置",
                        "path": "/settings/configs",
                        "permission": "setting:config:list",
                    },
                    {
                        "key": "permissions",
                        "label": "权限管理",
                        "path": "/settings/permissions",
                        "permission": "system:role:list",
                    },
                ],
            },
        ],
    },
]


def _check_menu_permission(item: dict, has_perm_func) -> bool:
    """检查用户是否有菜单项的权限"""
    any_perms = item.get("_any_permissions")
    if any_perms:
        return any(has_perm_func(p) for p in any_perms)

    permission = item.get("permission")
    if permission is None:
        return True

    return has_perm_func(permission)


def _filter_menu_item(item: dict, has_perm_func) -> Optional[dict]:
    """过滤单个菜单项"""
    children = item.get("children")
    if children:
        visible_children = []
        for child in children:
            filtered = _filter_menu_item(child, has_perm_func)
            if filtered is not None:
                visible_children.append(filtered)

        if not visible_children:
            return None

        result = {k: v for k, v in item.items() if not k.startswith("_")}
        result["children"] = visible_children
        return result

    if not _check_menu_permission(item, has_perm_func):
        return None

    return {k: v for k, v in item.items() if not k.startswith("_")}


def get_user_menus(db: Session, current_user: User) -> List[dict]:
    """
    获取当前用户的菜单树

    根据用户角色→权限，过滤 ALL_MENUS 中用户可见的菜单项，
    支持 _any_permissions（满足任一权限即显示）和子菜单递归过滤。

    返回格式：[{key, label, items: [{key, label, path, icon, children}]}]
    """
    from permission_middleware import has_permission

    def has_perm(perm_str: str) -> bool:
        return has_permission(current_user, perm_str, db)

    result = []
    for group in ALL_MENUS:
        visible_items = []
        for item in group["items"]:
            filtered = _filter_menu_item(item, has_perm)
            if filtered is not None:
                visible_items.append(filtered)
        if visible_items:
            result.append({
                "key": group["key"],
                "label": group["label"],
                "items": visible_items,
            })

    return result
