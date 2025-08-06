"""
JWT认证中间件 - 基于GitHub OAuth
"""

from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.token_blacklist import TokenBlacklist
from app.models.user import User

security = HTTPBearer()


class JWTBearer:
    """JWT Bearer认证处理器"""

    async def verify_token(self, token: str, db: AsyncSession) -> Dict[str, Any]:
        """验证JWT token并返回payload"""
        try:
            # 解码JWT token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True},
            )

            # 检查必要字段
            user_id = payload.get("user_id")
            jti = payload.get("jti")

            if not user_id or not jti:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token格式无效：缺少必要字段"
                )

            # 检查token是否在黑名单中
            from sqlalchemy import select

            result = await db.execute(select(TokenBlacklist).where(TokenBlacklist.jti == jti))
            blacklisted_token = result.scalar_one_or_none()
            if blacklisted_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token已被撤销"
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token已过期")
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token验证失败: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"认证服务错误: {str(e)}"
            )

    async def __call__(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db),
    ) -> Dict[str, Any]:
        """FastAPI依赖注入方法"""
        token = credentials.credentials
        return await self.verify_token(token, db)


# 创建全局认证实例
auth_handler = JWTBearer()


async def get_current_user(
    token_payload: Dict[str, Any] = Depends(auth_handler), db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户信息"""
    try:
        user_id = token_payload.get("user_id")

        # 从数据库获取用户信息
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户账户已被禁用")

        return user

    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token中缺少必要信息: {str(e)}"
        )


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """获取当前用户信息（可选，用于需要支持匿名访问的端点）"""
    if not credentials:
        return None

    try:
        token_payload = await auth_handler.verify_token(credentials.credentials, db)
        return await get_current_user(token_payload, db)
    except HTTPException:
        return None
