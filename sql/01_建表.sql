-- ================================================
-- 中小企业门户网站 建表脚本
-- 数据库: SQLite (兼容 MySQL，切换时改连接串即可)
-- 创建时间: 2026-09-30
-- ================================================

-- 1. 管理员表
CREATE TABLE IF NOT EXISTS t_admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(100) NOT NULL,
    nickname VARCHAR(50),
    avatar VARCHAR(255),
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted TINYINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_admin_username ON t_admin(username);

-- 2. 栏目分类表
CREATE TABLE IF NOT EXISTS t_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted TINYINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_category_type ON t_category(type);
CREATE INDEX IF NOT EXISTS idx_category_sort ON t_category(sort_order);

-- 3. 新闻文章表
CREATE TABLE IF NOT EXISTS t_article (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    summary VARCHAR(500),
    content TEXT NOT NULL,
    cover_image VARCHAR(255),
    source VARCHAR(100),
    view_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    published_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted TINYINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_article_category ON t_article(category_id);
CREATE INDEX IF NOT EXISTS idx_article_status_pub ON t_article(status, published_at);
CREATE INDEX IF NOT EXISTS idx_article_created ON t_article(created_at);

-- 4. 产品表
CREATE TABLE IF NOT EXISTS t_product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    short_desc VARCHAR(500),
    description TEXT NOT NULL,
    cover_image VARCHAR(255),
    params TEXT,
    is_recommend TINYINT NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted TINYINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_product_category ON t_product(category_id);
CREATE INDEX IF NOT EXISTS idx_product_recommend ON t_product(is_recommend, status);
CREATE INDEX IF NOT EXISTS idx_product_sort ON t_product(sort_order);

-- 5. 产品图片表
CREATE TABLE IF NOT EXISTS t_product_image (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_pimage_product ON t_product_image(product_id);

-- 6. 单页内容表
CREATE TABLE IF NOT EXISTS t_page (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_key VARCHAR(50) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    extra_data TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_page_key ON t_page(page_key);

-- 7. 留言表
CREATE TABLE IF NOT EXISTS t_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    content TEXT NOT NULL,
    is_read TINYINT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted TINYINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_message_read ON t_message(is_read);
CREATE INDEX IF NOT EXISTS idx_message_created ON t_message(created_at);

-- 8. 轮播图表
CREATE TABLE IF NOT EXISTS t_banner (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200),
    image_url VARCHAR(255) NOT NULL,
    link_url VARCHAR(255),
    sort_order INTEGER NOT NULL DEFAULT 0,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted TINYINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_banner_status_sort ON t_banner(status, sort_order);

-- 9. 友情链接表
CREATE TABLE IF NOT EXISTS t_friend_link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    url VARCHAR(255) NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted TINYINT NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_flink_status_sort ON t_friend_link(status, sort_order);

-- 10. 网站配置表
CREATE TABLE IF NOT EXISTS t_site_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    remark VARCHAR(200),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_config_key ON t_site_config(config_key);

-- ================================================
-- 初始数据
-- ================================================

-- 默认管理员 (admin / admin123)
-- bcrypt hash for 'admin123': $2b$12$... (运行时由 seed.py 生成)
INSERT INTO t_admin (username, password_hash, nickname, status) VALUES ('admin', '__SEED_GENERATED__', '超级管理员', 1);

-- 默认栏目分类
INSERT INTO t_category (name, type, sort_order, status) VALUES ('企业新闻', 'article', 1, 1);
INSERT INTO t_category (name, type, sort_order, status) VALUES ('行业资讯', 'article', 2, 1);
INSERT INTO t_category (name, type, sort_order, status) VALUES ('通知公告', 'article', 3, 1);
INSERT INTO t_category (name, type, sort_order, status) VALUES ('产品分类一', 'product', 1, 1);
INSERT INTO t_category (name, type, sort_order, status) VALUES ('产品分类二', 'product', 2, 1);

-- 默认单页内容
INSERT INTO t_page (page_key, title, content) VALUES ('about', '关于我们', '<p>这里是关于我们页面内容，请在后台管理中编辑。</p>');
INSERT INTO t_page (page_key, title, content) VALUES ('culture', '企业文化', '<p>这里是企业文化页面内容，请在后台管理中编辑。</p>');
INSERT INTO t_page (page_key, title, content, extra_data) VALUES ('contact', '联系我们', '<p>这里是联系我们页面内容。</p>', '{"address":"请编辑企业地址","phone":"请编辑联系电话","email":"请编辑邮箱","workTime":"周一至周五 9:00-18:00"}');

-- 默认网站配置
INSERT INTO t_site_config (config_key, config_value, remark) VALUES ('site_name', '中小企业门户网站', '网站名称');
INSERT INTO t_site_config (config_key, config_value, remark) VALUES ('site_logo', '', '网站Logo');
INSERT INTO t_site_config (config_key, config_value, remark) VALUES ('icp', '', 'ICP备案号');
INSERT INTO t_site_config (config_key, config_value, remark) VALUES ('home_article_count', '6', '首页最新动态展示条数');
INSERT INTO t_site_config (config_key, config_value, remark) VALUES ('home_product_count', '8', '首页产品精选展示条数');
