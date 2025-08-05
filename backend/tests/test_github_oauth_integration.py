"""
GitHub OAuth + JWT认证系统集成测试
"""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.main import app
from app.models.user import User
from app.services.github_service import GitHubOAuthService
from app.services.jwt_service import JWTService


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    mock_session = Mock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def mock_github_user_info():
    """模拟GitHub用户信息"""
    return {
        "github_user_id": 12345678,
        "github_username": "testuser",
        "email": "test@example.com",
        "name": "Test User",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345678?v=4",
        "bio": "Test user biography",
        "location": "Test City",
        "public_repos": 10,
        "followers": 5,
        "following": 3,
    }


@pytest.fixture
def mock_user():
    """模拟用户对象"""
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.github_user_id = 12345678
    mock_user.github_username = "testuser"
    mock_user.email = "test@example.com"
    mock_user.name = "Test User"
    mock_user.avatar_url = "https://avatars.githubusercontent.com/u/12345678?v=4"
    mock_user.bio = "Test user biography"
    mock_user.location = "Test City"
    mock_user.timezone = "UTC"
    mock_user.is_active = True
    mock_user.created_at = "2025-01-01T00:00:00Z"
    mock_user.updated_at = "2025-01-01T00:00:00Z"
    return mock_user


class TestGitHubOAuthLogin:
    """测试GitHub OAuth登录流程"""

    def test_get_github_auth_url(self, client):
        """测试获取GitHub OAuth授权URL"""
        with patch.object(GitHubOAuthService, "get_auth_url") as mock_get_auth_url:
            mock_get_auth_url.return_value = {
                "auth_url": "https://github.com/login/oauth/authorize?client_id=test&state=test_state",
                "state": "test_state",
            }

            response = client.get("/api/v1/auth/github/login")

            assert response.status_code == 200
            data = response.json()
            assert "auth_url" in data
            assert "state" in data
            assert "github.com/login/oauth/authorize" in data["auth_url"]

    def test_github_oauth_callback_success(self, client, mock_db, mock_github_user_info, mock_user):
        """测试GitHub OAuth回调成功流程"""

        def mock_get_db():
            return mock_db

        app.dependency_overrides[get_db] = mock_get_db

        with patch.object(
            GitHubOAuthService, "exchange_code_for_token"
        ) as mock_exchange, patch.object(
            GitHubOAuthService, "get_user_info"
        ) as mock_get_user, patch(
            "app.services.user_service.UserService"
        ) as mock_user_service_class, patch.object(
            JWTService, "create_access_token"
        ) as mock_create_token:
            # 配置模拟
            mock_exchange.return_value = "mock_access_token"
            mock_get_user.return_value = mock_github_user_info

            mock_user_service = mock_user_service_class.return_value
            mock_user_service.create_or_update_github_user = AsyncMock(return_value=mock_user)

            mock_create_token.return_value = "mock_jwt_token"

            # 模拟session
            with client.session_transaction() as sess:
                sess["oauth_state"] = "test_state"

            response = client.post(
                "/api/v1/auth/github/callback", json={"code": "test_code", "state": "test_state"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "mock_jwt_token"
            assert data["token_type"] == "bearer"
            assert "user" in data
            assert data["user"]["github_username"] == "testuser"

            # 验证服务调用
            mock_exchange.assert_called_once_with("test_code")
            mock_get_user.assert_called_once_with("mock_access_token")
            mock_user_service.create_or_update_github_user.assert_called_once_with(
                mock_github_user_info
            )

        app.dependency_overrides.clear()

    def test_github_oauth_callback_invalid_state(self, client):
        """测试GitHub OAuth回调状态参数无效"""
        with client.session_transaction() as sess:
            sess["oauth_state"] = "valid_state"

        response = client.post(
            "/api/v1/auth/github/callback", json={"code": "test_code", "state": "invalid_state"}
        )

        assert response.status_code == 400
        assert "无效的state参数" in response.json()["detail"]


class TestJWTAuthentication:
    """测试JWT认证功能"""

    def test_get_profile_without_token(self, client):
        """测试没有token时访问认证端点"""
        response = client.get("/api/v1/auth/profile")
        assert response.status_code == 403

    def test_get_profile_with_valid_token(self, client, mock_user):
        """测试有效token访问认证端点"""

        def mock_get_current_user():
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user

        response = client.get("/api/v1/auth/profile")

        assert response.status_code == 200
        data = response.json()
        assert data["github_username"] == "testuser"
        assert data["email"] == "test@example.com"

        app.dependency_overrides.clear()

    def test_refresh_token(self, client, mock_user):
        """测试JWT令牌刷新"""

        def mock_get_current_user():
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user

        with patch.object(JWTService, "create_access_token") as mock_create_token:
            mock_create_token.return_value = "new_jwt_token"

            response = client.post("/api/v1/auth/refresh", json={})

            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "new_jwt_token"
            assert "user" in data

        app.dependency_overrides.clear()

    def test_logout(self, client, mock_db, mock_user):
        """测试用户登出"""

        def mock_get_current_user():
            return mock_user

        def mock_get_db():
            return mock_db

        app.dependency_overrides[get_current_user] = mock_get_current_user
        app.dependency_overrides[get_db] = mock_get_db

        with patch.object(JWTService, "blacklist_token") as mock_blacklist:
            mock_blacklist.return_value = True

            headers = {"Authorization": "Bearer mock_token"}
            response = client.post("/api/v1/auth/logout", json={}, headers=headers)

            assert response.status_code == 200
            assert response.json()["message"] == "登出成功"

        app.dependency_overrides.clear()


class TestProtectedEndpoints:
    """测试受保护端点的认证要求"""

    def test_all_protected_endpoints_require_auth(self, client):
        """测试所有受保护的端点都需要认证"""
        protected_endpoints = [
            ("/api/v1/auth/profile", "GET"),
            ("/api/v1/auth/refresh", "POST"),
            ("/api/v1/auth/logout", "POST"),
        ]

        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json={})

            assert response.status_code == 403, f"端点 {method} {endpoint} 应该需要认证"


class TestJWTTokenBlacklist:
    """测试JWT令牌黑名单功能"""

    def test_blacklisted_token_rejected(self, client, mock_db):
        """测试被列入黑名单的令牌被拒绝"""

        def mock_get_db():
            return mock_db

        app.dependency_overrides[get_db] = mock_get_db

        with patch("app.core.auth.JWTBearer.verify_token") as mock_verify:
            mock_verify.side_effect = Exception("Token已被撤销")

            headers = {"Authorization": "Bearer blacklisted_token"}
            response = client.get("/api/v1/auth/profile", headers=headers)

            assert response.status_code == 401

        app.dependency_overrides.clear()


class TestGitHubOAuthService:
    """测试GitHub OAuth服务"""

    @pytest.mark.asyncio
    async def test_exchange_code_for_token_success(self):
        """测试成功交换授权码获取令牌"""
        service = GitHubOAuthService()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = mock_client_class.return_value.__aenter__.return_value
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"access_token": "test_token"}
            mock_client.post.return_value = mock_response

            token = await service.exchange_code_for_token("test_code")

            assert token == "test_token"

    @pytest.mark.asyncio
    async def test_get_user_info_success(self, mock_github_user_info):
        """测试成功获取GitHub用户信息"""
        service = GitHubOAuthService()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = mock_client_class.return_value.__aenter__.return_value

            # 模拟用户信息响应
            mock_user_response = Mock()
            mock_user_response.raise_for_status.return_value = None
            mock_user_response.json.return_value = {
                "id": 12345678,
                "login": "testuser",
                "name": "Test User",
                "avatar_url": "https://avatars.githubusercontent.com/u/12345678?v=4",
                "bio": "Test user biography",
                "location": "Test City",
                "public_repos": 10,
                "followers": 5,
                "following": 3,
            }

            # 模拟邮箱信息响应
            mock_email_response = Mock()
            mock_email_response.raise_for_status.return_value = None
            mock_email_response.json.return_value = [
                {"email": "test@example.com", "primary": True, "verified": True}
            ]

            mock_client.get.side_effect = [mock_user_response, mock_email_response]

            user_info = await service.get_user_info("test_token")

            assert user_info["github_user_id"] == 12345678
            assert user_info["github_username"] == "testuser"
            assert user_info["email"] == "test@example.com"
            assert user_info["name"] == "Test User"


