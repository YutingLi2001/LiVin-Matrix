"""
JWT令牌黑名单模型
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .base import BaseModel


class TokenBlacklist(BaseModel):
    """
    JWT令牌黑名单模型 - 用于撤销JWT令牌
    """
    __tablename__ = "token_blacklist"
    
    # JWT令牌唯一标识符
    jti = Column(String(255), unique=True, nullable=False, index=True)
    
    # 用户ID关联
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 令牌过期时间
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # 关系映射
    user = relationship("User")
    
    def __repr__(self):
        return f"<TokenBlacklist(jti='{self.jti}', user_id={self.user_id}, expires_at='{self.expires_at}')>"
    
    def is_expired(self) -> bool:
        """检查令牌是否已过期"""
        from datetime import timezone
        return datetime.now(timezone.utc) > self.expires_at