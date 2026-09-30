import logging

from sqlalchemy.orm import Session
from utils.response import ok, fail

from models import User, Role, UserRole, RolePermission, Permission
from auth import verify_password, hash_password, create_access_token

logger = logging.getLogger("auth_service")


def login(db: Session, username: str, password: str) -> dict:
    """用户登录"""
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return None

    token = create_access_token(user.id)

    # 获取用户的角色和权限
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = []
    permissions = []

    if role_ids:
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

        role_permissions = db.query(RolePermission).filter(RolePermission.role_id.in_(role_ids)).all()
        permission_ids = list(set([rp.permission_id for rp in role_permissions]))
        if permission_ids:
            perms = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
            for p in perms:
                if p.resource:
                    permissions.append(f"{p.module}:{p.resource}:{p.action}")
                else:
                    permissions.append(f"{p.module}:{p.action}")

    is_super_admin = user.is_super_admin

    return {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "is_admin": user.is_admin,
            "is_super_admin": is_super_admin,
            "must_change_password": user.must_change_password,
            "roles": [r.name for r in roles] if roles else [],
            "role_codes": [r.code for r in roles] if roles else [],
            "permissions": permissions,
        },
    }


def register(db: Session, username: str, password: str, display_name: str) -> dict | None:
    """用户自注册"""
    if db.query(User).filter(User.username == username).first():
        return None, "用户名已存在"
    if db.query(User).filter(User.display_name == display_name).first():
        return None, "显示名已被使用"

    user = User(
        username=username,
        password_hash=hash_password(password),
        display_name=display_name,
        is_admin=False,
        must_change_password=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"User registered: {user.username}")

    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
    }, None


def change_password(db: Session, current_user: User, old_password: str, new_password: str) -> bool:
    """修改密码"""
    if not verify_password(old_password, current_user.password_hash):
        return False
    current_user.password_hash = hash_password(new_password)
    current_user.must_change_password = False
    db.commit()
    logger.info(f"Password changed: user={current_user.username}")
    return True


def reset_password(db: Session, user_id: int, new_password: str) -> dict | None:
    """重置用户密码"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    user.password_hash = hash_password(new_password)
    user.must_change_password = True
    db.commit()

    logger.info(f"Password reset for user {user.username}")
    return {"display_name": user.display_name}


def get_me(current_user: User) -> dict:
    """获取当前用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "is_admin": current_user.is_admin,
        "must_change_password": current_user.must_change_password,
    }


def check_username(db: Session, username: str) -> dict:
    """检查用户名是否可用"""
    exists = db.query(User).filter(User.username == username).first() is not None
    return {"available": not exists}


def check_display_name(db: Session, display_name: str) -> dict:
    """检查显示名是否可用"""
    exists = db.query(User).filter(User.display_name == display_name).first() is not None
    return {"available": not exists}
