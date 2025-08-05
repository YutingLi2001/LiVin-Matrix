"""
认证相关的Pydantic模型
"""
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field


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
    github_user_id: Optional[int] = Field(None, description="GitHub用户ID")
    github_username: Optional[str] = Field(None, description="GitHub用户名")
    email: EmailStr = Field(..., description="用户邮箱")
    name: Optional[str] = Field(None, description="用户姓名")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    bio: Optional[str] = Field(None, description="个人简介")
    location: Optional[str] = Field(None, description="用户位置")
    timezone: str = Field(default="UTC", description="用户时区")
    is_active: bool = Field(default=True, description="是否活跃")
    auth_provider: str = Field(..., description="认证提供商")
    email_verified: bool = Field(default=False, description="邮箱是否已验证")
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


# 邮箱认证相关模型
class EmailRegisterRequest(BaseModel):
    """邮箱注册请求模型"""

    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=8, description="用户密码")
    name: Optional[str] = Field(None, description="用户姓名")


class EmailLoginRequest(BaseModel):
    """邮箱登录请求模型"""

    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., description="用户密码")


class EmailVerificationRequest(BaseModel):
    """邮箱验证请求模型"""

    token: str = Field(..., description="验证令牌")


class ForgotPasswordRequest(BaseModel):
    """忘记密码请求模型"""

    email: EmailStr = Field(..., description="用户邮箱")


class ResetPasswordRequest(BaseModel):
    """重置密码请求模型"""

    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, description="新密码")


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""

    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, description="新密码")


class TestEmailRequest(BaseModel):
    """测试邮件请求模型"""

    email: EmailStr = Field(..., description="收件人邮箱")


class SuccessResponse(BaseModel):
    """成功响应模型"""

    message: str = Field(..., description="成功消息")
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    error: str = Field(..., description="错误类型")
    error_description: str = Field(..., description="错误描述")
    error_code: Optional[int] = Field(None, description="错误代码")


# 更新前向引用
AuthResponse.model_rebuild()
