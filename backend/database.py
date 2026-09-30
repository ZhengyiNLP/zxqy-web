"""
数据库连接与初始化编排模块

功能描述：
- MySQL / SQLite 数据库连接配置
- 表结构创建与初始化编排

关键流程：
1. init_db() → create_all → migration.run_migrations() → seed.run_seed()
2. 迁移逻辑见 migration.py，种子数据见 seed.py
3. 外部模块统一 from database import get_db / Base / engine / SessionLocal
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging

logger = logging.getLogger("database")

# 数据库连接：优先环境变量，其次默认 SQLite 零配置启动（MySQL 时设置 DATABASE_URL）
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///" + os.path.join(os.path.dirname(__file__), "data", "app.db").replace("\\", "/"),
)

_is_sqlite = DATABASE_URL.startswith("sqlite")

if _is_sqlite:
    # SQLite 模式（测试或开发快速启动）
    DB_DIR = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(DB_DIR, exist_ok=True)
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # MySQL 模式
    engine = create_engine(DATABASE_URL, pool_recycle=3600, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database: create tables → run migrations → seed data."""
    # Import models to register them with Base
    import models as _models  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Run migrations for existing databases
    from migration import run_migrations
    run_migrations(engine)

    # Initialize seed data (admin user, permissions, roles, etc.)
    from seed import run_seed
    run_seed(SessionLocal)
