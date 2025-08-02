"""
用户相关模型
"""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """
    用户模型 - 集成Auth0认证
    """
    __tablename__ = "users"
    
    # Auth0集成字段
    auth0_user_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=True, index=True)
    
    # 用户配置
    timezone = Column(String(50), default="UTC", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # 关系映射
    daily_records = relationship("UserDailyRecord", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', auth0_id='{self.auth0_user_id}')>"