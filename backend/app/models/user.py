"""
用户相关模型
"""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """
    用户模型 - 支持GitHub OAuth和邮箱认证
    """

    __tablename__ = "users"

    # 基础用户信息
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)

    # GitHub OAuth集成字段 (现在为可选)
    github_user_id = Column(BigInteger, unique=True, nullable=True, index=True)
    github_username = Column(String(255), nullable=True, index=True)

    # 邮箱认证字段
    password_hash = Column(String(255), nullable=True)  # bcrypt哈希密码
    email_verified = Column(Boolean, default=False, nullable=False)  # 邮箱是否已验证
    verification_token = Column(String(255), nullable=True)  # 邮箱验证令牌
    password_reset_token = Column(String(255), nullable=True)  # 密码重置令牌
    password_reset_expires = Column(DateTime, nullable=True)  # 密码重置令牌过期时间
    auth_provider = Column(String(50), default="email", nullable=False)  # 认证提供商: 'github' | 'email'

    # 用户配置
    timezone = Column(String(50), default="UTC", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # 关系映射
    daily_records = relationship("UserDailyRecord", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', github_id='{self.github_user_id}')>"
