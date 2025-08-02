"""
认证相关的Pydantic模型
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr


class GitHubCallbackRequest(BaseModel):
    """GitHub OAuth回调请求模型"""
    code: str = Field(..., description="GitHub OAuth授权码")
    state: Optional[str] = Field(None, description="CSRF状态参数")


class AuthResponse(BaseModel):
    """认证响应模型"""
    access_token: str = Field(..., description="JWT访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌过期时间（秒）")
    user: "UserProfile" = Field(..., description="用户信息")


class UserProfile(BaseModel):
    """用户资料模型"""
    id: int = Field(..., description="用户ID")
    github_user_id: int = Field(..., description="GitHub用户ID")
    github_username: str = Field(..., description="GitHub用户名")
    email: EmailStr = Field(..., description="用户邮箱")
    name: Optional[str] = Field(None, description="用户姓名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    location: Optional[str] = Field(None, description="用户位置")
    timezone: str = Field(default="UTC", description="用户时区")
    is_active: bool = Field(default=True, description="是否活跃")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class GitHubUserInfo(BaseModel):
    """GitHub用户信息模型"""
    github_user_id: int = Field(..., description="GitHub用户ID")
    github_username: str = Field(..., description="GitHub用户名")
    email: EmailStr = Field(..., description="用户邮箱")
    name: Optional[str] = Field(None, description="用户姓名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    location: Optional[str] = Field(None, description="用户位置")
    public_repos: int = Field(default=0, description="公开仓库数量")
    followers: int = Field(default=0, description="关注者数量")
    following: int = Field(default=0, description="关注数量")


class TokenRefreshRequest(BaseModel):
    """令牌刷新请求模型"""
    refresh_token: Optional[str] = Field(None, description="刷新令牌（可选）")


class LogoutRequest(BaseModel):
    """登出请求模型"""
    revoke_all: bool = Field(default=False, description="是否撤销所有令牌")


class AuthURLResponse(BaseModel):
    """认证URL响应模型"""
    auth_url: str = Field(..., description="GitHub OAuth授权URL")
    state: str = Field(..., description="CSRF状态参数")


class TokenInfo(BaseModel):
    """令牌信息模型"""
    user_id: int = Field(..., description="用户ID")
    github_user_id: int = Field(..., description="GitHub用户ID")
    jti: str = Field(..., description="JWT ID")
    exp: int = Field(..., description="过期时间戳")
    iat: int = Field(..., description="签发时间戳")
    type: str = Field(default="access", description="令牌类型")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str = Field(..., description="错误类型")
    error_description: str = Field(..., description="错误描述")
    error_code: Optional[int] = Field(None, description="错误代码")


# 更新前向引用
AuthResponse.model_rebuild()