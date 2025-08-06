"""添加邮箱认证支持 - 扩展用户表支持邮箱密码登录

Revision ID: 004
Revises: 003
Create Date: 2025-08-04 10:00:00.000000

此迁移添加邮箱认证所需的字段，同时保持GitHub OAuth兼容性
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    添加邮箱认证支持字段

    新增字段：
    - password_hash: bcrypt哈希密码
    - email_verified: 邮箱验证状态
    - verification_token: 邮箱验证令牌
    - password_reset_token: 密码重置令牌
    - password_reset_expires: 密码重置令牌过期时间
    - auth_provider: 认证提供商类型

    同时将GitHub字段改为可选，支持多种认证方式
    """

    # 添加邮箱认证相关字段
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "email_verified",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "users",
        sa.Column("verification_token", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("password_reset_token", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("password_reset_expires", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "auth_provider",
            sa.String(length=50),
            nullable=False,
            server_default="email",
        ),
    )

    # 将GitHub字段改为可选，以支持邮箱认证用户
    op.alter_column("users", "github_user_id", existing_type=sa.BigInteger(), nullable=True)
    op.alter_column(
        "users",
        "github_username",
        existing_type=sa.String(length=255),
        nullable=True,
    )

    # 更新现有GitHub OAuth用户的auth_provider
    op.execute("UPDATE users SET auth_provider = 'github' WHERE github_user_id IS NOT NULL")
    op.execute("UPDATE users SET email_verified = true WHERE github_user_id IS NOT NULL")

    # 添加索引以提高查询性能
    op.create_index(
        op.f("ix_users_verification_token"),
        "users",
        ["verification_token"],
        unique=False,
    )
    op.create_index(
        op.f("ix_users_password_reset_token"),
        "users",
        ["password_reset_token"],
        unique=False,
    )
    op.create_index(
        op.f("ix_users_auth_provider"),
        "users",
        ["auth_provider"],
        unique=False,
    )


def downgrade() -> None:
    """
    回退邮箱认证支持

    警告：此操作将删除所有邮箱认证用户的数据
    """
    # 删除索引
    op.drop_index(op.f("ix_users_auth_provider"), table_name="users")
    op.drop_index(op.f("ix_users_password_reset_token"), table_name="users")
    op.drop_index(op.f("ix_users_verification_token"), table_name="users")

    # 删除邮箱认证相关字段
    op.drop_column("users", "auth_provider")
    op.drop_column("users", "password_reset_expires")
    op.drop_column("users", "password_reset_token")
    op.drop_column("users", "verification_token")
    op.drop_column("users", "email_verified")
    op.drop_column("users", "password_hash")

    # 恢复GitHub字段为必填
    op.alter_column(
        "users",
        "github_username",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.alter_column(
        "users",
        "github_user_id",
        existing_type=sa.BigInteger(),
        nullable=False,
    )