class TestJWTService:
    """测试JWT服务"""

    def test_create_and_verify_token(self):
        """测试JWT令牌创建和验证"""
        service = JWTService()

        user_data = {
            "user_id": 1,
            "github_user_id": 12345678,
            "email": "test@example.com",
            "github_username": "testuser",
        }

        # 创建令牌
        token = service.create_access_token(user_data)
        assert token is not None
        assert isinstance(token, str)

        # 验证令牌
        payload = service.verify_token(token)
        assert payload["user_id"] == 1
        assert payload["github_user_id"] == 12345678
        assert payload["email"] == "test@example.com"
        assert "jti" in payload
        assert "exp" in payload

    @pytest.mark.asyncio
    async def test_token_blacklist(self, mock_db):
        """测试令牌黑名单功能"""
        service = JWTService()

        user_data = {"user_id": 1, "github_user_id": 12345678, "email": "test@example.com"}

        token = service.create_access_token(user_data)

        with patch.object(mock_db, "execute") as mock_execute, patch.object(
            mock_db, "add"
        ) as mock_add, patch.object(mock_db, "commit") as mock_commit:
            mock_execute.return_value.scalar_one_or_none.return_value = None

            result = await service.blacklist_token(token, mock_db)

            assert result is True
            mock_add.assert_called_once()
            mock_commit.assert_called_once()
