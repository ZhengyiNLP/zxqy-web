from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import CreateUserRequest, UpdateUserRequest, ResetPasswordRequest
from auth import get_current_user
from permission_middleware import check_permission
from utils.response import ok, fail
from services.users_service import (
    create_user,
    list_users,
    update_user,
    delete_user,
    get_current_user_info,
    update_my_profile,
    change_my_password,
    reset_user_password,
)

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.post("", dependencies=[Depends(check_permission("system:user:add"))])
def create_user_endpoint(
    req: CreateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data, err = create_user(db, req)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return ok(data)


@router.get("", dependencies=[Depends(check_permission("system:user:list"))])
def list_users_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = list_users(db)
    return ok(data)


@router.put("/{user_id}", dependencies=[Depends(check_permission("system:user:edit"))])
def update_user_endpoint(
    user_id: int,
    req: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data, err = update_user(db, user_id, req)
    if err == "用户不存在":
        raise HTTPException(status_code=404, detail=err)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return ok(data)


@router.delete("/{user_id}", dependencies=[Depends(check_permission("system:user:delete"))])
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    err = delete_user(db, current_user, user_id)
    if err == "用户不存在":
        raise HTTPException(status_code=404, detail=err)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return ok(message="删除成功")


@router.get("/me", dependencies=[Depends(check_permission("auth:profile:view"))])
def get_current_user_info_endpoint(
    current_user: User = Depends(get_current_user),
):
    data = get_current_user_info(current_user)
    return ok(data)


@router.put("/me", dependencies=[Depends(check_permission("auth:profile:edit"))])
def update_my_profile_endpoint(
    req: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data, err = update_my_profile(db, current_user, req)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return ok(data)


@router.put("/me/password", dependencies=[Depends(check_permission("auth:password:change"))])
def change_my_password_endpoint(
    req: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    err = change_my_password(db, current_user, req)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return ok(message="密码修改成功")


@router.post("/{user_id}/reset-password", dependencies=[Depends(check_permission("system:user:reset-password"))])
def reset_user_password_endpoint(
    user_id: int,
    req: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data, err = reset_user_password(db, current_user, user_id, req)
    if err == "用户不存在":
        raise HTTPException(status_code=404, detail=err)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return ok(data, "密码重置成功，用户下次登录时需要修改密码")
