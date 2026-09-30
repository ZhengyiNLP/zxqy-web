# 中小企业门户网站 Docker 部署镜像
# 单服务模式：FastAPI 同时提供 API + 前端静态文件 + 上传文件
FROM python:3.12-slim

WORKDIR /app

# 系统依赖（bcrypt 需要）
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# 安装 uv（Python 包管理器）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 先复制依赖清单（利用 Docker 缓存层）
COPY pyproject.toml uv.lock ./

# 安装 Python 依赖
RUN uv sync --frozen --no-dev

# 复制后端代码 + 前端静态文件 + 演示数据（含 SQLite 数据库与上传图片）
COPY . .

EXPOSE 8000

# 启动服务（生产模式，多 worker）
CMD ["uv", "run", "--no-dev", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
