"""
JWT令牌服务
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.token_blacklist import TokenBlacklist


class JWTService:
    """JWT令牌管理服务"""

    def create_access_token(
        self, user_data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建JWT访问令牌

        Args:
            user_data: 用户数据字典，包含user_id等信息
            expires_delta: 过期时间增量，默认使用配置值

        Returns:
            JWT令牌字符串
        """
        to_encode = user_data.copy()

        # 设置过期时间
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )

        # 添加标准JWT声明
        jti = str(uuid.uuid4())  # JWT ID，用于令牌撤销
        to_encode.update(
            {"exp": expire, "iat": datetime.now(timezone.utc), "jti": jti, "type": "access"}
        )

        # 生成JWT令牌
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证JWT令牌并返回payload

        Args:
            token: JWT令牌字符串

        Returns:
            令牌payload字典

        Raises:
            JWTError: 当令牌验证失败时
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True},
            )
            return payload

        except jwt.ExpiredSignatureError:
            raise JWTError("Token已过期")
        except jwt.InvalidTokenError:
            raise JWTError("Token无效")
        except Exception as e:
            raise JWTError(f"Token验证失败: {str(e)}")

    async def blacklist_token(self, token: str, db: AsyncSession) -> bool:
        """
        将令牌添加到黑名单

        Args:
            token: JWT令牌字符串
            db: 数据库会话

        Returns:
            操作是否成功
        """
        try:
            # 验证令牌并提取信息
            payload = self.verify_token(token)

            jti = payload.get("jti")
            user_id = payload.get("user_id")
            exp = payload.get("exp")

            if not jti or not user_id or not exp:
                return False

            # 转换过期时间
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)

            # 检查令牌是否已在黑名单中
            existing = await db.execute(select(TokenBlacklist).where(TokenBlacklist.jti == jti))
            if existing.scalar_one_or_none():
                return True  # 已经在黑名单中

            # 添加到黑名单
            blacklist_entry = TokenBlacklist(jti=jti, user_id=user_id, expires_at=expires_at)

            db.add(blacklist_entry)
            await db.commit()

            return True

        except Exception:
            return False

    async def is_token_blacklisted(self, jti: str, db: AsyncSession) -> bool:
        """
        检查令牌是否在黑名单中

        Args:
            jti: JWT ID
            db: 数据库会话

        Returns:
            令牌是否被撤销
        """
        try:
            result = await db.execute(select(TokenBlacklist).where(TokenBlacklist.jti == jti))
            blacklisted_token = result.scalar_one_or_none()

            if not blacklisted_token:
                return False

            # 检查令牌是否已过期（过期的黑名单条目可以被清理）
            if blacklisted_token.is_expired():
                await db.delete(blacklisted_token)
                await db.commit()
                return False

            return True

        except Exception:
            return False

    async def cleanup_expired_tokens(self, db: AsyncSession) -> int:
        """
        清理过期的黑名单令牌

        Args:
            db: 数据库会话

        Returns:
            清理的令牌数量
        """
        try:
            now = datetime.now(timezone.utc)

            # 查找过期的令牌
            result = await db.execute(select(TokenBlacklist).where(TokenBlacklist.expires_at < now))
            expired_tokens = result.scalars().all()

            # 删除过期的令牌
            for token in expired_tokens:
                await db.delete(token)

            await db.commit()

            return len(expired_tokens)

        except Exception:
            return 0

    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """
        获取令牌信息（不验证过期时间）

        Args:
            token: JWT令牌字符串

        Returns:
            令牌信息字典或None
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": False},  # 不验证过期时间
            )
            return payload
        except Exception:
            return None
