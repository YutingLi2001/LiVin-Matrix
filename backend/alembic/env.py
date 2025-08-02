"""
Alembic 环境配置
"""

import asyncio
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# 添加应用程序路径到 sys.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 导入应用程序配置和模型
from app.core.config import settings
from app.core.database import Base
from app.models import User, UserDailyRecord, WorkoutSession

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_database_url():
    """
    获取数据库连接URL，优先使用环境变量
    """
    return settings.DATABASE_URL or config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 支持数据库方言特性
        render_as_batch=True,
        # 版本控制表名
        version_table="alembic_version",
        # 支持事务性DDL
        transaction_per_migration=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """
    执行迁移的实际函数
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # 支持数据库方言特性
        render_as_batch=True,
        # 版本控制表名
        version_table="alembic_version",
        # 支持事务性DDL
        transaction_per_migration=True,
        # 比较类型
        compare_type=True,
        # 比较服务器默认值
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """
    在异步模式下运行迁移
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = AsyncEngine(
        engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # 检查是否在异步模式下运行
    try:
        # 尝试异步模式
        asyncio.run(run_async_migrations())
    except Exception:
        # 回退到同步模式
        configuration = config.get_section(config.config_ini_section)
        configuration["sqlalchemy.url"] = get_database_url()
        
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()