"""
认证相关API端点
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import User as UserResponse

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_current_user_profile(
    current_user_info: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前用户档案
    需要认证
    """
    try:
        auth_service = AuthService(db)

        # 获取或创建用户（处理首次登录）
        user = await auth_service.get_or_create_user(current_user_info)

        return UserResponse.model_validate(user)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"获取用户档案失败: {str(e)}"
        )


@router.post("/sync", response_model=UserResponse)
async def sync_user_profile(
    current_user_info: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    同步用户档案信息
    需要认证
    """
    try:
        auth_service = AuthService(db)
        auth0_user_id = current_user_info.get("auth0_user_id")

        if not auth0_user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="缺少用户ID")

        # 同步用户信息
        user = await auth_service.sync_user_profile(auth0_user_id, current_user_info)

        return UserResponse.model_validate(user)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"同步用户档案失败: {str(e)}"
        )
