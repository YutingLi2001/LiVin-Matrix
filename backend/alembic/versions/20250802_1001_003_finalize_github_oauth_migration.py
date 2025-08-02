"""完成GitHub OAuth迁移 - 清理Auth0字段并设置约束

Revision ID: 003
Revises: 002
Create Date: 2025-08-02 10:01:00.000000

注意：此迁移应在所有用户数据已迁移到GitHub OAuth后执行
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    完成GitHub OAuth迁移 - 清理Auth0字段并设置约束
    
    警告：执行此迁移前请确保：
    1. 所有用户数据已从Auth0迁移到GitHub OAuth
    2. github_user_id和github_username字段已填充有效数据
    3. 已备份现有数据
    """
    
    # 删除Auth0相关字段和索引
    op.drop_index(op.f('ix_users_auth0_user_id'), table_name='users')
    op.drop_column('users', 'auth0_user_id')
    
    # 设置GitHub字段为NOT NULL（仅在数据已迁移后执行）
    # 注意：在实际环境中，可能需要分步骤执行以避免锁定
    op.alter_column('users', 'github_user_id', 
                   existing_type=sa.BigInteger(),
                   nullable=False)
    op.alter_column('users', 'github_username',
                   existing_type=sa.String(length=255),
                   nullable=False)


def downgrade() -> None:
    """
    回退GitHub OAuth迁移
    
    警告：此操作将丢失GitHub OAuth数据
    """
    # 恢复GitHub字段为nullable
    op.alter_column('users', 'github_username',
                   existing_type=sa.String(length=255),
                   nullable=True)
    op.alter_column('users', 'github_user_id', 
                   existing_type=sa.BigInteger(),
                   nullable=True)
    
    # 恢复Auth0字段
    op.add_column('users', sa.Column('auth0_user_id', sa.String(length=255), nullable=False))
    op.create_index(op.f('ix_users_auth0_user_id'), 'users', ['auth0_user_id'], unique=True)