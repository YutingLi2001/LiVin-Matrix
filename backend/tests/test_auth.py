"""
认证相关测试
"""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest
from jose import jwt

from app.core.auth import JWTBearer
from app.core.config import settings
from app.services.auth_service import AuthService


class TestJWTBearer:
    """JWT Bearer认证测试 - 基于GitHub OAuth"""

    @pytest.fixture
    def auth_handler(self):
        return JWTBearer()

    @pytest.fixture
    def mock_jwks(self):
        return {
            "keys": [{"kid": "test-kid", "kty": "RSA", "use": "sig", "n": "test-n", "e": "AQAB"}]
        }

    @pytest.fixture
    def valid_token_payload(self):
        return {
            "sub": "auth0|123456789",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
            "nickname": "testuser",
            "aud": settings.AUTH0_AUDIENCE,
            "iss": f"https://{settings.AUTH0_DOMAIN}/",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }

    @pytest.fixture
    def mock_token(self, valid_token_payload):
        """创建模拟的JWT token"""
        return jwt.encode(
            valid_token_payload, "test-secret", algorithm="HS256"  # 在实际测试中会被RSA密钥替换  # 简化测试
        )

    @pytest.mark.asyncio
    async def test_get_jwks_success(self, auth_handler, mock_jwks):
        """测试成功获取JWKS"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = mock_jwks
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await auth_handler.get_jwks()
            assert result == mock_jwks

    def test_get_rsa_key_success(self, auth_handler, mock_jwks, mock_token):
        """测试成功获取RSA密钥"""
        with patch("jose.jwt.get_unverified_header") as mock_header:
            mock_header.return_value = {"kid": "test-kid"}

            result = auth_handler.get_rsa_key(mock_token, mock_jwks)

            expected_key = {
                "kty": "RSA",
                "kid": "test-kid",
                "use": "sig",
                "n": "test-n",
                "e": "AQAB",
            }
            assert result == expected_key

    def test_get_rsa_key_not_found(self, auth_handler, mock_jwks, mock_token):
        """测试密钥不存在的情况"""
        with patch("jose.jwt.get_unverified_header") as mock_header:
            mock_header.return_value = {"kid": "nonexistent-kid"}

            result = auth_handler.get_rsa_key(mock_token, mock_jwks)
            assert result is None


class TestAuthService:
    """认证服务测试"""

    @pytest.fixture
    def mock_db(self):
        return Mock()

    @pytest.fixture
    def auth_service(self, mock_db):
        with patch("app.services.auth_service.UserService"):
            return AuthService(mock_db)

    @pytest.fixture
    def user_info(self):
        return {
            "auth0_user_id": "auth0|123456789",
            "email": "test@example.com",
            "name": "Test User",
            "nickname": "testuser",
        }

    @pytest.mark.asyncio
    async def test_get_or_create_user_existing(self, auth_service, user_info):
        """测试获取已存在的用户"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.username = "Test User"

        auth_service.user_service.get_user_by_auth0_id = AsyncMock(return_value=mock_user)

        result = await auth_service.get_or_create_user(user_info)

        assert result == mock_user
        auth_service.user_service.get_user_by_auth0_id.assert_called_once_with("auth0|123456789")

    @pytest.mark.asyncio
    async def test_get_or_create_user_new(self, auth_service, user_info):
        """测试创建新用户"""
        mock_user = Mock()

        auth_service.user_service.get_user_by_auth0_id = AsyncMock(return_value=None)
        auth_service.user_service.create_user = AsyncMock(return_value=mock_user)

        result = await auth_service.get_or_create_user(user_info)

        assert result == mock_user
        auth_service.user_service.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_or_create_user_missing_info(self, auth_service):
        """测试缺少必要信息的情况"""
        incomplete_user_info = {
            "auth0_user_id": "auth0|123456789"
            # 缺少email
        }

        with pytest.raises(ValueError, match="缺少必要的用户信息"):
            await auth_service.get_or_create_user(incomplete_user_info)

    @pytest.mark.asyncio
    async def test_update_user_if_needed_no_update(self, auth_service, user_info):
        """测试用户信息无需更新"""
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.username = "Test User"

        result = await auth_service._update_user_if_needed(mock_user, user_info)

        assert result == mock_user
        # 确保没有调用数据库操作
        auth_service.db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_user_if_needed_with_update(self, auth_service, user_info):
        """测试用户信息需要更新"""
        mock_user = Mock()
        mock_user.email = "old@example.com"  # 旧邮箱
        mock_user.username = "Old Name"  # 旧用户名

        auth_service.db.commit = AsyncMock()
        auth_service.db.refresh = AsyncMock()

        result = await auth_service._update_user_if_needed(mock_user, user_info)

        assert result == mock_user
        assert mock_user.email == "test@example.com"
        assert mock_user.username == "Test User"

        # 确保调用了数据库操作
        auth_service.db.add.assert_called_once_with(mock_user)
        auth_service.db.commit.assert_called_once()
        auth_service.db.refresh.assert_called_once_with(mock_user)
