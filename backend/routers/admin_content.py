"""管理端内容管理路由 - 管理员接口"""
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import (Article, Product, ProductImage, Page, Message, Banner,
                    FriendLink, Category, SysConfig)
from schemas import (ArticleCreate, ArticleUpdate, ArticleStatusUpdate,
                     ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate,
                     PageUpdate, BannerCreate, BannerUpdate,
                     FriendLinkCreate, FriendLinkUpdate)
from auth import get_current_user
from utils.response import ok, fail
from datetime import datetime, timezone
import os, uuid

router = APIRouter(prefix="/api/v1/admin", tags=["管理端-内容管理"])

# ====== Dashboard ======

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """仪表盘"""
    article_count = db.query(Article).filter(Article.deleted == 0).count()
    product_count = db.query(Product).filter(Product.deleted == 0).count()
    unread_count = db.query(Message).filter(Message.is_read == 0, Message.deleted == 0).count()
    banner_count = db.query(Banner).filter(Banner.deleted == 0).count()
    recent_msgs = db.query(Message).filter(Message.deleted == 0).order_by(
        desc(Message.created_at)
    ).limit(5).all()
    return ok({
        "articleCount": article_count,
        "productCount": product_count,
        "unreadMessageCount": unread_count,
        "bannerCount": banner_count,
        "recentMessages": [{
            "id": m.id, "name": m.name, "phone": m.phone,
            "content": m.content[:100], "isRead": m.is_read,
            "createdAt": m.created_at.isoformat() if m.created_at else None
        } for m in recent_msgs],
    })

# ====== Category ======

@router.get("/categories")
def list_categories(type: str = Query(None), db: Session = Depends(get_db), user=Depends(get_current_user)):
    query = db.query(Category).filter(Category.deleted == 0)
    if type:
        query = query.filter(Category.type == type)
    cats = query.order_by(Category.sort_order).all()
    return ok([{
        "id": c.id, "name": c.name, "type": c.type,
        "sortOrder": c.sort_order, "status": c.status
    } for c in cats])

@router.post("/categories")
def create_category(req: CategoryCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cat = Category(name=req.name, type=req.type, sort_order=req.sort_order, status=req.status)
    db.add(cat); db.commit(); db.refresh(cat)
    return ok({"id": cat.id}, "创建成功")

@router.put("/categories/{cat_id}")
def update_category(cat_id: int, req: CategoryUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == cat_id, Category.deleted == 0).first()
    if not cat: return fail("分类不存在", code=4041)
    if req.name is not None: cat.name = req.name
    if req.sort_order is not None: cat.sort_order = req.sort_order
    if req.status is not None: cat.status = req.status
    db.commit()
    return ok(message="更新成功")

@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # 检查是否有关联内容
    art_count = db.query(Article).filter(Article.category_id == cat_id, Article.deleted == 0).count()
    prod_count = db.query(Product).filter(Product.category_id == cat_id, Product.deleted == 0).count()
    if art_count + prod_count > 0:
        return fail("该分类下有内容，无法删除", code=4001)
    cat = db.query(Category).filter(Category.id == cat_id, Category.deleted == 0).first()
    if not cat: return fail("分类不存在", code=4041)
    cat.deleted = 1; db.commit()
    return ok(message="删除成功")

# ====== Article ======

@router.get("/articles")
def list_articles(
    page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=50),
    categoryId: int = Query(None), title: str = Query(None),
    db: Session = Depends(get_db), user=Depends(get_current_user),
):
    query = db.query(Article).filter(Article.deleted == 0)
    if categoryId: query = query.filter(Article.category_id == categoryId)
    if title: query = query.filter(Article.title.contains(title))
    total = query.count()
    articles = query.order_by(desc(Article.created_at)).offset(
        (page - 1) * pageSize
    ).limit(pageSize).all()
    return ok({
        "list": [{
            "id": a.id, "title": a.title, "summary": a.summary,
            "coverImage": a.cover_image, "categoryId": a.category_id,
            "categoryName": a.category.name if a.category else None,
            "status": a.status, "source": a.source,
            "publishedAt": a.published_at.isoformat() if a.published_at else None,
            "createdAt": a.created_at.isoformat() if a.created_at else None,
        } for a in articles],
        "total": total, "page": page, "pageSize": pageSize
    })

