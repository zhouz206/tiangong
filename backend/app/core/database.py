"""
数据库配置
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 确保数据目录存在
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 数据库 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{os.path.join(DATA_DIR, 'tiangong.db')}"
)

# 创建引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# 同步引擎（用于初始化）
sync_engine = create_engine(
    DATABASE_URL.replace("+aiosqlite", ""),
    echo=False,
    future=True
)

# Session 配置
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base 类
Base = declarative_base()


async def get_db():
    """获取数据库会话"""
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


def init_db():
    """初始化数据库（创建表）"""
    Base.metadata.create_all(bind=sync_engine)
