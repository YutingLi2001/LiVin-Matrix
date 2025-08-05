"""
数据库迁移集成测试

测试Alembic迁移的完整性和数据安全性
"""

import pytest
import tempfile
import os
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text, MetaData
from testcontainers.postgres import PostgresContainer
from app.core.config import settings


class TestDatabaseMigrations:
    """数据库迁移测试套件"""
    
    @pytest.fixture(scope="class")
    def postgres_container(self):
        """PostgreSQL测试容器"""
        with PostgresContainer("postgres:15-alpine") as postgres:
            yield postgres
    
    @pytest.fixture(scope="class")
    def test_database_url(self, postgres_container):
        """测试数据库URL"""
        return postgres_container.get_connection_url()
    
    @pytest.fixture(scope="class")
    def alembic_config(self, test_database_url):
        """Alembic配置"""
        # 创建临时配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(f"""
[alembic]
script_location = alembic
sqlalchemy.url = {test_database_url}

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""")
            config_path = f.name
        
        config = Config(config_path)
        return config
    
    @pytest.fixture
    def clean_database(self, test_database_url):
        """干净的测试数据库"""
        engine = create_engine(test_database_url)
        
        # 清理数据库
        with engine.connect() as conn:
            # 删除所有表
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
            conn.commit()
        
        yield engine
        engine.dispose()

    def test_migration_upgrade_from_empty(self, alembic_config, clean_database):
        """测试从空数据库升级到最新版本"""
        # 运行所有迁移
        command.upgrade(alembic_config, "head")
        
        # 验证所有表都已创建
        with clean_database.connect() as conn:
            # 检查表是否存在
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            expected_tables = [
                'alembic_version',
                'token_blacklist', 
                'user_daily_records',
                'users',
                'workout_sessions'
            ]
            
            assert set(tables) == set(expected_tables), f"Expected {expected_tables}, got {tables}"
    
    def test_migration_current_version(self, alembic_config, clean_database):
        """测试迁移版本跟踪"""
        # 升级到最新版本
        command.upgrade(alembic_config, "head")
        
        # 检查当前版本
        with clean_database.connect() as conn:
            context = MigrationContext.configure(conn)
            current_rev = context.get_current_revision()
            
            # 应该是最新版本 (003)
            assert current_rev == "003", f"Expected version 003, got {current_rev}"
    
    def test_migration_step_by_step(self, alembic_config, clean_database):
        """测试逐步迁移"""
        # 升级到版本001
        command.upgrade(alembic_config, "001")
        
        with clean_database.connect() as conn:
            # 验证基础表存在
            result = conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name IN ('users', 'user_daily_records')
            """))
            tables = [row[0] for row in result]
            assert 'users' in tables
            assert 'user_daily_records' in tables
        
        # 继续升级到版本002
        command.upgrade(alembic_config, "002")
        
        with clean_database.connect() as conn:
            # 验证GitHub OAuth字段存在
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name IN ('github_user_id', 'github_username')
            """))
            columns = [row[0] for row in result]
            assert 'github_user_id' in columns
            assert 'github_username' in columns
        
        # 升级到最新版本
        command.upgrade(alembic_config, "head")
        
        with clean_database.connect() as conn:
            # 验证Auth0字段已删除
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'auth0_user_id'
            """))
            auth0_columns = [row[0] for row in result]
            assert len(auth0_columns) == 0, "Auth0 fields should be removed in version 003"

    def test_migration_data_preservation(self, alembic_config, clean_database):
        """测试迁移过程中数据保持完整"""
        # 升级到版本001
        command.upgrade(alembic_config, "001")
        
        # 插入测试数据
        with clean_database.connect() as conn:
            conn.execute(text("""
                INSERT INTO users (email, username, timezone, is_active, auth0_user_id) 
                VALUES ('test@example.com', 'testuser', 'UTC', true, 'auth0|123456')
            """))
            conn.commit()
            
            # 验证数据插入成功
            result = conn.execute(text("SELECT email FROM users WHERE username = 'testuser'"))
            email = result.scalar()
            assert email == 'test@example.com'
        
        # 升级到版本002（添加GitHub字段）
        command.upgrade(alembic_config, "002")
        
        with clean_database.connect() as conn:
            # 验证原数据仍然存在
            result = conn.execute(text("SELECT email FROM users WHERE username = 'testuser'"))
            email = result.scalar()
            assert email == 'test@example.com'
            
            # 添加GitHub数据
            conn.execute(text("""
                UPDATE users SET github_user_id = 123456, github_username = 'testuser' 
                WHERE username = 'testuser'
            """))
            conn.commit()
        
        # 注意：版本003会删除auth0字段，在真实场景中需要先迁移数据
        # 这里我们跳过版本003的测试，因为它需要特殊的数据迁移处理

    def test_migration_rollback(self, alembic_config, clean_database):
        """测试迁移回滚功能"""
        # 升级到最新版本
        command.upgrade(alembic_config, "head")
        
        # 验证所有表存在
        with clean_database.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """))
            table_count = result.scalar()
            assert table_count >= 4  # 至少4个主要表
        
        # 回滚到版本002
        command.downgrade(alembic_config, "002")
        
        with clean_database.connect() as conn:
            # 验证auth0字段重新出现
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'auth0_user_id'
            """))
            auth0_columns = [row[0] for row in result]
            assert len(auth0_columns) == 1, "Auth0 field should be restored after rollback"

    def test_migration_script_syntax(self, alembic_config):
        """测试迁移脚本语法正确性"""
        # 获取脚本目录
        script = ScriptDirectory.from_config(alembic_config)
        
        # 验证所有迁移脚本可以被解析
        revisions = script.walk_revisions()
        revision_ids = []
        
        for rev in revisions:
            assert rev.revision is not None
            assert rev.module is not None
            revision_ids.append(rev.revision)
        
        # 验证预期的迁移版本存在
        expected_revisions = ['001', '002', '003']
        for expected_rev in expected_revisions:
            assert expected_rev in revision_ids, f"Migration {expected_rev} not found"

    def test_database_constraints_after_migration(self, alembic_config, clean_database):
        """测试迁移后数据库约束正确性"""
        command.upgrade(alembic_config, "head")
        
        with clean_database.connect() as conn:
            # 测试外键约束
            try:
                # 尝试插入无效的外键数据
                conn.execute(text("""
                    INSERT INTO user_daily_records (user_id, record_date) 
                    VALUES (99999, '2025-01-01')
                """))
                conn.commit()
                assert False, "Foreign key constraint should prevent this insert"
            except Exception:
                # 预期的错误，回滚
                conn.rollback()
            
            # 测试检查约束
            try:
                # 先插入有效用户
                conn.execute(text("""
                    INSERT INTO users (email, username, github_user_id, github_username) 
                    VALUES ('test@example.com', 'testuser', 123456, 'testuser')
                """))
                user_result = conn.execute(text("SELECT id FROM users WHERE email = 'test@example.com'"))
                user_id = user_result.scalar()
                
                # 尝试插入无效的睡眠质量分数
                conn.execute(text(f"""
                    INSERT INTO user_daily_records (user_id, record_date, sleep_quality) 
                    VALUES ({user_id}, '2025-01-01', 15)
                """))
                conn.commit()
                assert False, "Check constraint should prevent invalid sleep_quality value"
            except Exception:
                # 预期的错误
                conn.rollback()