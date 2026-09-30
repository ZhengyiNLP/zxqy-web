from sqlalchemy.orm import Session
from utils.response import ok, fail
from models import User, Role, UserRole
from schemas import CreateUserRequest, UpdateUserRequest, ResetPasswordRequest
from auth import hash_password, verify_password


def create_user(db: Session, req: CreateUserRequest):
    """创建新用户"""
    if db.query(User).filter(User.username == req.username).first():
        return None, "用户名已存在"

    # 校验角色
    roles = []
    if req.role_ids:
        roles = db.query(Role).filter(Role.id.in_(req.role_ids)).all()
        if len(roles) != len(req.role_ids):
            return None, "部分角色不存在"
        for role in roles:
            if role.code == "super_admin":
                return None, "超级管理员角色只能在系统初始化时分配，无法手动设置"

    is_admin = any(r.code == "super_admin" for r in roles)

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        display_name=req.display_name,
        is_admin=is_admin,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 分配角色
    for role in roles:
        db.add(UserRole(user_id=user.id, role_id=role.id))
    db.commit()

    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "is_admin": user.is_admin,
        "must_change_password": user.must_change_password,
        "roles": [{"id": r.id, "code": r.code, "name": r.name} for r in roles],
    }, None


def list_users(db: Session):
    """获取所有用户列表"""
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        user_roles = db.query(UserRole).filter(UserRole.user_id == u.id).all()
        role_ids = [ur.role_id for ur in user_roles]
        roles = []
        if role_ids:
            roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        result.append({
            "id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "is_admin": u.is_admin,
            "must_change_password": u.must_change_password,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "roles": [{"id": r.id, "code": r.code, "name": r.name} for r in roles],
        })
    return result


def update_user(db: Session, user_id: int, req: UpdateUserRequest):
    """更新用户信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None, "用户不存在"

    if req.display_name is not None:
        user.display_name = req.display_name

    if req.role_ids is not None:
        roles = []
        if req.role_ids:
            roles = db.query(Role).filter(Role.id.in_(req.role_ids)).all()
            if len(roles) != len(req.role_ids):
                return None, "部分角色不存在"
            for role in roles:
                if role.code == "super_admin":
                    return None, "超级管理员角色只能在系统初始化时分配，无法手动设置"

        db.query(UserRole).filter(UserRole.user_id == user.id).delete()
        for role in roles:
            db.add(UserRole(user_id=user.id, role_id=role.id))
        user.is_admin = any(r.code == "super_admin" for r in roles)

    db.commit()
    db.refresh(user)

    # 查询最终角色
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = []
    if role_ids:
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()

    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "is_admin": user.is_admin,
        "roles": [{"id": r.id, "code": r.code, "name": r.name} for r in roles],
    }, None


def delete_user(db: Session, current_user: User, user_id: int):
    """删除用户"""
    if user_id == current_user.id:
        return "不能删除自己"
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return "用户不存在"
    db.delete(user)
    db.commit()
    return None


def get_current_user_info(current_user: User):
    """获取当前登录用户信息"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "display_name": current_user.display_name,
        "is_admin": current_user.is_admin,
        "must_change_password": current_user.must_change_password,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
    }


def update_my_profile(db: Session, current_user: User, req: dict):
    """更新当前用户资料"""
    if "display_name" in req:
        if not req["display_name"] or not req["display_name"].strip():
            return None, "显示名称不能为空"
        current_user.display_name = req["display_name"].strip()
    db.commit()
    db.refresh(current_user)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "display_name": current_user.display_name,
    }, None


def change_my_password(db: Session, current_user: User, req: dict):
    """修改当前用户密码"""
    old_password = req.get("old_password")
    new_password = req.get("new_password")

    if not old_password or not new_password:
        return "请提供旧密码和新密码"

    if len(new_password) < 6:
        return "新密码长度不能少于6位"

    if not verify_password(old_password, current_user.password_hash):
        return "当前密码错误"

    current_user.password_hash = hash_password(new_password)
    current_user.must_change_password = False
    db.commit()
    return None


def reset_user_password(db: Session, current_user: User, user_id: int, req: ResetPasswordRequest):
    """管理员重置用户密码"""
    if user_id == current_user.id:
        return None, "不能重置自己的密码，请使用修改密码功能"

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None, "用户不存在"

    user.password_hash = hash_password(req.new_password)
    user.must_change_password = True
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "must_change_password": user.must_change_password,
    }, None
