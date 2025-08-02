"""
认证API端点测试
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.core.auth import get_current_user


class TestAuthEndpoints:
    """认证API端点测试"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_user_info(self):
        return {
            "auth0_user_id": "auth0|123456789",
            "email": "test@example.com",
            "name": "Test User",
            "nickname": "testuser"
        }
    
    @pytest.fixture
    def mock_user(self):
        mock_user = Mock()
        mock_user.id = 1
        mock_user.auth0_user_id = "auth0|123456789"
        mock_user.email = "test@example.com"
        mock_user.username = "Test User"
        mock_user.timezone = "UTC"
        mock_user.created_at = "2025-01-01T00:00:00Z"
        mock_user.updated_at = "2025-01-01T00:00:00Z"
        return mock_user
    
    def test_get_profile_without_auth(self, client):
        """测试未认证访问档案接口"""
        response = client.get("/api/v1/auth/profile")
        assert response.status_code == 403
    
    def test_get_profile_with_auth(self, client, mock_user_info, mock_user):
        """测试已认证访问档案接口"""
        # 覆盖认证依赖
        def mock_get_current_user():
            return mock_user_info
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        with patch("app.services.auth_service.AuthService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_or_create_user = AsyncMock(return_value=mock_user)
            
            response = client.get("/api/v1/auth/profile")
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["username"] == "Test User"
        
        # 清理依赖覆盖
        app.dependency_overrides.clear()
    
    def test_sync_profile_with_auth(self, client, mock_user_info, mock_user):
        """测试同步用户档案接口"""
        def mock_get_current_user():
            return mock_user_info
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        with patch("app.services.auth_service.AuthService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.sync_user_profile = AsyncMock(return_value=mock_user)
            
            response = client.post("/api/v1/auth/sync")
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            
            mock_service.sync_user_profile.assert_called_once_with(
                "auth0|123456789", mock_user_info
            )
        
        app.dependency_overrides.clear()
    
    def test_sync_profile_missing_user_id(self, client):
        """测试缺少用户ID的同步请求"""
        def mock_get_current_user():
            return {"email": "test@example.com"}  # 缺少auth0_user_id
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.post("/api/v1/auth/sync")
        
        assert response.status_code == 400
        assert "缺少用户ID" in response.json()["detail"]
        
        app.dependency_overrides.clear()


class TestUserEndpoints:
    """用户API端点测试"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_user_info(self):
        return {
            "auth0_user_id": "auth0|123456789",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    def test_get_users_without_auth(self, client):
        """测试未认证访问用户列表"""
        response = client.get("/api/v1/users/")
        assert response.status_code == 403
    
    def test_get_users_with_auth(self, client, mock_user_info):
        """测试已认证访问用户列表"""
        def mock_get_current_user():
            return mock_user_info
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_user"] == "test@example.com"
        assert "message" in data
        
        app.dependency_overrides.clear()
    
    def test_get_user_profile_without_auth(self, client):
        """测试未认证访问用户档案"""
        response = client.get("/api/v1/users/profile")
        assert response.status_code == 403
    
    def test_get_user_profile_with_auth_user_not_found(self, client, mock_user_info):
        """测试已认证但用户不存在"""
        def mock_get_current_user():
            return mock_user_info
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        with patch("app.services.user_service.UserService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_user_by_auth0_id = AsyncMock(return_value=None)
            
            response = client.get("/api/v1/users/profile")
            
            assert response.status_code == 404
            assert "用户不存在" in response.json()["detail"]
        
        app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestAsyncAuthEndpoints:
    """异步认证API端点测试"""
    
    @pytest.fixture
    async def async_client(self):
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_user_info(self):
        return {
            "auth0_user_id": "auth0|123456789",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    async def test_auth_endpoint_async(self, async_client, mock_user_info):
        """测试异步认证端点"""
        def mock_get_current_user():
            return mock_user_info
        
        app.dependency_overrides[get_current_user] = mock_get_current_user
        
        with patch("app.services.auth_service.AuthService") as mock_service_class:
            mock_user = Mock()
            mock_user.email = "test@example.com"
            mock_user.username = "Test User"
            
            mock_service = mock_service_class.return_value
            mock_service.get_or_create_user = AsyncMock(return_value=mock_user)
            
            response = await async_client.get("/api/v1/auth/profile")
            
            assert response.status_code == 200
            
        app.dependency_overrides.clear()