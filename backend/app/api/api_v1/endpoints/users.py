"""
用户管理端点
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.schemas.user import User as UserResponse, UserUpdate
from app.schemas.responses import create_success_response, create_error_response, ErrorCodes

router = APIRouter()


@router.get("/profile")
async def get_user_profile(
    current_user_info: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    获取当前用户档案
    
    **需要认证**
    
    返回格式:
    ```json
    {
        "success": true,
        "data": {
            "id": 1,
            "auth0_user_id": "auth0|123456",
            "email": "user@example.com",
            "username": "user123",
            "timezone": "UTC",
            "is_active": true
        },
        "message": "用户档案获取成功"
    }
    ```
    """
    try:
        auth_service = AuthService(db)
        auth0_user_id = current_user_info.get("auth0_user_id")

        if not auth0_user_id:
            return create_error_response(
                message="缺少用户ID",
                error_code=ErrorCodes.BAD_REQUEST
            )

        user = auth_service.get_user_by_auth0_id(auth0_user_id)
        if not user:
            return create_error_response(
                message="用户不存在",
                error_code=ErrorCodes.NOT_FOUND
            )

        user_data = UserResponse.model_validate(user).model_dump()
        return create_success_response(
            data=user_data,
            message="用户档案获取成功"
        )

    except Exception as e:
        return create_error_response(
            message="获取用户档案失败",
            error_code=ErrorCodes.INTERNAL_ERROR,
            details={"error": str(e)}
        )


@router.put("/profile")
async def update_user_profile(
    user_update: UserUpdate,
    current_user_info: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    更新当前用户档案
    
    **需要认证**
    
    请求体:
    ```json
    {
        "username": "new_username",
        "timezone": "Asia/Shanghai"
    }
    ```
    
    返回格式:
    ```json
    {
        "success": true,
        "data": {
            "id": 1,
            "auth0_user_id": "auth0|123456",
            "email": "user@example.com",
            "username": "new_username",
            "timezone": "Asia/Shanghai",
            "is_active": true
        },
        "message": "用户档案更新成功"
    }
    ```
    """
    try:
        user_service = UserService(db)
        auth0_user_id = current_user_info.get("auth0_user_id")

        if not auth0_user_id:
            return create_error_response(
                message="缺少用户ID",
                error_code=ErrorCodes.BAD_REQUEST
            )

        # 获取当前用户
        current_user = user_service.get_user_by_auth0_id(auth0_user_id)
        if not current_user:
            return create_error_response(
                message="用户不存在",
                error_code=ErrorCodes.NOT_FOUND
            )

        # 更新用户信息
        updated_user = user_service.update_user(current_user.id, user_update)
        
        user_data = UserResponse.model_validate(updated_user).model_dump()
        return create_success_response(
            data=user_data,
            message="用户档案更新成功"
        )

    except ValueError as e:
        return create_error_response(
            message=str(e),
            error_code=ErrorCodes.VALIDATION_ERROR
        )
    except Exception as e:
        return create_error_response(
            message="用户档案更新失败",
            error_code=ErrorCodes.INTERNAL_ERROR,
            details={"error": str(e)}
        )


@router.get("/")
async def get_users(current_user_info: Dict[str, Any] = Depends(get_current_user)):
    """
    获取用户列表（需要认证）
    
    **注意**: 此端点仅为演示，实际应用中应限制管理员访问
    """
    return create_success_response(
        data={
            "users": [],
            "total": 0,
            "current_user": current_user_info.get("email"),
        },
        message="用户列表端点 - 待实现"
    )


@router.get("/{user_id}")
async def get_user(user_id: int, current_user_info: Dict[str, Any] = Depends(get_current_user)):
    """
    获取用户详情（需要认证）
    
    **注意**: 此端点仅为演示，实际应用中应限制本人或管理员访问
    """
    return create_success_response(
        data={
            "user_id": user_id,
            "current_user": current_user_info.get("email"),
        },
        message="用户详情端点 - 待实现"
    )
