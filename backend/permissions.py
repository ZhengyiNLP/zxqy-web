"""
通用权限检查辅助函数
供各路由文件复用
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional


def mask_username(username: str) -> str:
    """用户名脱敏，用于日志"""
    if len(username) <= 1:
        return "***"
    return username[0] + "***"
