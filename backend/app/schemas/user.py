"""
用户相关的 Pydantic 模式
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模式 - 集成Auth0"""
    auth0_user_id: str = Field(..., description="Auth0用户ID")
    email: EmailStr = Field(..., description="用户邮箱")
    username: Optional[str] = Field(None, description="用户名")
    timezone: str = Field(default="UTC", description="用户时区")
    is_active: bool = Field(default=True, description="是否激活")


class UserCreate(UserBase):
    """用户创建模式"""
    pass


class UserUpdate(BaseModel):
    """用户更新模式"""
    username: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    """返回给客户端的用户模式"""
    id: int
    
    class Config:
        from_attributes = True


class UserWithRecords(User):
    """包含记录的用户模式"""
    daily_records_count: int = Field(..., description="日记录总数")
    latest_record_date: Optional[str] = Field(None, description="最新记录日期")
    
    class Config:
        from_attributes = True