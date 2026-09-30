from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# --- Auth ---
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100, description="密码至少6位")


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=100, description="密码至少6位")


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=6, max_length=100, description="密码至少6位")
    new_password: str = Field(..., min_length=6, max_length=100, description="密码至少6位")


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=100, description="密码至少6位")


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    is_admin: bool
    must_change_password: bool
    created_at: datetime

    class Config:
        from_attributes = True


# --- User Management ---
class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100, description="密码至少6位")
    display_name: str = Field(..., min_length=2, max_length=100)
    role_ids: Optional[List[int]] = None


class UpdateUserRequest(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role_ids: Optional[List[int]] = None


# --- Sys Config ---
class CreateSysConfigRequest(BaseModel):
    config_name: str = Field(..., max_length=100)
    config_key: str = Field(..., max_length=100, pattern=r"^[a-z][a-z0-9_.]*$", description="小写字母/数字/下划线/点")
    config_value: str = Field("", max_length=10000)
    remark: str = Field("", max_length=500)


class UpdateSysConfigRequest(BaseModel):
    config_name: str = Field(..., max_length=100)
    config_value: str = Field("", max_length=10000)
    remark: str = Field("", max_length=500)


# --- Unified Response ---
class APIResponse(BaseModel):
    code: int = 0
    data: object = None
    message: str = "success"


# ====== 业务 Schema ======

# --- Category ---
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    type: str = Field(..., max_length=20)  # article / product
    sort_order: int = 0
    status: int = 1

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None

class CategoryOut(BaseModel):
    id: int
    name: str
    type: str
    sort_order: int
    status: int
    class Config:
        from_attributes = True

# --- Article ---
class ArticleCreate(BaseModel):
    category_id: int
    title: str = Field(..., max_length=200)
    summary: Optional[str] = None
    content: str
    cover_image: Optional[str] = None
    source: Optional[str] = None
    status: str = "draft"

class ArticleUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None

class ArticleStatusUpdate(BaseModel):
    status: str  # draft / published

class ArticleListOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: int
    category_name: Optional[str] = None
    status: str
    published_at: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

class ArticleDetailOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    content: str
    cover_image: Optional[str] = None
    source: Optional[str] = None
    view_count: int
    category_name: Optional[str] = None
    published_at: Optional[datetime] = None
    prev_article: Optional[dict] = None
    next_article: Optional[dict] = None
    class Config:
        from_attributes = True

# --- Product ---
class ProductImageOut(BaseModel):
    id: int
    image_url: str
    sort_order: int
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(..., max_length=200)
    short_desc: Optional[str] = None
    description: str
    cover_image: Optional[str] = None
    params: Optional[str] = None  # JSON string
    is_recommend: int = 0
    sort_order: int = 0
    status: int = 1
    images: Optional[List[str]] = None  # image url list

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    short_desc: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    params: Optional[str] = None
    is_recommend: Optional[int] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None
    images: Optional[List[str]] = None

class ProductListOut(BaseModel):
    id: int
    name: str
    short_desc: Optional[str] = None
    cover_image: Optional[str] = None
    category_id: int
    is_recommend: int
    status: int
    sort_order: int
    class Config:
        from_attributes = True

class ProductDetailOut(BaseModel):
    id: int
    name: str
    short_desc: Optional[str] = None
    description: str
    cover_image: Optional[str] = None
    params: Optional[str] = None
    is_recommend: int
    category_name: Optional[str] = None
    images: List[ProductImageOut] = []
    class Config:
        from_attributes = True

# --- Page ---
class PageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    extra_data: Optional[str] = None

class PageOut(BaseModel):
    id: int
    page_key: str
    title: str
    content: Optional[str] = None
    extra_data: Optional[str] = None
    class Config:
        from_attributes = True

# --- Message ---
class MessageCreate(BaseModel):
    name: str = Field(..., max_length=50)
    phone: str = Field(..., max_length=20)
    email: Optional[str] = None
    content: str

class MessageOut(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str] = None
    content: str
    is_read: int
    created_at: datetime
    class Config:
        from_attributes = True

# --- Banner ---
class BannerCreate(BaseModel):
    title: Optional[str] = None
    image_url: str
    link_url: Optional[str] = None
    sort_order: int = 0
    status: int = 1

class BannerUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None

class BannerOut(BaseModel):
    id: int
    title: Optional[str] = None
    image_url: str
    link_url: Optional[str] = None
    sort_order: int
    status: int
    class Config:
        from_attributes = True

# --- FriendLink ---
class FriendLinkCreate(BaseModel):
    name: str = Field(..., max_length=100)
    url: str = Field(..., max_length=255)
    sort_order: int = 0
    status: int = 1

class FriendLinkUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[int] = None

class FriendLinkOut(BaseModel):
    id: int
    name: str
    url: str
    sort_order: int
    status: int
    class Config:
        from_attributes = True
