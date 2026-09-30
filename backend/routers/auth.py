from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import LoginRequest, RegisterRequest, ChangePasswordRequest
from auth import get_current_user
from permission_middleware import check_permission
from utils.response import ok, fail
from services.auth_service import (
    login as svc_login,
    register as svc_register,
    change_password as svc_change_password,
    get_me as svc_get_me,
    check_username as svc_check_username,
    check_display_name as svc_check_display_name,
)

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    data = svc_login(db, req.username, req.password)
    if data is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return ok(data)


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    data, error = svc_register(db, req.username, req.password, req.display_name)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return ok(data, "注册成功")


@router.post("/change-password", dependencies=[Depends(check_permission("auth:password:change"))])
def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """修改密码"""
    if not svc_change_password(db, current_user, req.old_password, req.new_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    return ok(message="密码修改成功")


@router.get("/me", dependencies=[Depends(check_permission("auth:profile:view"))])
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    data = svc_get_me(current_user)
    return ok(data)


@router.get("/check-username")
def check_username(
    username: str,
    db: Session = Depends(get_db),
):
    """检查用户名是否可用"""
    data = svc_check_username(db, username)
    return ok(data)


@router.get("/check-display-name")
def check_display_name(
    display_name: str,
    db: Session = Depends(get_db),
):
    """检查显示名称是否可用"""
    data = svc_check_display_name(db, display_name)
    return ok(data)
