"""
健康检查端点
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check():
    """系统健康检查"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "livin-matrix-backend",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
        }
    )


@router.get("/database")
async def database_health():
    """数据库健康检查"""
    # TODO: 实现数据库连接检查
    return JSONResponse(
        content={
            "status": "healthy",
            "component": "database",
            "message": "Database connection is healthy"
        }
    )


@router.get("/redis")
async def redis_health():
    """Redis 健康检查"""
    # TODO: 实现 Redis 连接检查
    return JSONResponse(
        content={
            "status": "healthy",
            "component": "redis",
            "message": "Redis connection is healthy"
        }
    )