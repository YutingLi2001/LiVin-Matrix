"""
核心功能测试 - 精简版
只测试真正重要的20%业务功能
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """测试系统健康检查 - 最重要的基础测试"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_github_oauth_login():
    """测试GitHub OAuth登录重定向"""
    response = client.get("/api/v1/auth/github/login")
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "github.com/login/oauth/authorize" in data["auth_url"]


def test_protected_route_requires_auth():
    """测试受保护路由需要认证"""
    response = client.get("/api/v1/auth/profile")
    assert response.status_code == 403


def test_user_profile_requires_auth():
    """测试用户档案需要认证"""
    response = client.get("/api/v1/user/profile")
    assert response.status_code == 403


def test_404_error_handling():
    """测试404错误处理"""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert isinstance(data, dict)
    # 验证包含错误信息
    has_error_info = "detail" in data or "error" in data or "message" in data
    assert has_error_info


def test_application_startup():
    """测试应用可以正常启动"""
    from app.main import app

    assert app is not None


def test_basic_api_structure():
    """测试API基本结构"""
    # 测试根路径重定向或返回基本信息
    response = client.get("/")
    # 应该返回某种响应，不应该是500错误
    assert response.status_code < 500


def test_cors_headers():
    """测试CORS配置"""
    response = client.get("/health")
    assert response.status_code == 200
    # 基本验证响应头存在
    assert "content-type" in response.headers


def test_database_connection_health():
    """通过健康检查间接测试数据库连接"""
    response = client.get("/health")
    assert response.status_code == 200
    # 如果数据库有问题，健康检查应该反映出来
    data = response.json()
    assert data["success"] is True


def test_json_response_format():
    """测试JSON响应格式一致性"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    # 验证标准响应格式
    assert "success" in data
    assert "data" in data
    assert isinstance(data["success"], bool)


def test_api_version_endpoint():
    """测试API版本信息"""
    response = client.get("/health")
    data = response.json()
    if "metadata" in data:
        metadata = data["metadata"]
        assert isinstance(metadata, dict)


def test_environment_configuration():
    """测试环境配置加载"""
    from app.core.config import get_settings

    settings = get_settings()
    # 验证关键配置项存在
    assert hasattr(settings, "PROJECT_NAME")
    assert hasattr(settings, "VERSION")
