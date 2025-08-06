"""
GitHub OAuth认证相关API端点
"""

from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    AuthURLResponse,
    ChangePasswordRequest,
    EmailLoginRequest,
    EmailRegisterRequest,
    EmailVerificationRequest,
    ErrorResponse,
    ForgotPasswordRequest,
    GitHubCallbackRequest,
    LogoutRequest,
    ResetPasswordRequest,
    SuccessResponse,
    TestEmailRequest,
    TokenRefreshRequest,
    UserProfile,
)
from app.services.github_service import GitHubOAuthService
from app.services.jwt_service import JWTService
from app.services.user_service import UserService

router = APIRouter()

# 实例化服务
github_service = GitHubOAuthService()
jwt_service = JWTService()


@router.get("/github/login", response_model=AuthURLResponse)
async def get_github_auth_url():
    """
    获取GitHub OAuth授权URL
    """
    try:
        # 生成GitHub OAuth授权URL
        auth_data = github_service.get_auth_url()

        # 不在后端存储state，由前端管理
        return AuthURLResponse(**auth_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成授权URL失败: {str(e)}",
        )


@router.post("/github/callback", response_model=AuthResponse)
async def github_oauth_callback(callback_data: GitHubCallbackRequest, db: AsyncSession = Depends(get_db)):
    """
    处理GitHub OAuth回调
    """
    try:
        # state参数验证由前端处理，后端只验证code的有效性

        # 交换code获取access_token
        access_token = await github_service.exchange_code_for_token(callback_data.code)

        # 获取GitHub用户信息
        github_user_info = await github_service.get_user_info(access_token)

        # 创建或更新用户
        user_service = UserService(db)
        try:
            user = await user_service.create_or_update_github_user(github_user_info)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"用户创建或更新失败: {str(e)}",
            )

        # 生成JWT令牌
        token_data = {
            "user_id": user.id,
            "github_user_id": user.github_user_id,
            "email": user.email,
            "github_username": user.github_username,
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
            auth_provider=user.auth_provider,
            email_verified=user.email_verified,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )

        return AuthResponse(
            access_token=jwt_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_profile,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth回调处理失败: {str(e)}",
        )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
            "github_username": current_user.github_username,
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
            auth_provider=current_user.auth_provider,
            email_verified=current_user.email_verified,
            created_at=current_user.created_at.isoformat(),
            updated_at=current_user.updated_at.isoformat(),
        )

        return AuthResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_profile,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"令牌刷新失败: {str(e)}",
        )


@router.post("/logout")
async def logout(
    logout_data: LogoutRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
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
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="令牌撤销失败")

        return {"message": "登出成功"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}",
        )


@router.get("/profile", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
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
            auth_provider=current_user.auth_provider,
            email_verified=current_user.email_verified,
            created_at=current_user.created_at.isoformat(),
            updated_at=current_user.updated_at.isoformat(),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户资料失败: {str(e)}",
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
        "token_expire_minutes": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    }


@router.get("/debug/config")
async def debug_config():
    """
    调试配置信息
    """
    return {
        "github_client_id": settings.GITHUB_CLIENT_ID,
        "github_redirect_uri": settings.GITHUB_REDIRECT_URI,
        "environment": settings.ENVIRONMENT,
    }


# ================== 邮箱认证相关端点 ==================


@router.post("/email/register", response_model=SuccessResponse)
async def email_register(register_data: EmailRegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    邮箱注册新用户
    """
    from app.services.email_auth_service import EmailAuthService
    from app.services.email_service import EmailService

    try:
        email_auth_service = EmailAuthService(db)
        email_service = EmailService()

        # 注册用户
        user = await email_auth_service.register_user(
            email=register_data.email,
            password=register_data.password,
            name=register_data.name,
        )

        # 发送验证邮件
        if user.verification_token:
            email_sent = await email_service.send_verification_email(
                to_email=user.email,
                verification_token=user.verification_token,
                user_name=user.name,
            )

            if not email_sent:
                # 邮件发送失败，但用户已创建，返回警告
                return SuccessResponse(
                    message="注册成功，但验证邮件发送失败，请稍后重试验证",
                    data={"user_id": user.id, "email_sent": False},
                )

        return SuccessResponse(
            message="注册成功！请检查邮箱并点击验证链接完成注册",
            data={"user_id": user.id, "email_sent": True},
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}",
        )


@router.post("/email/login", response_model=AuthResponse)
async def email_login(login_data: EmailLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    邮箱密码登录
    """
    from app.services.email_auth_service import EmailAuthService

    try:
        email_auth_service = EmailAuthService(db)

        # 验证用户登录
        user = await email_auth_service.authenticate_user(email=login_data.email, password=login_data.password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误，或邮箱未验证",
            )

        # 生成JWT令牌
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "auth_provider": user.auth_provider,
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
            auth_provider=user.auth_provider,
            email_verified=user.email_verified,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )

        return AuthResponse(
            access_token=jwt_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_profile,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}",
        )


