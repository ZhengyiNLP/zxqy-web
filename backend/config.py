import os
import secrets
import logging

logger = logging.getLogger("config")

# 数据库路径（优先环境变量，默认 SQLite 零配置启动；使用 MySQL 时设置 DATABASE_URL）
DATABASE_DIR = os.path.join(os.path.dirname(__file__), "data")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(DATABASE_DIR, "app.db").replace("\\", "/"),
)

# JWT配置 - 优先环境变量，其次本地持久化文件，最后自动生成（并保存）
JWT_SECRET_FILE = os.path.join(DATABASE_DIR, ".jwt_secret")

def _get_jwt_secret() -> str:
    """获取 JWT 密钥，确保重启后不会变化"""
    env_val = os.getenv("JWT_SECRET")
    if env_val:
        return env_val
    # 尝试读取本地文件
    try:
        with open(JWT_SECRET_FILE, "r") as f:
            secret = f.read().strip()
            if secret:
                return secret
    except FileNotFoundError:
        pass
    # 文件不存在，生成新密钥并保存
    secret = secrets.token_hex(32)
    os.makedirs(DATABASE_DIR, exist_ok=True)
    with open(JWT_SECRET_FILE, "w") as f:
        f.write(secret)
    os.chmod(JWT_SECRET_FILE, 0o600)
    return secret

JWT_SECRET = _get_jwt_secret()
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# CORS配置 - 生产环境应设置 ALLOWED_ORIGINS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

# CORS 安全警告
if "*" in ALLOWED_ORIGINS:
    logger.warning("=" * 50)
    logger.warning("⚠️  CORS 配置为允许所有来源 (*)")
    logger.warning("⚠️  生产环境请设置 ALLOWED_ORIGINS 环境变量")
    logger.warning("⚠️  示例: ALLOWED_ORIGINS=https://your-domain.com")
    logger.warning("=" * 50)
