import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("app")

from database import init_db
from utils.response import ok, fail
from utils.exceptions import BusinessException
from config import ALLOWED_ORIGINS

app = FastAPI(title="中小企业门户网站 API", version="0.1.0")


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常统一处理，根据 code 映射正确的 HTTP 状态码"""
    status_map = {400: 400, 403: 403, 404: 404}
    status_code = status_map.get(exc.code, 200)
    return JSONResponse(
        status_code=status_code,
        content=fail(exc.message, exc.code, exc.data)
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "data": None, "message": exc.detail}
        )
    import traceback
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "data": None, "message": "服务器内部错误"}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（框架骨架只包含 auth/users/permissions/menus/sys_config）
from routers import auth, users, permissions, menus, sys_config
from routers import portal, admin_content

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(permissions.router)
app.include_router(menus.router)
app.include_router(sys_config.router)
# 业务路由
app.include_router(portal.router)
app.include_router(admin_content.router)


@app.on_event("startup")
async def startup():
    init_db()
    logger.info("中小企业门户网站 API started")


@app.get("/health")
def health():
    return ok({"status": "ok"})


# ====== 上传文件托管 ======
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
# 双路径挂载：/uploads 供生产同源直访，/api/uploads 供前端开发代理（/api 前缀）访问
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/api/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads-api")


# ====== 前端静态文件托管（生产部署时使用） ======
# 开发模式下前端走 vite dev server (5173)，不经过这里
# 生产部署时 npm run build → 把 dist/ 内容复制到 backend/static/

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

if os.path.isdir(STATIC_DIR):
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # 排除 API 路径，避免 API 404 返回 HTML
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API 路径不存在")
        
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            if full_path.endswith(".html"):
                with open(file_path) as f:
                    content = f.read()
                return HTMLResponse(content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
            return FileResponse(file_path)
        
        index_path = os.path.join(STATIC_DIR, "index.html")
        with open(index_path) as f:
            content = f.read()
        return HTMLResponse(content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
