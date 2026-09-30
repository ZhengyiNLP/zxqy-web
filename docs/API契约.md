# 中小企业门户网站 API 契约

> 创建时间：2026-09-30
> 状态：待确认
> 关联流程：fullstack-dev-flow stage-2
> 关联数据库设计：docs/数据库设计.md

---

## 一、通用约定

### 1.1 基础路径

- 后端 API 基础路径：`/api/v1`
- 访客端接口前缀：`/api/v1/portal/`
- 管理端接口前缀：`/api/v1/admin/`

### 1.2 鉴权方式

- 方式：Bearer Token (JWT)
- Header：`Authorization: Bearer <token>`
- Token 获取：管理员登录接口返回
- Token 过期：7 天（可配置）
- 访客端接口无需鉴权

### 1.3 通用响应结构

```json
{
  "code": 0,
  "msg": "success",
  "data": { ... }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 0=成功，非0=失败 |
| msg | string | 提示消息 |
| data | object/array/null | 业务数据 |

### 1.4 通用错误码

| 错误码 | 含义 |
|--------|------|
| 0 | 成功 |
| 4001 | 参数错误 |
| 4011 | 未登录 |
| 4012 | Token 过期 |
| 4031 | 无权限 |
| 4041 | 资源不存在 |
| 5000 | 服务器内部错误 |

### 1.5 分页约定

入参：

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| page | int | 1 | 页码 |
| pageSize | int | 10 | 每页条数 |

出参：

```json
{
  "list": [ ... ],
  "total": 100,
  "page": 1,
  "pageSize": 10
}
```

---

## 二、访客端接口（前台门户）

### 2.1 首页数据聚合

- **路径**：`GET /api/v1/portal/home`
- **鉴权**：不需要
- **入参**：无
- **出参**：

```json
{
  "code": 0,
  "data": {
    "banners": [
      { "id": 1, "title": "广告1", "imageUrl": "/uploads/xxx.jpg", "linkUrl": "/news/1" }
    ],
    "latestArticles": [
      { "id": 1, "title": "新闻标题", "summary": "摘要", "coverImage": "/uploads/xxx.jpg", "publishedAt": "2026-09-30T10:00:00" }
    ],
    "recommendProducts": [
      { "id": 1, "name": "产品名", "shortDesc": "描述", "coverImage": "/uploads/xxx.jpg" }
    ],
    "aboutSummary": "企业简介摘要内容...",
    "friendLinks": [
      { "id": 1, "name": "友情链接1", "url": "https://example.com" }
    ]
  }
}
```

### 2.2 新闻列表

- **路径**：`GET /api/v1/portal/articles`
- **鉴权**：不需要
- **入参**（query）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| pageSize | int | 否 | 每页条数，默认10 |
| categoryId | int | 否 | 栏目筛选 |

- **出参**：

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 1,
        "title": "新闻标题",
        "summary": "摘要",
        "coverImage": "/uploads/xxx.jpg",
        "categoryName": "企业新闻",
        "publishedAt": "2026-09-30T10:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "pageSize": 10
  }
}
```

### 2.3 新闻详情

- **路径**：`GET /api/v1/portal/articles/{id}`
- **鉴权**：不需要
- **入参**：path 参数 id
- **出参**：

```json
{
  "code": 0,
  "data": {
    "id": 1,
    "title": "新闻标题",
    "summary": "摘要",
    "content": "<p>富文本HTML</p>",
    "coverImage": "/uploads/xxx.jpg",
    "source": "来源",
    "viewCount": 100,
    "categoryName": "企业新闻",
    "publishedAt": "2026-09-30T10:00:00",
    "prevArticle": { "id": 0, "title": "" },
    "nextArticle": { "id": 2, "title": "下一篇标题" }
  }
}
```

### 2.4 产品列表

- **路径**：`GET /api/v1/portal/products`
- **鉴权**：不需要
- **入参**（query）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| pageSize | int | 否 | 每页条数，默认12 |
| categoryId | int | 否 | 分类筛选 |

