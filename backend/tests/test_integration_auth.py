"""
认证系统集成测试
"""
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_db():
    """模拟数据库会话"""
    mock_session = Mock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def mock_user_token_payload():
    """模拟JWT token payload"""
    return {
        "sub": "auth0|test123456789",
        "email": "test@example.com",
        "email_verified": True,
        "name": "Test User",
        "nickname": "testuser",
        "picture": "https://example.com/avatar.jpg",
        "aud": "test-audience",
        "iss": "https://test-domain.auth0.com/",
    }


def test_health_check_no_auth_required(client):
    """测试健康检查端点不需要认证"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200


def test_auth_profile_without_token(client):
    """测试没有token时访问认证端点"""
    response = client.get("/api/v1/auth/profile")
    assert response.status_code == 403  # FastAPI的HTTPBearer默认返回403


def test_auth_profile_with_mock_token(client, mock_db, mock_user_token_payload):
    """测试有效token访问认证端点"""

    # 模拟用户信息
    def mock_get_current_user():
        return {
            "auth0_user_id": mock_user_token_payload["sub"],
            "email": mock_user_token_payload["email"],
            "name": mock_user_token_payload["name"],
            "nickname": mock_user_token_payload["nickname"],
        }

    def mock_get_db():
        return mock_db

    # 覆盖依赖
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_db] = mock_get_db

    with patch("app.services.auth_service.AuthService") as mock_auth_service_class:
        # 模拟用户对象
        mock_user = Mock()
        mock_user.id = 1
        mock_user.auth0_user_id = mock_user_token_payload["sub"]
        mock_user.email = mock_user_token_payload["email"]
        mock_user.username = mock_user_token_payload["name"]
        mock_user.timezone = "UTC"
        mock_user.is_active = True

        # 配置模拟服务
        mock_auth_service = mock_auth_service_class.return_value
        mock_auth_service.get_or_create_user.return_value = mock_user

        response = client.get("/api/v1/auth/profile")

        assert response.status_code == 200

        # 验证服务被正确调用
        mock_auth_service.get_or_create_user.assert_called_once()

        # 清理依赖覆盖
        app.dependency_overrides.clear()


def test_user_profile_with_mock_token(client, mock_db, mock_user_token_payload):
    """测试用户档案端点"""

    def mock_get_current_user():
        return {
            "auth0_user_id": mock_user_token_payload["sub"],
            "email": mock_user_token_payload["email"],
            "name": mock_user_token_payload["name"],
        }

    def mock_get_db():
        return mock_db

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_db] = mock_get_db

    with patch("app.services.auth_service.AuthService") as mock_auth_service_class:
        mock_user = Mock()
        mock_user.id = 1
        mock_user.auth0_user_id = mock_user_token_payload["sub"]
        mock_user.email = mock_user_token_payload["email"]
        mock_user.username = mock_user_token_payload["name"]

        mock_auth_service = mock_auth_service_class.return_value
        mock_auth_service.get_user_by_auth0_id.return_value = mock_user

        response = client.get("/api/v1/users/profile")

        assert response.status_code == 200

        mock_auth_service.get_user_by_auth0_id.assert_called_once_with(
            mock_user_token_payload["sub"]
        )

        app.dependency_overrides.clear()


def test_user_profile_user_not_found(client, mock_db, mock_user_token_payload):
    """测试用户不存在的情况"""

    def mock_get_current_user():
        return {
            "auth0_user_id": mock_user_token_payload["sub"],
            "email": mock_user_token_payload["email"],
        }

    def mock_get_db():
        return mock_db

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_db] = mock_get_db

    with patch("app.services.auth_service.AuthService") as mock_auth_service_class:
        mock_auth_service = mock_auth_service_class.return_value
        mock_auth_service.get_user_by_auth0_id.return_value = None

        response = client.get("/api/v1/users/profile")

        assert response.status_code == 404
        assert "用户不存在" in response.json()["detail"]

        app.dependency_overrides.clear()


def test_protected_endpoints_require_auth(client):
    """测试所有受保护的端点都需要认证"""
    protected_endpoints = [
        "/api/v1/auth/profile",
        "/api/v1/auth/sync",
        "/api/v1/users/profile",
        "/api/v1/users/",
        "/api/v1/users/123",
    ]

    for endpoint in protected_endpoints:
        if endpoint.endswith("sync"):
            response = client.post(endpoint)
        else:
            response = client.get(endpoint)

        assert response.status_code == 403, f"端点 {endpoint} 应该需要认证"


def test_auth_sync_endpoint(client, mock_db, mock_user_token_payload):
    """测试用户信息同步端点"""

    def mock_get_current_user():
        return {
            "auth0_user_id": mock_user_token_payload["sub"],
            "email": mock_user_token_payload["email"],
            "name": "Updated Name",  # 模拟信息更新
        }

    def mock_get_db():
        return mock_db

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[get_db] = mock_get_db

    with patch("app.services.auth_service.AuthService") as mock_auth_service_class:
        mock_user = Mock()
        mock_user.username = "Updated Name"

        mock_auth_service = mock_auth_service_class.return_value
        mock_auth_service.sync_user_profile.return_value = mock_user

        response = client.post("/api/v1/auth/sync")

        assert response.status_code == 200

        mock_auth_service.sync_user_profile.assert_called_once()

        app.dependency_overrides.clear()
