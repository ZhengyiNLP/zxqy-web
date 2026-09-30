"""
模块名称：系统参数配置服务

功能描述：
- sys_config 表的读取（进程内缓存）与增删改
- 业务代码读取运行参数的统一入口，避免硬编码常量散落各处

使用约定：
- 读取：get_config(db, "ai.request.timeout", "60") / get_int(db, ...)
- 写入只走本模块 CRUD（或设置页接口），缓存自动失效
- 新参数需同时在 database.py 的 DEFAULT_SYS_CONFIGS 登记种子数据
"""
from typing import Optional

from sqlalchemy.orm import Session

from models import SysConfig
from utils.exceptions import BusinessException

# 进程内缓存：key -> value。单进程部署足够，任何写入后整体失效重建
_cache: dict[str, Optional[str]] = {}


def get_config(db: Session, key: str, default: Optional[str] = None) -> Optional[str]:
    if key in _cache:
        return _cache[key]
    row = db.query(SysConfig).filter(SysConfig.config_key == key).first()
    value = row.config_value if row else default
    _cache[key] = value
    return value


def get_int(db: Session, key: str, default: int) -> int:
    raw = get_config(db, key, None)
    try:
        return int(raw) if raw is not None and raw != "" else default
    except ValueError:
        return default


def _serialize(row: SysConfig) -> dict:
    return {
        "id": row.id,
        "config_name": row.config_name,
        "config_key": row.config_key,
        "config_value": row.config_value,
        "config_type": row.config_type,
        "remark": row.remark,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


def list_configs(db: Session) -> list[dict]:
    rows = db.query(SysConfig).order_by(SysConfig.id).all()
    return [_serialize(r) for r in rows]


def create_config(db: Session, config_name: str, config_key: str, config_value: str, remark: str = "") -> dict:
    exists = db.query(SysConfig).filter(SysConfig.config_key == config_key).first()
    if exists:
        raise BusinessException("配置键已存在")
    row = SysConfig(
        config_name=config_name,
        config_key=config_key,
        config_value=config_value,
        config_type="N",
        remark=remark,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    _cache.clear()
    return _serialize(row)


def update_config(db: Session, config_id: int, config_name: str, config_value: str, remark: str = "") -> dict:
    row = db.query(SysConfig).filter(SysConfig.id == config_id).first()
    if not row:
        raise BusinessException("配置不存在")
    row.config_name = config_name
    row.config_value = config_value
    row.remark = remark
    db.commit()
    db.refresh(row)
    _cache.clear()
    return _serialize(row)


def delete_config(db: Session, config_id: int) -> None:
    row = db.query(SysConfig).filter(SysConfig.id == config_id).first()
    if not row:
        raise BusinessException("配置不存在")
    if row.config_type == "Y":
        raise BusinessException("系统内置参数不可删除")
    db.delete(row)
    db.commit()
    _cache.clear()
