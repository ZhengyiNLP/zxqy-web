"""
权限管理路由
提供角色、权限的CRUD操作
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import User
from auth import get_current_user
from permission_middleware import require_permission, check_permission
from pydantic import BaseModel
from datetime import datetime
from utils.response import ok, fail
from services.permissions_service import (
    get_permissions as svc_get_permissions,
    get_modules as svc_get_modules,
    get_roles as svc_get_roles,
    get_role as svc_get_role,
    create_role as svc_create_role,
    update_role as svc_update_role,
    delete_role as svc_delete_role,
    get_user_roles as svc_get_user_roles,
    assign_user_role as svc_assign_user_role,
    remove_user_role as svc_remove_user_role,
    get_my_permissions as svc_get_my_permissions,
)

router = APIRouter(prefix="/api/permissions", tags=["权限管理"])


# ============ Pydantic 模型 ============

class PermissionResponse(BaseModel):
    id: int
    module: str
    resource: Optional[str]
    action: str
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: List[int] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None


class RoleResponse(RoleBase):
    id: int
    is_system: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class UserRoleAssign(BaseModel):
    user_id: int
    role_id: int


class UserRoleResponse(BaseModel):
    id: int
    user_id: int
    role_id: int
    role_code: str
    role_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 权限相关 API ============

@router.get("/permissions")
def get_permissions(
    module: Optional[str] = Query(None, description="按模块筛选"),
    current_user: User = Depends(check_permission("system:role:list")),
    db: Session = Depends(get_db)
):
    """获取所有权限列表"""
    result = svc_get_permissions(db, module=module)
    return ok(result)


@router.get("/modules")
def get_modules(
    current_user: User = Depends(check_permission("system:role:list")),
    db: Session = Depends(get_db)
):
    """获取所有权限模块列表"""
    result = svc_get_modules(db)
    return ok(result)


# ============ 角色相关 API ============

@router.get("/roles")
def get_roles(
    include_system: bool = Query(True, description="是否包含系统预置角色"),
    current_user: User = Depends(check_permission("system:role:list")),
    db: Session = Depends(get_db)
):
    """获取角色列表"""
    result = svc_get_roles(db, include_system=include_system)
    return ok(result)


@router.get("/roles/{role_id}")
def get_role(
    role_id: int,
    current_user: User = Depends(check_permission("system:role:list")),
    db: Session = Depends(get_db)
):
    """获取角色详情"""
    result = svc_get_role(db, role_id=role_id)
    if result is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return ok(result)


@router.post("/roles")
def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(check_permission("system:role:add")),
    db: Session = Depends(get_db)
):
    """创建新角色"""
    result, error = svc_create_role(
        db, code=role_data.code, name=role_data.name,
        description=role_data.description, permission_ids=role_data.permission_ids
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    return ok(result, "success")


@router.put("/roles/{role_id}")
def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(check_permission("system:role:edit")),
    db: Session = Depends(get_db)
):
    """更新角色信息"""
    result, error = svc_update_role(
        db, role_id=role_id, name=role_data.name,
        description=role_data.description, is_active=role_data.is_active,
        permission_ids=role_data.permission_ids
    )
    if error:
        status_code = 404 if error == "角色不存在" else 400
        raise HTTPException(status_code=status_code, detail=error)
    return ok(result, "success")


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    current_user: User = Depends(check_permission("system:role:delete")),
    db: Session = Depends(get_db)
):
    """删除角色"""
    success, error = svc_delete_role(db, role_id=role_id)
    if not success:
        status_code = 404 if error == "角色不存在" else 400
        raise HTTPException(status_code=status_code, detail=error)
    return ok(message="删除成功")


# ============ 用户角色分配 API ============

@router.get("/users/{user_id}/roles")
def get_user_roles(
    user_id: int,
    current_user: User = Depends(check_permission("system:role:list")),
    db: Session = Depends(get_db)
):
    """获取用户的角色列表"""
    result, error = svc_get_user_roles(db, user_id=user_id)
    if error:
        raise HTTPException(status_code=404, detail=error)
    return ok(result, "success")


@router.post("/users/roles")
def assign_user_role(
    assignment: UserRoleAssign,
    current_user: User = Depends(check_permission("system:role:assign")),
    db: Session = Depends(get_db)
):
    """为用户分配角色"""
    success, error = svc_assign_user_role(db, user_id=assignment.user_id, role_id=assignment.role_id)
    if not success:
        status_code = 404 if "不存在" in error else 400
        raise HTTPException(status_code=status_code, detail=error)
    return ok(message="角色分配成功")


@router.delete("/users/{user_id}/roles/{role_id}")
def remove_user_role(
    user_id: int,
    role_id: int,
    current_user: User = Depends(check_permission("system:role:assign")),
    db: Session = Depends(get_db)
):
    """移除用户的角色"""
    success, error = svc_remove_user_role(db, user_id=user_id, role_id=role_id)
    if not success:
        status_code = 404 if "不存在" in error else 400
        raise HTTPException(status_code=status_code, detail=error)
    return ok(message="删除成功")


# ============ 当前用户权限信息 API ============

@router.get("/me/permissions", dependencies=[Depends(check_permission("auth:profile:view"))])
def get_my_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的权限信息"""
    result = svc_get_my_permissions(db, current_user=current_user)
    return ok(result, "success")
