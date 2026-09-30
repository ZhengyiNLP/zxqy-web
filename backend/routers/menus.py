"""
菜单路由
提供当前用户的菜单树接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import get_current_user
from permission_middleware import check_permission
from utils.response import ok, fail
from services.permissions_service import get_user_menus

router = APIRouter(prefix="/api/menus", tags=["菜单"])


@router.get("", dependencies=[Depends(check_permission("system:menu:view"))])
def get_menus(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的菜单树（基于权限过滤）"""
    menus = get_user_menus(db, current_user=current_user)
    return ok(menus)
