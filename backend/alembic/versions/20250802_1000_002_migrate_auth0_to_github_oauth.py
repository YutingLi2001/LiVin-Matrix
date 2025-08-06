"""迁移Auth0认证到GitHub OAuth认证

Revision ID: 002
Revises: 001
Create Date: 2025-08-02 10:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    执行数据库升级操作 - 从Auth0迁移到GitHub OAuth
    """
    # 创建token_blacklist表
    op.create_table(
        "token_blacklist",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("jti", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_token_blacklist_expires_at"),
        "token_blacklist",
        ["expires_at"],
        unique=False,
    )
    op.create_index(op.f("ix_token_blacklist_id"), "token_blacklist", ["id"], unique=False)
    op.create_index(op.f("ix_token_blacklist_jti"), "token_blacklist", ["jti"], unique=True)
    op.create_index(
        op.f("ix_token_blacklist_user_id"),
        "token_blacklist",
        ["user_id"],
        unique=False,
    )

    # 添加GitHub OAuth相关字段到users表
    op.add_column("users", sa.Column("github_user_id", sa.BigInteger(), nullable=True))
    op.add_column(
        "users",
        sa.Column("github_username", sa.String(length=255), nullable=True),
    )
    op.add_column("users", sa.Column("name", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("location", sa.String(length=255), nullable=True))

    # 创建GitHub相关字段的索引
    op.create_index(
        op.f("ix_users_github_user_id"),
        "users",
        ["github_user_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_users_github_username"),
        "users",
        ["github_username"],
        unique=False,
    )

    # 注意：在实际部署中，需要先清空users表或迁移现有数据
    # 然后设置github_user_id和github_username为NOT NULL
    # 这里先设置为nullable=True以避免迁移失败


def downgrade() -> None:
    """
    执行数据库降级操作 - 从GitHub OAuth回退到Auth0
    """
    # 删除GitHub相关字段的索引
    op.drop_index(op.f("ix_users_github_username"), table_name="users")
    op.drop_index(op.f("ix_users_github_user_id"), table_name="users")

    # 删除GitHub OAuth相关字段
    op.drop_column("users", "location")
    op.drop_column("users", "bio")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "name")
    op.drop_column("users", "github_username")
    op.drop_column("users", "github_user_id")

    # 删除token_blacklist表
    op.drop_index(op.f("ix_token_blacklist_user_id"), table_name="token_blacklist")
    op.drop_index(op.f("ix_token_blacklist_jti"), table_name="token_blacklist")
    op.drop_index(op.f("ix_token_blacklist_id"), table_name="token_blacklist")
    op.drop_index(op.f("ix_token_blacklist_expires_at"), table_name="token_blacklist")
    op.drop_table("token_blacklist")
