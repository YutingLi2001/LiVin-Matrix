"""
用户相关模型
"""

from sqlalchemy import Column, String, Boolean, BigInteger, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """
    用户模型 - 集成GitHub OAuth认证
    """
    __tablename__ = "users"
    
    # GitHub OAuth集成字段
    github_user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    github_username = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    
    # 用户配置
    timezone = Column(String(50), default="UTC", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 关系映射
    daily_records = relationship("UserDailyRecord", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', github_id='{self.github_user_id}')>"