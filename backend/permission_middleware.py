"""
权限检查中间件
提供基于权限标识的权限检查功能
权限格式：模块:业务:操作（如 daily:report:create）
支持通配符：*:*:*（全部）、模块:*:*（模块所有）、模块:业务:*（业务所有）

核心规则：
- is_super_admin=True 的用户绕过所有权限检查（系统约束，仅1人，初始化时分配）
- 其他所有用户通过 RBAC 查询角色→权限→匹配
- is_admin 不再作为权限绕过条件，管理员角色通过权限配置获得访问能力
"""
from functools import wraps
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserRole, RolePermission, Permission
from auth import get_current_user
from typing import List, Set


def get_user_permissions(user: User, db: Session) -> Set[str]:
    """获取用户的所有权限标识集合"""
    if user.is_super_admin:
        return {"*:*:*"}

    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    role_ids = [ur.role_id for ur in user_roles]

    if not role_ids:
        return set()

    role_permissions = db.query(RolePermission).filter(
        RolePermission.role_id.in_(role_ids)
    ).all()

    permission_ids = [rp.permission_id for rp in role_permissions]

    if not permission_ids:
        return set()

    permissions = db.query(Permission).filter(
        Permission.id.in_(permission_ids),
        Permission.is_active == True
    ).all()

    permission_set = set()
    for perm in permissions:
        if perm.module and perm.action:
            if perm.resource:
                permission_set.add(f"{perm.module}:{perm.resource}:{perm.action}")
            else:
                permission_set.add(f"{perm.module}:{perm.action}")

    return permission_set


def match_permission(required_perm: str, user_perms: Set[str]) -> bool:
    """
    检查权限是否匹配，支持通配符
    
    匹配规则：
    - "*:*:*" → 匹配所有权限
    - "module:*:*" → 匹配该模块下所有权限
    - "module:resource:*" → 匹配该业务下所有操作
    - 逐段匹配：每一段相等或用户权限段为 "*" 则匹配
    
    示例：
    - 用户有 "daily:*:*" → 匹配 "daily:report:create"、"daily:report:list"
    - 用户有 "*:report:list" → 匹配 "daily:report:list"、"weekly:report:list"
    """
    for user_perm in user_perms:
        if user_perm == "*:*:*":
            return True

        required_parts = required_perm.split(":")
        user_parts = user_perm.split(":")

        match = True
        for i in range(max(len(required_parts), len(user_parts))):
            required = required_parts[i] if i < len(required_parts) else None
            user = user_parts[i] if i < len(user_parts) else None

            if user == "*":
                continue
            if required != user:
                match = False
                break

        if match:
            return True

    return False


def has_permission(user: User, permission_str: str, db: Session) -> bool:
    """检查用户是否有指定权限"""
    if user.is_super_admin:
        return True

    user_permissions = get_user_permissions(user, db)

    if "*:*:*" in user_permissions:
        return True

    return match_permission(permission_str, user_permissions)


def require_permission(permission_str: str):
    """权限检查装饰器，用于FastAPI路由"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')

            if not current_user or not db:
                raise HTTPException(status_code=500, detail="权限检查参数错误")

            if not has_permission(current_user, permission_str, db):
                raise HTTPException(
                    status_code=403,
                    detail="权限不足，请联系管理员"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_permission(permission_str: str):
    """权限检查依赖项，用于FastAPI Depends"""
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not has_permission(current_user, permission_str, db):
            raise HTTPException(
                status_code=403,
                detail="权限不足，请联系管理员"
            )
        return current_user
    return permission_checker


def check_any_permission(*permission_strs: str):
    """检查用户是否有任意一个指定权限"""
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if current_user.is_super_admin:
            return current_user

        for perm_str in permission_strs:
            if has_permission(current_user, perm_str, db):
                return current_user

        raise HTTPException(
            status_code=403,
            detail="权限不足，请联系管理员"
        )
    return permission_checker


def check_all_permissions(*permission_strs: str):
    """检查用户是否有所有指定权限"""
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if current_user.is_super_admin:
            return current_user

        for perm_str in permission_strs:
            if not has_permission(current_user, perm_str, db):
                raise HTTPException(
                    status_code=403,
                    detail=f"权限不足，需要权限: {perm_str}"
                )

        return current_user
    return permission_checker
