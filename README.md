# 中小企业门户网站（zxqy-web）

> 基于 FastAPI + Vue3 + TypeScript 的中小企业门户网站模板，前台门户展示 + 后台内容管理。

---

## 项目简介

面向中小企业的通用门户网站，支持企业信息展示（首页、新闻动态、产品展示、关于我们、企业文化、联系我们、留言咨询），后台提供完整的内容管理（新闻/产品/单页/轮播图/友情链接/留言的增删改查）。响应式布局，适配桌面端和移动端。

## 核心特性

- 前后端分离架构（FastAPI + Vue3 + Vite）
- 前台门户 + 后台管理双端
- 新闻/产品/单页内容管理（富文本）
- 产品多图图集展示
- 在线留言咨询
- 轮播图/友情链接管理
- 网站基础信息配置
- JWT 认证 + RBAC 权限系统
- 响应式布局（桌面端 + 移动端）
- SQLite 零配置启动，可平滑切换 MySQL

## 技术栈

| 端 | 技术 | 版本 |
|----|------|------|
| 后端 | FastAPI | 0.110+ |
| 前端 | Vue3 + TypeScript + Vite | 3.4+ |
| UI库 | Element Plus | 最新 |
| 数据库 | SQLite / MySQL | - |
| ORM | SQLAlchemy | 2.0+ |
| 认证 | JWT (python-jose + bcrypt) | - |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- uv（Python 包管理器）
- npm（随 Node.js 安装）

### 启动后端

```powershell
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

后端地址：http://localhost:8000
API文档：http://localhost:8000/docs
默认账号：admin / admin123

### 启动前端

```powershell
cd frontend
npm install
npm run dev
```

门户首页：http://localhost:5173/
管理后台：http://localhost:5173/login

## 打包发布

```powershell
# 构建前端
cd frontend
npm run build

# 将 dist/ 内容复制到 backend/static/
# 启动后端即可同时服务前后端
cd ../backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## 项目结构

```
zxqy-web/
├── backend/                 # 后端代码
│   ├── app/                 # (模板结构，本项目管理逻辑在根级)
│   ├── routers/             # 路由层
│   │   ├── portal.py        # 门户端接口
│   │   ├── admin_content.py # 管理端接口
│   │   └── auth.py          # 认证接口
│   ├── models.py            # 数据模型（用户+权限+10张业务表）
│   ├── schemas.py           # Pydantic 数据结构
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置
│   ├── database.py          # 数据库连接
│   ├── auth.py              # JWT 认证
│   ├── seed.py              # 种子数据
│   ├── uploads/             # 上传文件
│   └── pyproject.toml
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── api/business.ts  # 业务API封装
│   │   ├── views/portal/    # 门户页面（9个）
│   │   ├── views/admin/     # 管理页面（9个）
│   │   ├── layouts/         # 布局组件
│   │   ├── router/          # 路由配置
│   │   ├── stores/          # Pinia 状态管理
│   │   └── utils/api.ts     # axios 封装
│   └── package.json
├── sql/                     # SQL 脚本
├── docs/                    # 项目文档
└── .devflow/                # 流程管控（不提交git）
```

## 安全说明

- 首次部署后请立即修改 admin 默认密码
- 生产环境请设置环境变量：`ALLOWED_ORIGINS`、`JWT_SECRET`、`DATABASE_URL`
- `.env` 文件不要提交到版本库
- 上传文件限制 5MB，仅支持 jpg/png/gif/webp

## 文档索引

| 文档 | 路径 |
|------|------|
| 需求规格 | docs/需求规格.md |
| 面向客户的功能清单 | docs/面向客户的功能清单.md |
| 架构设计 | docs/架构设计.md |
| 数据库设计 | docs/数据库设计.md |
| API 契约 | docs/API契约.md |
| 测试手册 | docs/测试手册.md |
| 部署手册 | docs/部署手册.md |
| 功能完成情况 | docs/功能完成情况.md |

## 功能完成状态

28/28 功能点全部完成（100%）。

> AI生成
