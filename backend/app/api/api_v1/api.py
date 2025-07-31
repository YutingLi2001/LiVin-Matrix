"""
API v1 路由聚合
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import health, users

api_router = APIRouter()

# 健康检查
api_router.include_router(health.router, prefix="/health", tags=["健康检查"])

# 用户相关
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])