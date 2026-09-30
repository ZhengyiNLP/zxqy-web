from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import CreateSysConfigRequest, UpdateSysConfigRequest
from auth import get_current_user
from permission_middleware import check_permission
from utils.response import ok
from services.sys_config_service import (
    list_configs,
    create_config,
    update_config,
    delete_config,
)

router = APIRouter(prefix="/api/settings/sys-configs", tags=["系统参数"])


@router.get("", dependencies=[Depends(check_permission("setting:config:list"))])
def list_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取系统参数列表"""
    return ok(list_configs(db))


@router.post("", dependencies=[Depends(check_permission("setting:config:add"))])
def create(req: CreateSysConfigRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """新增系统参数"""
    return ok(create_config(db, req.config_name, req.config_key, req.config_value, req.remark), "新增成功")


@router.put("/{config_id}", dependencies=[Depends(check_permission("setting:config:edit"))])
def update(config_id: int, req: UpdateSysConfigRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """更新系统参数"""
    return ok(update_config(db, config_id, req.config_name, req.config_value, req.remark), "保存成功")


@router.delete("/{config_id}", dependencies=[Depends(check_permission("setting:config:delete"))])
def delete(config_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除系统参数（系统内置参数不可删除）"""
    delete_config(db, config_id)
    return ok(message="删除成功")
