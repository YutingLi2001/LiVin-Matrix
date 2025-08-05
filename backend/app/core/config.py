"""
应用配置模块

支持Docker Secrets和环境变量的统一配置管理
"""

import logging
import secrets
from typing import List, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """应用设置"""

    # 基础配置
    PROJECT_NAME: str = "LiVin Matrix API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 安全配置
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 天

    # 数据库配置
    DATABASE_URL: Optional[str] = None

    # 数据库连接池配置
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379"

    # CORS 配置
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 默认CORS配置（基于环境）
    def get_cors_origins(self) -> List[str]:
        """根据环境返回CORS配置"""
        if self.BACKEND_CORS_ORIGINS:
            return self.BACKEND_CORS_ORIGINS

        if self.ENVIRONMENT == "development":
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",  # Vite默认端口
                "http://127.0.0.1:5173",  # Vite默认端口
            ]
        elif self.ENVIRONMENT == "production":
            return ["https://your-domain.github.io", "https://livin-matrix.com"]
        else:
            return []

    # GitHub OAuth 配置
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:3000/auth/callback"

    # 邮件服务配置 (Resend)
    RESEND_API_KEY: str = "re_Ax8gF7Ds_FjVx8o5bDfzUfVdeFmotCp1z"
    EMAIL_FROM_ADDRESS: str = "onboarding@resend.dev"
    EMAIL_FROM_NAME: str = "LiVin Matrix Team"
    FRONTEND_URL: str = "http://localhost:3000"

    # 密码安全配置
    PASSWORD_MIN_LENGTH: int = 8
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_EXPIRE_HOURS: int = 1

    # JWT 配置
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # 环境配置
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # 日志配置
    LOG_LEVEL: str = "INFO"

    class Config:
        case_sensitive = True


def create_settings() -> Settings:
    """
    创建配置实例，集成Docker Secrets支持

    Returns:
        配置实例
    """
    # 首先创建基础设置实例
    base_settings = Settings()

    try:
        # 延迟导入避免循环依赖
        from app.services.secrets_service import get_secret

        # 使用Docker Secrets覆盖敏感配置
        try:
            # GitHub OAuth密钥
            base_settings.GITHUB_CLIENT_SECRET = get_secret(
                "fastapi_github_oauth_client_secret",
                "GITHUB_CLIENT_SECRET",
                base_settings.GITHUB_CLIENT_SECRET,
            )

            # JWT签名密钥
            base_settings.JWT_SECRET_KEY = get_secret(
                "fastapi_jwt_signing_key", "JWT_SECRET_KEY", base_settings.JWT_SECRET_KEY
            )

            # FastAPI应用密钥
            base_settings.SECRET_KEY = get_secret(
                "fastapi_session_secret_key", "SECRET_KEY", base_settings.SECRET_KEY
            )

            # 邮件服务密钥
            base_settings.RESEND_API_KEY = get_secret(
                "resend_api_key", "RESEND_API_KEY", base_settings.RESEND_API_KEY
            )

            # 数据库密码（如果DATABASE_URL中包含密码占位符，需要替换）
            if base_settings.DATABASE_URL and "postgres@postgres:" in base_settings.DATABASE_URL:
                try:
                    postgres_password = get_secret(
                        "postgres_db_password", "POSTGRES_PASSWORD", "your_secure_password_here"
                    )
                    # 替换URL中的密码占位符
                    base_settings.DATABASE_URL = base_settings.DATABASE_URL.replace(
                        "postgres@postgres:", f"postgres:{postgres_password}@postgres:"
                    )
                    logger.info("Database URL updated with secret password")
                except Exception as e:
                    logger.warning(f"Failed to update database password from secret: {e}")

            logger.info("Successfully loaded configuration with Docker Secrets support")

        except Exception as e:
            logger.warning(f"Failed to load some secrets, using fallback values: {str(e)}")

    except ImportError:
        logger.info("Secrets service not available, using environment variables only")

    return base_settings


settings = create_settings()
