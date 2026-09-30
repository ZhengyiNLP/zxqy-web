"""
数据模型定义

框架骨架只包含基础模型：
- User：用户
- Permission：权限
- Role：角色
- RolePermission：角色-权限关联
- UserRole：用户-角色关联
- SysConfig：系统参数配置

业务模型请在各自的模块中定义，
并在 models.py 底部 import 以确保 Base.metadata.create_all 能发现它们。
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_super_admin = Column(Boolean, default=False)
    must_change_password = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    user_roles = relationship("UserRole", back_populates="user")


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module = Column(String(50), nullable=False)
    resource = Column(String(50))
    action = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint('module', 'resource', 'action', name='uq_permission_full'),)


class Role(Base):
    """角色表"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_system = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")


class RolePermission(Base):
    """角色权限关联表"""
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission")

    __table_args__ = (UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),)


class UserRole(Base):
    """用户角色关联表"""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='uq_user_role'),)


class SysConfig(Base):
    """系统参数配置（key-value，运行时可在设置页修改，无需改代码）"""
    __tablename__ = "sys_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_name = Column(String(100), nullable=False)
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, default="")
    config_type = Column(String(1), default="N")  # Y=系统内置（不可删除）N=自定义
    remark = Column(String(500), default="")
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


# ====== 业务模型 ======

class Category(Base):
    """栏目分类"""
    __tablename__ = "t_category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # article / product
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1)  # 0=禁用 1=启用
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted = Column(Integer, default=0)


class Article(Base):
    """新闻文章"""
    __tablename__ = "t_article"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("t_category.id"), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(String(500))
    content = Column(Text, nullable=False)
    cover_image = Column(String(255))
    source = Column(String(100))
    view_count = Column(Integer, default=0)
    status = Column(String(20), default="draft")  # draft / published
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted = Column(Integer, default=0)

    category = relationship("Category")


class Product(Base):
    """产品"""
    __tablename__ = "t_product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("t_category.id"), nullable=False)
    name = Column(String(200), nullable=False)
    short_desc = Column(String(500))
    description = Column(Text, nullable=False)
    cover_image = Column(String(255))
    params = Column(Text)  # JSON format
    is_recommend = Column(Integer, default=0)
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1)  # 0=下架 1=上架
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted = Column(Integer, default=0)

    category = relationship("Category")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


class ProductImage(Base):
    """产品图片"""
    __tablename__ = "t_product_image"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("t_product.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    product = relationship("Product", back_populates="images")


class Page(Base):
    """单页内容"""
    __tablename__ = "t_page"

    id = Column(Integer, primary_key=True, autoincrement=True)
    page_key = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    extra_data = Column(Text)  # JSON format
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))


class Message(Base):
    """留言"""
    __tablename__ = "t_message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100))
    content = Column(Text, nullable=False)
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    deleted = Column(Integer, default=0)


class Banner(Base):
    """轮播图"""
    __tablename__ = "t_banner"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200))
    image_url = Column(String(255), nullable=False)
    link_url = Column(String(255))
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted = Column(Integer, default=0)


class FriendLink(Base):
    """友情链接"""
    __tablename__ = "t_friend_link"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    url = Column(String(255), nullable=False)
    sort_order = Column(Integer, default=0)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    deleted = Column(Integer, default=0)
