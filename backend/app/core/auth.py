"""
Auth0 JWT验证中间件
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.security import get_auth0_well_known_url, get_auth0_issuer

security = HTTPBearer()


class Auth0JWTBearer:
    """Auth0 JWT Bearer认证"""

    def __init__(self):
        self.jwks_client = None
        self.jwks_cache = {}
        self.jwks_cache_time = None

    async def get_jwks(self) -> Dict[str, Any]:
        """获取Auth0的JWKS（JSON Web Key Set）"""
        # 缓存JWKS 1小时
        now = datetime.now(timezone.utc)
        if (
            self.jwks_cache_time
            and (now - self.jwks_cache_time).total_seconds() < 3600
            and self.jwks_cache
        ):
            return self.jwks_cache

        try:
            jwks_url = get_auth0_well_known_url(settings.AUTH0_DOMAIN)
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url)
                response.raise_for_status()
                jwks = response.json()

            self.jwks_cache = jwks
            self.jwks_cache_time = now
            return jwks

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"无法获取Auth0公钥: {str(e)}"
            )

    def get_rsa_key(self, token: str, jwks: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """从JWKS中获取用于验证token的RSA公钥"""
        try:
            unverified_header = jwt.get_unverified_header(token)
        except JWTError:
            return None

        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break
        return rsa_key if rsa_key else None

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """验证JWT token并返回payload"""
        try:
            # 获取JWKS
            jwks = await self.get_jwks()

            # 获取用于验证的RSA公钥
            rsa_key = self.get_rsa_key(token, jwks)
            if not rsa_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的token：找不到匹配的公钥"
                )

            # 验证token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[settings.AUTH0_ALGORITHM],
                audience=settings.AUTH0_AUDIENCE,
                issuer=get_auth0_issuer(settings.AUTH0_DOMAIN),
                options={"verify_exp": True},
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token已过期")
        except jwt.JWTClaimsError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token声明无效（audience或issuer不匹配）"
            )
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token验证失败: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"认证服务错误: {str(e)}"
            )

    async def __call__(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """FastAPI依赖注入方法"""
        token = credentials.credentials
        return await self.verify_token(token)


# 创建全局认证实例
auth_handler = Auth0JWTBearer()


async def get_current_user(token_payload: Dict[str, Any] = Depends(auth_handler)) -> Dict[str, Any]:
    """获取当前用户信息（从token中提取）"""
    try:
        user_info = {
            "auth0_user_id": token_payload.get("sub"),
            "email": token_payload.get("email"),
            "email_verified": token_payload.get("email_verified", False),
            "name": token_payload.get("name"),
            "nickname": token_payload.get("nickname"),
            "picture": token_payload.get("picture"),
            "updated_at": token_payload.get("updated_at"),
        }

        # 确保至少有用户ID
        if not user_info["auth0_user_id"]:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token中缺少用户ID")

        return user_info

    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token中缺少必要信息: {str(e)}"
        )