- **出参**：

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 1,
        "name": "产品名称",
        "shortDesc": "简短描述",
        "coverImage": "/uploads/xxx.jpg"
      }
    ],
    "total": 30,
    "page": 1,
    "pageSize": 12
  }
}
```

### 2.5 产品详情

- **路径**：`GET /api/v1/portal/products/{id}`
- **鉴权**：不需要
- **入参**：path 参数 id
- **出参**：

```json
{
  "code": 0,
  "data": {
    "id": 1,
    "name": "产品名称",
    "shortDesc": "简短描述",
    "description": "<p>富文本HTML</p>",
    "coverImage": "/uploads/xxx.jpg",
    "params": [ { "key": "规格", "value": "100x50" } ],
    "images": [ "/uploads/img1.jpg", "/uploads/img2.jpg" ],
    "categoryName": "产品分类1"
  }
}
```

### 2.6 单页内容

- **路径**：`GET /api/v1/portal/pages/{page_key}`
- **鉴权**：不需要
- **入参**：path 参数 page_key（about/culture/contact）
- **出参**：

```json
{
  "code": 0,
  "data": {
    "id": 1,
    "pageKey": "about",
    "title": "关于我们",
    "content": "<p>富文本HTML</p>",
    "extraData": null
  }
}
```

> 联系我们页（page_key=contact）extraData 返回结构化联系信息：
```json
{ "address": "地址", "phone": "电话", "email": "邮箱", "workTime": "办公时间" }
```

### 2.7 提交留言

- **路径**：`POST /api/v1/portal/messages`
- **鉴权**：不需要
- **入参**（JSON body）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 姓名 |
| phone | string | 是 | 联系电话 |
| email | string | 否 | 邮箱 |
| content | string | 是 | 留言内容 |

- **出参**：

```json
{
  "code": 0,
  "msg": "留言成功，我们会尽快与您联系"
}
```

- **错误码**：
  - 4001：参数错误（必填项为空、手机号格式不对）

### 2.8 栏目分类列表（前台）

- **路径**：`GET /api/v1/portal/categories`
- **鉴权**：不需要
- **入参**（query）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | article/product，不传返回全部 |

- **出参**：

```json
{
  "code": 0,
  "data": [
    { "id": 1, "name": "企业新闻", "type": "article", "sortOrder": 0 }
  ]
}
```

---

## 三、管理端接口（后台管理系统）

### 3.1 管理员登录

- **路径**：`POST /api/v1/admin/auth/login`
- **鉴权**：不需要
- **入参**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

- **出参**：

```json
{
  "code": 0,
  "data": {
    "token": "eyJhbGc...",
    "userInfo": {
      "id": 1,
      "username": "admin",
      "nickname": "管理员",
      "avatar": null
    }
  }
}
```

- **错误码**：4001（用户名或密码错误）、4002（账号已被禁用）

### 3.2 修改密码

- **路径**：`PUT /api/v1/admin/auth/password`
- **鉴权**：需要
- **入参**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| oldPassword | string | 是 | 旧密码 |
| newPassword | string | 是 | 新密码 |

### 3.3 仪表盘

- **路径**：`GET /api/v1/admin/dashboard`
- **鉴权**：需要
- **出参**：

```json
{
  "code": 0,
  "data": {
    "articleCount": 50,
    "productCount": 30,
    "unreadMessageCount": 5,
    "bannerCount": 4,
    "recentMessages": [
      { "id": 1, "name": "张三", "phone": "138xxx", "content": "咨询...", "createdAt": "2026-09-30T10:00:00", "isRead": 0 }
    ]
  }
}
```

### 3.4 栏目分类管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 分类列表 | GET | /api/v1/admin/categories | 支持type筛选 |
| 新增分类 | POST | /api/v1/admin/categories | name/type/sortOrder/status |
| 编辑分类 | PUT | /api/v1/admin/categories/{id} | 同上 |
| 删除分类 | DELETE | /api/v1/admin/categories/{id} | 有关联内容时提示 |

### 3.5 新闻管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 新闻列表 | GET | /api/v1/admin/articles | 支持categoryId筛选、title搜索、分页 |
| 新增新闻 | POST | /api/v1/admin/articles | title/categoryId/summary/content/coverImage/source/status |
| 编辑新闻 | PUT | /api/v1/admin/articles/{id} | 同上 |
| 删除新闻 | DELETE | /api/v1/admin/articles/{id} | 软删除 |
| 修改状态 | PUT | /api/v1/admin/articles/{id}/status | status: draft/published |

### 3.6 产品管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 产品列表 | GET | /api/v1/admin/products | 支持categoryId筛选、name搜索、分页 |
| 新增产品 | POST | /api/v1/admin/products | name/categoryId/shortDesc/description/coverImage/params/isRecommend/sortOrder/status/images[] |
| 编辑产品 | PUT | /api/v1/admin/products/{id} | 同上 |
| 删除产品 | DELETE | /api/v1/admin/products/{id} | 软删除(同时删除关联图片) |

### 3.7 单页内容管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 页面列表 | GET | /api/v1/admin/pages | - |
| 编辑页面 | PUT | /api/v1/admin/pages/{id} | title/content/extraData |

### 3.8 轮播图管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 轮播图列表 | GET | /api/v1/admin/banners | - |
| 新增 | POST | /api/v1/admin/banners | title/imageUrl/linkUrl/sortOrder/status |
| 编辑 | PUT | /api/v1/admin/banners/{id} | 同上 |
| 删除 | DELETE | /api/v1/admin/banners/{id} | 软删除 |

### 3.9 友情链接管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 列表 | GET | /api/v1/admin/friend-links | - |
| 新增 | POST | /api/v1/admin/friend-links | name/url/sortOrder/status |
| 编辑 | PUT | /api/v1/admin/friend-links/{id} | 同上 |
| 删除 | DELETE | /api/v1/admin/friend-links/{id} | 软删除 |

### 3.10 留言管理

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 留言列表 | GET | /api/v1/admin/messages | 支持isRead筛选、分页 |
| 留言详情 | GET | /api/v1/admin/messages/{id} | - |
| 标记已读 | PUT | /api/v1/admin/messages/{id}/read | - |
| 删除留言 | DELETE | /api/v1/admin/messages/{id} | 软删除 |

### 3.11 网站配置

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取配置 | GET | /api/v1/admin/site-config | 返回全部配置键值对 |
| 保存配置 | PUT | /api/v1/admin/site-config | 批量更新 |

### 3.12 文件上传

- **路径**：`POST /api/v1/admin/upload`
- **鉴权**：需要
- **入参**：multipart/form-data，字段 `file`
- **出参**：

```json
{
  "code": 0,
  "data": { "url": "/uploads/2026/09/xxx.jpg" }
}
```

---

## 四、五列对应矩阵（需求→实体→表→API→模块）

| 需求功能点 | 核心实体 | 数据库表 | API接口 | 架构模块 |
|----------|---------|---------|---------|---------|
| 首页轮播图展示 | 轮播图 | t_banner | GET /portal/home (banners) | banner模块 |
| 首页企业简介 | 单页内容 | t_page | GET /portal/home (aboutSummary) | page模块 |
| 首页最新动态 | 新闻文章 | t_article | GET /portal/home (latestArticles) | article模块 |
| 首页产品精选 | 产品展示 | t_product | GET /portal/home (recommendProducts) | product模块 |
| 首页友情链接 | 友情链接 | t_friend_link | GET /portal/home (friendLinks) | friend_link模块 |
| 新闻列表页 | 新闻文章 | t_article, t_category | GET /portal/articles | article模块 |
| 新闻详情页 | 新闻文章 | t_article | GET /portal/articles/{id} | article模块 |
| 产品列表页 | 产品展示 | t_product, t_category | GET /portal/products | product模块 |
| 产品详情页 | 产品展示 | t_product, t_product_image | GET /portal/products/{id} | product模块 |
| 关于我们页 | 单页内容 | t_page | GET /portal/pages/about | page模块 |
| 企业文化页 | 单页内容 | t_page | GET /portal/pages/culture | page模块 |
| 联系我们页 | 单页内容 | t_page | GET /portal/pages/contact | page模块 |
| 留言提交 | 留言咨询 | t_message | POST /portal/messages | message模块 |
| 管理员登录 | 管理员 | t_admin | POST /admin/auth/login | auth模块 |
| 仪表盘概览 | 管理员 | t_admin及各表 | GET /admin/dashboard | dashboard模块 |
| 栏目分类CRUD | 栏目分类 | t_category | /admin/categories (CRUD) | category模块 |
| 新闻CRUD | 新闻文章 | t_article | /admin/articles (CRUD) | article模块 |
| 新闻状态管理 | 新闻文章 | t_article | PUT /admin/articles/{id}/status | article模块 |
| 产品CRUD | 产品展示 | t_product, t_product_image | /admin/products (CRUD) | product模块 |
| 单页内容编辑 | 单页内容 | t_page | PUT /admin/pages/{id} | page模块 |
| 轮播图CRUD | 轮播图 | t_banner | /admin/banners (CRUD) | banner模块 |
| 友情链接CRUD | 友情链接 | t_friend_link | /admin/friend-links (CRUD) | friend_link模块 |
| 留言查看处理 | 留言咨询 | t_message | /admin/messages (CRUD) | message模块 |
| 网站基础信息设置 | 管理员 | t_site_config | /admin/site-config (GET/PUT) | config模块 |
| 修改密码 | 管理员 | t_admin | PUT /admin/auth/password | auth模块 |

> 矩阵无空行，28个需求功能点全部覆盖。

---

## 五、变更记录

| 日期 | 变更内容 | 变更人 |
|------|---------|--------|
| 2026-09-30 | 初始创建 | AI+用户 |

> AI生成
