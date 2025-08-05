"""
API v1 路由聚合
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, health, users

api_router = APIRouter()

# 健康检查
api_router.include_router(health.router, prefix="/health", tags=["健康检查"])

# 认证相关
api_router.include_router(auth.router, prefix="/auth", tags=["用户认证"])

# 用户相关 - 修改为 /user 以符合需求 /api/v1/user/profile
api_router.include_router(users.router, prefix="/user", tags=["用户管理"])
