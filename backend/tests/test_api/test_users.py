"""
用户 API 测试 - 更新为统一响应格式
"""

import pytest
from unittest.mock import AsyncMock, patch


class TestUserProfileAPI:
    """测试用户档案API"""
    
    def test_get_user_profile_success(self, client, mock_auth_user):
        """测试成功获取用户档案"""
        with patch('app.api.api_v1.endpoints.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"auth0_user_id": "auth0|123456", "email": "test@example.com"}
            
            with patch('app.services.auth_service.AuthService.get_user_by_auth0_id') as mock_get_by_auth0:
                mock_user = AsyncMock()
                mock_user.id = 1
                mock_user.auth0_user_id = "auth0|123456"
                mock_user.email = "test@example.com"
                mock_user.username = "testuser"
                mock_user.timezone = "UTC"
                mock_user.is_active = True
                mock_get_by_auth0.return_value = mock_user
                
                response = client.get("/api/v1/user/profile")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["message"] == "用户档案获取成功"
                assert data["data"]["email"] == "test@example.com"
                assert data["data"]["username"] == "testuser"
                assert "metadata" in data
    
    def test_get_user_profile_missing_auth0_id(self, client):
        """测试缺少Auth0 ID的情况"""
        with patch('app.api.api_v1.endpoints.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"email": "test@example.com"}  # 缺少auth0_user_id
            
            response = client.get("/api/v1/user/profile")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert data["message"] == "缺少用户ID"
            assert data["error"]["code"] == "bad_request"
    
    def test_get_user_profile_user_not_found(self, client):
        """测试用户不存在的情况"""
        with patch('app.api.api_v1.endpoints.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"auth0_user_id": "auth0|123456", "email": "test@example.com"}
            
            with patch('app.services.auth_service.AuthService.get_user_by_auth0_id') as mock_get_by_auth0:
                mock_get_by_auth0.return_value = None
                
                response = client.get("/api/v1/user/profile")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert data["message"] == "用户不存在"
                assert data["error"]["code"] == "not_found"
    
    def test_update_user_profile_success(self, client):
        """测试成功更新用户档案"""
        update_data = {
            "username": "newusername",
            "timezone": "Asia/Shanghai"
        }
        
        with patch('app.api.api_v1.endpoints.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"auth0_user_id": "auth0|123456", "email": "test@example.com"}
            
            with patch('app.services.user_service.UserService.get_user_by_auth0_id') as mock_get_by_auth0:
                mock_user = AsyncMock()
                mock_user.id = 1
                mock_get_by_auth0.return_value = mock_user
                
                with patch('app.services.user_service.UserService.update_user') as mock_update:
                    updated_user = AsyncMock()
                    updated_user.id = 1
                    updated_user.auth0_user_id = "auth0|123456"
                    updated_user.email = "test@example.com"
                    updated_user.username = "newusername"
                    updated_user.timezone = "Asia/Shanghai"
                    updated_user.is_active = True
                    mock_update.return_value = updated_user
                    
                    response = client.put("/api/v1/user/profile", json=update_data)
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
                    assert data["message"] == "用户档案更新成功"
                    assert data["data"]["username"] == "newusername"
                    assert data["data"]["timezone"] == "Asia/Shanghai"
    
    def test_update_user_profile_validation_error(self, client):
        """测试更新用户档案验证错误"""
        invalid_data = {
            "timezone": ""  # 空时区
        }
        
        response = client.put("/api/v1/user/profile", json=invalid_data)
        
        # FastAPI验证错误会被中间件处理
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "validation_error"
    
    def test_update_user_profile_user_not_found(self, client):
        """测试更新不存在的用户"""
        update_data = {"username": "newusername"}
        
        with patch('app.api.api_v1.endpoints.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"auth0_user_id": "auth0|123456", "email": "test@example.com"}
            
            with patch('app.services.user_service.UserService.get_user_by_auth0_id') as mock_get_by_auth0:
                mock_get_by_auth0.return_value = None
                
                response = client.put("/api/v1/user/profile", json=update_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is False
                assert data["message"] == "用户不存在"
                assert data["error"]["code"] == "not_found"


class TestUserListAPI:
    """测试用户列表API（演示端点）"""
    
    def test_get_users(self, client):
        """测试获取用户列表"""
        with patch('app.api.api_v1.endpoints.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"auth0_user_id": "auth0|123456", "email": "test@example.com"}
            
            response = client.get("/api/v1/user/")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "用户列表端点 - 待实现"
            assert "users" in data["data"]
            assert "total" in data["data"]
            assert isinstance(data["data"]["users"], list)
    
    def test_get_user_by_id(self, client):
        """测试根据 ID 获取用户"""
        user_id = 1
        
        with patch('app.api.api_v1.endpoints.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"auth0_user_id": "auth0|123456", "email": "test@example.com"}
            
            response = client.get(f"/api/v1/user/{user_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "用户详情端点 - 待实现"
            assert data["data"]["user_id"] == user_id


class TestResponseFormat:
    """测试统一响应格式"""
    
    def test_response_format_structure(self, client):
        """测试响应格式结构"""
        with patch('app.api.api_v1.endpoints.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"auth0_user_id": "auth0|123456", "email": "test@example.com"}
            
            response = client.get("/api/v1/user/")
            
            assert response.status_code == 200
            data = response.json()
            
            # 验证响应格式
            assert "success" in data
            assert "data" in data
            assert "message" in data
            assert "error" in data
            assert "metadata" in data
            
            # 验证元数据
            assert "timestamp" in data["metadata"]
            assert "version" in data["metadata"]
            assert data["metadata"]["version"] == "v1"
    
    def test_response_headers(self, client):
        """测试响应头"""
        with patch('app.api.api_v1.endpoints.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"auth0_user_id": "auth0|123456", "email": "test@example.com"}
            
            response = client.get("/api/v1/user/")
            
            # 验证中间件添加的响应头
            assert "x-request-id" in response.headers
            assert "x-api-version" in response.headers
            assert response.headers["x-api-version"] == "v1"


class TestCORSConfiguration:
    """测试CORS配置"""
    
    def test_cors_options_request(self, client):
        """测试CORS预检请求"""
        response = client.options(
            "/api/v1/user/profile",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization"
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_cors_actual_request(self, client):
        """测试CORS实际请求"""
        with patch('app.api.api_v1.endpoints.users.get_current_user') as mock_get_user:
            mock_get_user.return_value = {"auth0_user_id": "auth0|123456", "email": "test@example.com"}
            
            response = client.get(
                "/api/v1/user/",
                headers={"Origin": "http://localhost:3000"}
            )
            
            assert response.status_code == 200
            assert "access-control-allow-origin" in response.headers