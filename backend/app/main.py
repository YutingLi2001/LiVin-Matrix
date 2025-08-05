"""
LiVin Matrix Backend API

生活数据相关性分析平台后端服务
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.middleware.error_handler import (
    APIVersionMiddleware,
    RequestIDMiddleware,
    setup_exception_handlers,
    setup_logging,
)
from app.schemas.responses import create_success_response


def create_application() -> FastAPI:
    """创建 FastAPI 应用实例"""

    # 配置日志
    setup_logging()

    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="生活数据相关性分析平台 API",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 添加中间件（按添加顺序执行）
    # 1. Session中间件（用于OAuth state管理）
    application.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

    # 2. 请求ID中间件
    application.add_middleware(RequestIDMiddleware)

    # 3. API版本中间件
    application.add_middleware(APIVersionMiddleware, version="v1")

    # 4. CORS中间件
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )

    # 设置全局异常处理器
    setup_exception_handlers(application)

    # 包含路由
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return create_success_response(
        data={
            "status": "healthy",
            "service": "livin-matrix-backend",
            "version": settings.VERSION,
        },
        message="Service is running normally",
    )
