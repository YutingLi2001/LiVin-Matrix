"""
GitHub OAuth认证相关API端点
"""
from typing import Dict, Any
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.config import settings
from app.services.github_service import GitHubOAuthService
from app.services.jwt_service import JWTService
from app.services.user_service import UserService
from app.schemas.auth import (
    AuthURLResponse, 
    GitHubCallbackRequest, 
    AuthResponse, 
    UserProfile,
    TokenRefreshRequest,
    LogoutRequest,
    ErrorResponse
)
from app.models.user import User

router = APIRouter()

# 实例化服务
github_service = GitHubOAuthService()
jwt_service = JWTService()


@router.get("/github/login", response_model=AuthURLResponse)
async def get_github_auth_url(request: Request):
    """
    获取GitHub OAuth授权URL
    """
    try:
        # 生成GitHub OAuth授权URL
        auth_data = github_service.get_auth_url()
        
        # 将state存储在session中（生产环境中应使用Redis）
        request.session["oauth_state"] = auth_data["state"]
        
        return AuthURLResponse(**auth_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成授权URL失败: {str(e)}"
        )


@router.post("/github/callback", response_model=AuthResponse)
async def github_oauth_callback(
    callback_data: GitHubCallbackRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    处理GitHub OAuth回调
    """
    try:
        # 验证state参数（CSRF保护）
        stored_state = request.session.get("oauth_state")
        if not stored_state or stored_state != callback_data.state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的state参数"
            )
        
        # 清除session中的state
        request.session.pop("oauth_state", None)
        
        # 交换code获取access_token
        access_token = await github_service.exchange_code_for_token(callback_data.code)
        
        # 获取GitHub用户信息
        github_user_info = await github_service.get_user_info(access_token)
        
        # 创建或更新用户
        user_service = UserService(db)
        user = await user_service.create_or_update_github_user(github_user_info)
        
        # 生成JWT令牌
        token_data = {
            "user_id": user.id,
            "github_user_id": user.github_user_id,
            "email": user.email,
            "github_username": user.github_username
        }
        
        jwt_token = jwt_service.create_access_token(token_data)
        
        # 构建用户资料
        user_profile = UserProfile(
            id=user.id,
            github_user_id=user.github_user_id,
            github_username=user.github_username,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            bio=user.bio,
            location=user.location,
            timezone=user.timezone,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
        
        return AuthResponse(
            access_token=jwt_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_profile
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth回调处理失败: {str(e)}"
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    刷新JWT令牌
    """
    try:
        # 生成新的JWT令牌
        token_data = {
            "user_id": current_user.id,
            "github_user_id": current_user.github_user_id,
            "email": current_user.email,
            "github_username": current_user.github_username
        }
        
        new_token = jwt_service.create_access_token(token_data)
        
        # 构建用户资料
        user_profile = UserProfile(
            id=current_user.id,
            github_user_id=current_user.github_user_id,
            github_username=current_user.github_username,
            email=current_user.email,
            name=current_user.name,
            avatar_url=current_user.avatar_url,
            bio=current_user.bio,
            location=current_user.location,
            timezone=current_user.timezone,
            is_active=current_user.is_active,
            created_at=current_user.created_at.isoformat(),
            updated_at=current_user.updated_at.isoformat()
        )
        
        return AuthResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_profile
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"令牌刷新失败: {str(e)}"
        )


@router.post("/logout")
async def logout(
    logout_data: LogoutRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    用户登出，撤销JWT令牌
    """
    try:
        # 获取当前令牌
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            
            # 将令牌添加到黑名单
            success = await jwt_service.blacklist_token(token, db)
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="令牌撤销失败"
                )
        
        return {"message": "登出成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        )


@router.get("/profile", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户资料
    需要JWT认证
    """
    try:
        return UserProfile(
            id=current_user.id,
            github_user_id=current_user.github_user_id,
            github_username=current_user.github_username,
            email=current_user.email,
            name=current_user.name,
            avatar_url=current_user.avatar_url,
            bio=current_user.bio,
            location=current_user.location,
            timezone=current_user.timezone,
            is_active=current_user.is_active,
            created_at=current_user.created_at.isoformat(),
            updated_at=current_user.updated_at.isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户资料失败: {str(e)}"
        )


@router.get("/health")
async def auth_health_check():
    """
    认证服务健康检查
    """
    return {
        "status": "ok",
        "service": "GitHub OAuth Authentication",
        "version": "1.0.0",
        "jwt_algorithm": settings.JWT_ALGORITHM,
        "token_expire_minutes": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    }