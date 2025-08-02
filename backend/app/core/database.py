"""
数据库连接配置模块
"""

from typing import Optional, Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from .config import settings

# 创建基础模型类
Base = declarative_base()

# 全局引擎和会话工厂变量
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine() -> Engine:
    """获取或创建数据库引擎"""
    global _engine
    if _engine is None:
        if not settings.DATABASE_URL:
            # 为测试环境提供默认的SQLite内存数据库
            database_url = "sqlite:///:memory:"
        else:
            database_url = settings.DATABASE_URL
            
        _engine = create_engine(
            database_url,
            poolclass=QueuePool if not database_url.startswith("sqlite") else None,
            pool_size=settings.DB_POOL_SIZE if not database_url.startswith("sqlite") else None,
            max_overflow=settings.DB_MAX_OVERFLOW if not database_url.startswith("sqlite") else None,
            pool_recycle=settings.DB_POOL_RECYCLE if not database_url.startswith("sqlite") else None,
            pool_pre_ping=settings.DB_POOL_PRE_PING if not database_url.startswith("sqlite") else None,
            echo=settings.DEBUG,
            # 安全配置
            isolation_level="READ_COMMITTED" if not database_url.startswith("sqlite") else None,
            # 连接超时配置
            connect_args={"connect_timeout": 10} if "postgresql" in database_url else {},
        )
    return _engine


def get_session_local() -> sessionmaker:
    """获取会话工厂"""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    """
    获取数据库会话依赖
    
    Yields:
        Session: SQLAlchemy数据库会话
        
    Raises:
        DatabaseError: 数据库连接失败时抛出
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        # 测试连接
        db.execute("SELECT 1")
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def create_tables():
    """
    创建所有数据库表
    
    用于开发和测试环境的表创建
    生产环境应使用Alembic迁移
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    删除所有数据库表
    
    仅用于测试环境
    """
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)