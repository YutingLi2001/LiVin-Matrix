"""
应用配置模块
"""

import secrets
from typing import List, Optional

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings


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
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
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
            return [str(origin) for origin in self.BACKEND_CORS_ORIGINS]
        
        if self.ENVIRONMENT == "development":
            return [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",  # Vite默认端口
                "http://127.0.0.1:5173"   # Vite默认端口
            ]
        elif self.ENVIRONMENT == "production":
            return [
                "https://your-domain.github.io",
                "https://livin-matrix.com"
            ]
        else:
            return []
    
    # Auth0 配置
    AUTH0_DOMAIN: str = ""
    AUTH0_AUDIENCE: str = ""
    AUTH0_ALGORITHM: str = "RS256"
    
    # 环境配置
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()