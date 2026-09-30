"""门户端路由 - 访客公开接口"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Article, Product, ProductImage, Page, Message, Banner, FriendLink, Category, SysConfig
from schemas import MessageCreate
from utils.response import ok, fail
from datetime import datetime, timezone
import json

router = APIRouter(prefix="/api/v1/portal", tags=["门户-访客端"])


@router.get("/home")
def get_home(db: Session = Depends(get_db)):
    """首页数据聚合"""
    # 轮播图
    banners = db.query(Banner).filter(
        Banner.status == 1, Banner.deleted == 0
    ).order_by(Banner.sort_order).all()
    # 最新新闻
    article_count = int(_get_config(db, "home_article_count", "6"))
    latest_articles = db.query(Article).filter(
        Article.status == "published", Article.deleted == 0
    ).order_by(desc(Article.published_at)).limit(article_count).all()
    # 推荐产品
    product_count = int(_get_config(db, "home_product_count", "8"))
    recommend_products = db.query(Product).filter(
        Product.is_recommend == 1, Product.status == 1, Product.deleted == 0
    ).order_by(Product.sort_order).limit(product_count).all()
    # 企业简介
    about_page = db.query(Page).filter(Page.page_key == "about").first()
    about_summary = ""
    if about_page and about_page.content:
        # 取前200字作为摘要
        import re
        text = re.sub(r'<[^>]+>', '', about_page.content)
        about_summary = text[:200]
    # 友情链接
    friend_links = db.query(FriendLink).filter(
        FriendLink.status == 1, FriendLink.deleted == 0
    ).order_by(FriendLink.sort_order).all()

    return ok({
        "banners": [{
            "id": b.id, "title": b.title,
            "imageUrl": b.image_url, "linkUrl": b.link_url
        } for b in banners],
        "latestArticles": [{
            "id": a.id, "title": a.title, "summary": a.summary,
            "coverImage": a.cover_image,
            "publishedAt": a.published_at.isoformat() if a.published_at else None
        } for a in latest_articles],
        "recommendProducts": [{
            "id": p.id, "name": p.name, "shortDesc": p.short_desc,
            "coverImage": p.cover_image
        } for p in recommend_products],
        "aboutSummary": about_summary,
        "friendLinks": [{
            "id": f.id, "name": f.name, "url": f.url
        } for f in friend_links],
    })


@router.get("/categories")
def get_categories(type: str = Query(None), db: Session = Depends(get_db)):
    """栏目分类列表"""
    query = db.query(Category).filter(Category.deleted == 0, Category.status == 1)
    if type:
        query = query.filter(Category.type == type)
    cats = query.order_by(Category.sort_order).all()
    return ok([{
        "id": c.id, "name": c.name, "type": c.type,
        "sortOrder": c.sort_order
    } for c in cats])


@router.get("/articles")
def get_articles(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50),
    categoryId: int = Query(None),
    db: Session = Depends(get_db),
):
    """新闻列表"""
    query = db.query(Article).filter(Article.status == "published", Article.deleted == 0)
    if categoryId:
        query = query.filter(Article.category_id == categoryId)
    total = query.count()
    articles = query.order_by(desc(Article.published_at)).offset(
        (page - 1) * pageSize
    ).limit(pageSize).all()
    return ok({
        "list": [{
            "id": a.id, "title": a.title, "summary": a.summary,
            "coverImage": a.cover_image,
            "categoryName": a.category.name if a.category else None,
            "publishedAt": a.published_at.isoformat() if a.published_at else None
        } for a in articles],
        "total": total, "page": page, "pageSize": pageSize
    })


@router.get("/articles/{article_id}")
def get_article_detail(article_id: int, db: Session = Depends(get_db)):
    """新闻详情"""
    article = db.query(Article).filter(
        Article.id == article_id, Article.deleted == 0
    ).first()
    if not article:
        return fail("文章不存在", code=4041)
    # 增加浏览量
    article.view_count = (article.view_count or 0) + 1
    db.commit()
    # 上一篇
    prev = db.query(Article).filter(
        Article.id < article_id, Article.status == "published",
        Article.deleted == 0
    ).order_by(desc(Article.id)).first()
    # 下一篇
    nxt = db.query(Article).filter(
        Article.id > article_id, Article.status == "published",
        Article.deleted == 0
    ).order_by(Article.id).first()
    return ok({
        "id": article.id, "title": article.title, "summary": article.summary,
        "content": article.content, "coverImage": article.cover_image,
        "source": article.source, "viewCount": article.view_count,
        "categoryName": article.category.name if article.category else None,
        "publishedAt": article.published_at.isoformat() if article.published_at else None,
        "prevArticle": {"id": prev.id, "title": prev.title} if prev else {"id": 0, "title": ""},
        "nextArticle": {"id": nxt.id, "title": nxt.title} if nxt else {"id": 0, "title": ""},
    })


@router.get("/products")
def get_products(
    page: int = Query(1, ge=1),
    pageSize: int = Query(12, ge=1, le=50),
    categoryId: int = Query(None),
    db: Session = Depends(get_db),
):
    """产品列表"""
    query = db.query(Product).filter(Product.status == 1, Product.deleted == 0)
    if categoryId:
        query = query.filter(Product.category_id == categoryId)
    total = query.count()
    products = query.order_by(Product.sort_order).offset(
        (page - 1) * pageSize
    ).limit(pageSize).all()
    return ok({
        "list": [{
            "id": p.id, "name": p.name, "shortDesc": p.short_desc,
            "coverImage": p.cover_image
        } for p in products],
        "total": total, "page": page, "pageSize": pageSize
    })


@router.get("/products/{product_id}")
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    """产品详情"""
    product = db.query(Product).filter(
        Product.id == product_id, Product.deleted == 0
    ).first()
    if not product:
        return fail("产品不存在", code=4041)
    images = db.query(ProductImage).filter(
        ProductImage.product_id == product_id
    ).order_by(ProductImage.sort_order).all()
    return ok({
        "id": product.id, "name": product.name,
        "shortDesc": product.short_desc, "description": product.description,
        "coverImage": product.cover_image, "params": product.params,
        "categoryName": product.category.name if product.category else None,
        "images": [img.image_url for img in images],
    })


@router.get("/pages/{page_key}")
def get_page(page_key: str, db: Session = Depends(get_db)):
    """单页内容"""
    page = db.query(Page).filter(Page.page_key == page_key).first()
    if not page:
        return fail("页面不存在", code=4041)
    return ok({
        "id": page.id, "pageKey": page.page_key, "title": page.title,
        "content": page.content, "extraData": page.extra_data,
    })


@router.post("/messages")
def submit_message(req: MessageCreate, db: Session = Depends(get_db)):
    """提交留言"""
    msg = Message(
        name=req.name, phone=req.phone,
        email=req.email, content=req.content
    )
    db.add(msg)
    db.commit()
    return ok(message="留言成功，我们会尽快与您联系")


def _get_config(db: Session, key: str, default: str = "") -> str:
    """获取系统配置值"""
    cfg = db.query(SysConfig).filter(SysConfig.config_key == key).first()
    return cfg.config_value if cfg else default