@router.post("/email/verify", response_model=SuccessResponse)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    验证邮箱地址
    """
    from app.services.email_auth_service import EmailAuthService
    from app.services.email_service import EmailService

    try:
        email_auth_service = EmailAuthService(db)
        email_service = EmailService()

        # 验证邮箱
        success = await email_auth_service.verify_email(verification_data.token)

        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="验证令牌无效或已过期")

        # 获取已验证的用户发送欢迎邮件
        user = await email_auth_service.get_user_by_verification_token(verification_data.token)
        if user:
            # 发送欢迎邮件（不阻塞，失败也不影响验证结果）
            try:
                await email_service.send_welcome_email(user.email, user.name)
            except Exception:
                pass  # 忽略欢迎邮件发送失败

        return SuccessResponse(message="邮箱验证成功！现在可以正常登录了")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"邮箱验证失败: {str(e)}",
        )


@router.post("/email/forgot-password", response_model=SuccessResponse)
async def forgot_password(forgot_data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """
    申请密码重置
    """
    from app.services.email_auth_service import EmailAuthService
    from app.services.email_service import EmailService

    try:
        email_auth_service = EmailAuthService(db)
        email_service = EmailService()

        # 请求密码重置
        reset_token = await email_auth_service.request_password_reset(forgot_data.email)

        if not reset_token:
            # 为了安全，即使邮箱不存在也返回成功消息
            return SuccessResponse(message="如果该邮箱已注册，您将收到密码重置邮件")

        # 发送重置邮件
        user_service = UserService(db)
        user = await user_service.get_user_by_email(forgot_data.email)

        email_sent = await email_service.send_password_reset_email(
            to_email=forgot_data.email,
            reset_token=reset_token,
            user_name=user.name if user else None,
        )

        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="重置邮件发送失败，请稍后重试",
            )

        return SuccessResponse(message="密码重置邮件已发送，请检查您的邮箱")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密码重置申请失败: {str(e)}",
        )


@router.post("/email/reset-password", response_model=SuccessResponse)
async def reset_password(reset_data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """
    重置密码
    """
    from app.services.email_auth_service import EmailAuthService

    try:
        email_auth_service = EmailAuthService(db)

        # 重置密码
        success = await email_auth_service.reset_password(token=reset_data.token, new_password=reset_data.new_password)

        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="重置令牌无效或已过期")

        return SuccessResponse(message="密码重置成功！现在可以使用新密码登录")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密码重置失败: {str(e)}",
        )


@router.post("/email/change-password", response_model=SuccessResponse)
async def change_password(
    change_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    修改密码（需要登录）
    """
    from app.services.email_auth_service import EmailAuthService

    try:
        email_auth_service = EmailAuthService(db)

        # 修改密码
        success = await email_auth_service.change_password(
            user_id=current_user.id,
            current_password=change_data.current_password,
            new_password=change_data.new_password,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码错误或用户不支持密码认证",
            )

        return SuccessResponse(message="密码修改成功！")

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"密码修改失败: {str(e)}",
        )


@router.post("/email/test", response_model=SuccessResponse)
async def test_email(test_data: TestEmailRequest, db: AsyncSession = Depends(get_db)):
    """
    发送测试邮件
    """
    from app.services.email_service import EmailService

    try:
        email_service = EmailService()

        # 发送测试邮件
        email_sent = await email_service.send_test_email(test_data.email)

        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="测试邮件发送失败，请检查邮件服务配置",
            )

        return SuccessResponse(message="测试邮件发送成功！请检查收件箱")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"测试邮件发送失败: {str(e)}",
        )
