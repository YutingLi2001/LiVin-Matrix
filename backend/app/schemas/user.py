"""
用户相关的 Pydantic 模式
"""

from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """用户基础模式"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """用户创建模式"""
    password: str


class UserUpdate(BaseModel):
    """用户更新模式"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserInDB(UserBase):
    """数据库中的用户模式"""
    id: int
    hashed_password: str
    
    class Config:
        from_attributes = True


class User(UserBase):
    """返回给客户端的用户模式"""
    id: int
    
    class Config:
        from_attributes = True