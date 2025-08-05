-- LiVin Matrix 数据库初始化脚本
-- 仅负责扩展和基础配置，表结构由Alembic管理

-- 创建必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 可选：创建开发环境专用数据库用户
-- 生产环境应通过其他方式管理用户权限
DO $$ 
BEGIN
    -- 检查是否在开发环境（通过数据库名称判断）
    IF current_database() LIKE '%_dev' THEN
        -- 创建只读用户（可选）
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'livin_readonly') THEN
            CREATE ROLE livin_readonly WITH LOGIN PASSWORD 'your_readonly_password_here';
        END IF;
    END IF;
END $$;

-- 注意：表结构现在完全由Alembic迁移管理
-- 请确保在后端服务启动时运行: python -m alembic upgrade head