@router.post("/articles")
def create_article(req: ArticleCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    article = Article(
        category_id=req.category_id, title=req.title, summary=req.summary,
        content=req.content, cover_image=req.cover_image, source=req.source,
        status=req.status,
        published_at=datetime.now(timezone.utc) if req.status == "published" else None,
    )
    db.add(article); db.commit(); db.refresh(article)
    return ok({"id": article.id}, "创建成功")

@router.put("/articles/{article_id}")
def update_article(article_id: int, req: ArticleUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    article = db.query(Article).filter(Article.id == article_id, Article.deleted == 0).first()
    if not article: return fail("文章不存在", code=4041)
    if req.category_id is not None: article.category_id = req.category_id
    if req.title is not None: article.title = req.title
    if req.summary is not None: article.summary = req.summary
    if req.content is not None: article.content = req.content
    if req.cover_image is not None: article.cover_image = req.cover_image
    if req.source is not None: article.source = req.source
    if req.status is not None:
        article.status = req.status
        if req.status == "published" and not article.published_at:
            article.published_at = datetime.now(timezone.utc)
    db.commit()
    return ok(message="更新成功")

@router.delete("/articles/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    article = db.query(Article).filter(Article.id == article_id, Article.deleted == 0).first()
    if not article: return fail("文章不存在", code=4041)
    article.deleted = 1; db.commit()
    return ok(message="删除成功")

@router.put("/articles/{article_id}/status")
def update_article_status(article_id: int, req: ArticleStatusUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    article = db.query(Article).filter(Article.id == article_id, Article.deleted == 0).first()
    if not article: return fail("文章不存在", code=4041)
    article.status = req.status
    if req.status == "published" and not article.published_at:
        article.published_at = datetime.now(timezone.utc)
    db.commit()
    return ok(message="状态更新成功")

# ====== Product ======

@router.get("/products")
def list_products(
    page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=50),
    categoryId: int = Query(None), name: str = Query(None),
    db: Session = Depends(get_db), user=Depends(get_current_user),
):
    query = db.query(Product).filter(Product.deleted == 0)
    if categoryId: query = query.filter(Product.category_id == categoryId)
    if name: query = query.filter(Product.name.contains(name))
    total = query.count()
    products = query.order_by(Product.sort_order).offset(
        (page - 1) * pageSize
    ).limit(pageSize).all()
    return ok({
        "list": [{
            "id": p.id, "name": p.name, "shortDesc": p.short_desc,
            "coverImage": p.cover_image, "categoryId": p.category_id,
            "categoryName": p.category.name if p.category else None,
            "isRecommend": p.is_recommend, "status": p.status,
            "sortOrder": p.sort_order,
        } for p in products],
        "total": total, "page": page, "pageSize": pageSize
    })

@router.post("/products")
def create_product(req: ProductCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = Product(
        category_id=req.category_id, name=req.name, short_desc=req.short_desc,
        description=req.description, cover_image=req.cover_image,
        params=req.params, is_recommend=req.is_recommend,
        sort_order=req.sort_order, status=req.status,
    )
    db.add(product); db.flush()
    if req.images:
        for idx, url in enumerate(req.images):
            db.add(ProductImage(
                product_id=product.id, image_url=url, sort_order=idx
            ))
    db.commit()
    return ok({"id": product.id}, "创建成功")

@router.put("/products/{product_id}")
def update_product(product_id: int, req: ProductUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id, Product.deleted == 0).first()
    if not product: return fail("产品不存在", code=4041)
    if req.category_id is not None: product.category_id = req.category_id
    if req.name is not None: product.name = req.name
    if req.short_desc is not None: product.short_desc = req.short_desc
    if req.description is not None: product.description = req.description
    if req.cover_image is not None: product.cover_image = req.cover_image
    if req.params is not None: product.params = req.params
    if req.is_recommend is not None: product.is_recommend = req.is_recommend
    if req.sort_order is not None: product.sort_order = req.sort_order
    if req.status is not None: product.status = req.status
    # 更新图集
    if req.images is not None:
        db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
        for idx, url in enumerate(req.images):
            db.add(ProductImage(product_id=product_id, image_url=url, sort_order=idx))
    db.commit()
    return ok(message="更新成功")

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id, Product.deleted == 0).first()
    if not product: return fail("产品不存在", code=4041)
    db.query(ProductImage).filter(ProductImage.product_id == product_id).delete()
    product.deleted = 1; db.commit()
    return ok(message="删除成功")

# ====== Page ======

@router.get("/pages")
def list_pages(db: Session = Depends(get_db), user=Depends(get_current_user)):
    pages = db.query(Page).order_by(Page.id).all()
    return ok([{
        "id": p.id, "pageKey": p.page_key, "title": p.title,
        "content": p.content, "extraData": p.extra_data
    } for p in pages])

@router.put("/pages/{page_id}")
def update_page(page_id: int, req: PageUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    page = db.query(Page).filter(Page.id == page_id).first()
    if not page: return fail("页面不存在", code=4041)
    if req.title is not None: page.title = req.title
    if req.content is not None: page.content = req.content
    if req.extra_data is not None: page.extra_data = req.extra_data
    db.commit()
    return ok(message="更新成功")

# ====== Message ======

@router.get("/messages")
def list_messages(
    page: int = Query(1, ge=1), pageSize: int = Query(10, ge=1, le=50),
    isRead: int = Query(None),
    db: Session = Depends(get_db), user=Depends(get_current_user),
):
    query = db.query(Message).filter(Message.deleted == 0)
    if isRead is not None: query = query.filter(Message.is_read == isRead)
    total = query.count()
    msgs = query.order_by(desc(Message.created_at)).offset(
        (page - 1) * pageSize
    ).limit(pageSize).all()
    return ok({
        "list": [{
            "id": m.id, "name": m.name, "phone": m.phone,
            "email": m.email, "content": m.content, "isRead": m.is_read,
            "createdAt": m.created_at.isoformat() if m.created_at else None
        } for m in msgs],
        "total": total, "page": page, "pageSize": pageSize
    })

@router.get("/messages/{msg_id}")
def get_message(msg_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    msg = db.query(Message).filter(Message.id == msg_id, Message.deleted == 0).first()
    if not msg: return fail("留言不存在", code=4041)
    return ok({
        "id": msg.id, "name": msg.name, "phone": msg.phone,
        "email": msg.email, "content": msg.content, "isRead": msg.is_read,
        "createdAt": msg.created_at.isoformat() if msg.created_at else None
    })

@router.put("/messages/{msg_id}/read")
def mark_message_read(msg_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    msg = db.query(Message).filter(Message.id == msg_id, Message.deleted == 0).first()
    if not msg: return fail("留言不存在", code=4041)
    msg.is_read = 1; db.commit()
    return ok(message="已标记为已读")

@router.delete("/messages/{msg_id}")
def delete_message(msg_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    msg = db.query(Message).filter(Message.id == msg_id, Message.deleted == 0).first()
    if not msg: return fail("留言不存在", code=4041)
    msg.deleted = 1; db.commit()
    return ok(message="删除成功")

# ====== Banner ======

@router.get("/banners")
def list_banners(db: Session = Depends(get_db), user=Depends(get_current_user)):
    banners = db.query(Banner).filter(Banner.deleted == 0).order_by(Banner.sort_order).all()
    return ok([{
        "id": b.id, "title": b.title, "imageUrl": b.image_url,
        "linkUrl": b.link_url, "sortOrder": b.sort_order, "status": b.status
    } for b in banners])

@router.post("/banners")
def create_banner(req: BannerCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    banner = Banner(title=req.title, image_url=req.image_url,
                    link_url=req.link_url, sort_order=req.sort_order, status=req.status)
    db.add(banner); db.commit(); db.refresh(banner)
    return ok({"id": banner.id}, "创建成功")

@router.put("/banners/{banner_id}")
def update_banner(banner_id: int, req: BannerUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    banner = db.query(Banner).filter(Banner.id == banner_id, Banner.deleted == 0).first()
    if not banner: return fail("轮播图不存在", code=4041)
    if req.title is not None: banner.title = req.title
    if req.image_url is not None: banner.image_url = req.image_url
    if req.link_url is not None: banner.link_url = req.link_url
    if req.sort_order is not None: banner.sort_order = req.sort_order
    if req.status is not None: banner.status = req.status
    db.commit()
    return ok(message="更新成功")

@router.delete("/banners/{banner_id}")
def delete_banner(banner_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    banner = db.query(Banner).filter(Banner.id == banner_id, Banner.deleted == 0).first()
    if not banner: return fail("轮播图不存在", code=4041)
    banner.deleted = 1; db.commit()
    return ok(message="删除成功")

# ====== FriendLink ======

@router.get("/friend-links")
def list_friend_links(db: Session = Depends(get_db), user=Depends(get_current_user)):
    links = db.query(FriendLink).filter(FriendLink.deleted == 0).order_by(FriendLink.sort_order).all()
    return ok([{
        "id": f.id, "name": f.name, "url": f.url,
        "sortOrder": f.sort_order, "status": f.status
    } for f in links])

@router.post("/friend-links")
def create_friend_link(req: FriendLinkCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    link = FriendLink(name=req.name, url=req.url, sort_order=req.sort_order, status=req.status)
    db.add(link); db.commit(); db.refresh(link)
    return ok({"id": link.id}, "创建成功")

@router.put("/friend-links/{link_id}")
def update_friend_link(link_id: int, req: FriendLinkUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    link = db.query(FriendLink).filter(FriendLink.id == link_id, FriendLink.deleted == 0).first()
    if not link: return fail("友情链接不存在", code=4041)
    if req.name is not None: link.name = req.name
    if req.url is not None: link.url = req.url
    if req.sort_order is not None: link.sort_order = req.sort_order
    if req.status is not None: link.status = req.status
    db.commit()
    return ok(message="更新成功")

@router.delete("/friend-links/{link_id}")
def delete_friend_link(link_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    link = db.query(FriendLink).filter(FriendLink.id == link_id, FriendLink.deleted == 0).first()
    if not link: return fail("友情链接不存在", code=4041)
    link.deleted = 1; db.commit()
    return ok(message="删除成功")

# ====== Site Config ======

@router.get("/site-config")
def get_site_config(db: Session = Depends(get_db), user=Depends(get_current_user)):
    configs = db.query(SysConfig).all()
    return ok({c.config_key: c.config_value for c in configs})

@router.put("/site-config")
def save_site_config(configs: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    for key, value in configs.items():
        cfg = db.query(SysConfig).filter(SysConfig.config_key == key).first()
        if cfg:
            cfg.config_value = str(value)
        else:
            db.add(SysConfig(config_name=key, config_key=key, config_value=str(value)))
    db.commit()
    return ok(message="配置保存成功")

# ====== Upload ======

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    # 限制文件类型
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        return fail("仅支持 jpg/png/gif/webp 格式", code=4001)
    # 限制大小 (5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        return fail("文件大小不能超过5MB", code=4001)
    # 保存文件
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    now = datetime.now(timezone.utc)
    year_month = f"{now.year}/{now.month:02d}"
    save_dir = os.path.join(upload_dir, year_month)
    os.makedirs(save_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(save_dir, filename)
    with open(filepath, "wb") as f:
        f.write(content)
    url = f"/uploads/{year_month}/{filename}"
    return ok({"url": url}, "上传成功")
