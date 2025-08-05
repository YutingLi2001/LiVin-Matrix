"""
数据库连接配置模块
"""

from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import QueuePool

from .config import settings

# 创建基础模型类
Base = declarative_base()

# 全局引擎和会话工厂变量
_async_engine: Optional[AsyncEngine] = None


def get_async_engine() -> AsyncEngine:
    """获取或创建异步数据库引擎"""
    global _async_engine
    if _async_engine is None:
        if not settings.DATABASE_URL:
            # 为测试环境提供默认的SQLite内存数据库
            database_url = "sqlite+aiosqlite:///:memory:"
        else:
            database_url = settings.DATABASE_URL
            # 转换为异步数据库URL
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
            elif database_url.startswith("sqlite://"):
                database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://")

        _async_engine = create_async_engine(
            database_url,
            poolclass=QueuePool if not database_url.startswith("sqlite") else None,
            pool_size=settings.DB_POOL_SIZE if not database_url.startswith("sqlite") else None,
            max_overflow=settings.DB_MAX_OVERFLOW
            if not database_url.startswith("sqlite")
            else None,
            pool_recycle=settings.DB_POOL_RECYCLE
            if not database_url.startswith("sqlite")
            else None,
            pool_pre_ping=settings.DB_POOL_PRE_PING
            if not database_url.startswith("sqlite")
            else None,
            echo=settings.DEBUG,
            # 连接超时配置
            connect_args={"server_settings": {"jit": "off"}}
            if "postgresql" in database_url
            else {},
        )
    return _async_engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖

    Yields:
        AsyncSession: SQLAlchemy异步数据库会话

    Raises:
        DatabaseError: 数据库连接失败时抛出
    """
    async_engine = get_async_engine()
    async with AsyncSession(async_engine) as session:
        try:
            # 测试连接
            await session.execute(text("SELECT 1"))
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def create_tables():
    """
    创建所有数据库表

    用于开发和测试环境的表创建
    生产环境应使用Alembic迁移
    """
    async_engine = get_async_engine()
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    删除所有数据库表

    仅用于测试环境
    """
    async_engine = get_async_engine()
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
