# 数据库

## 技术栈

- **PostgreSQL** - 主数据库
- **SQLAlchemy** - ORM 框架
- **Alembic** - 数据库迁移工具

## 目录结构

```
database/
├── migrations/    # 数据库迁移文件
├── scripts/      # 数据库初始化脚本
└── seed/         # 测试数据
```

## 数据库连接

开发环境配置：
- 主机: localhost
- 端口: 5432
- 数据库: livin_matrix_dev
- 用户名: postgres
- 密码: 在环境变量中配置

## 迁移命令

```bash
# 生成迁移文件
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 环境要求

- PostgreSQL 14+
- Python 3.9+ (用于迁移工具)
