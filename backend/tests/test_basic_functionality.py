"""
基础功能测试 - 简化版本确保核心功能工作

这是最小化测试方案的核心测试文件
"""

import pytest
from fastapi.testclient import TestClient


def test_application_can_be_imported():
    """测试应用可以正常导入"""
    from app.main import app

    assert app is not None


def test_create_test_client():
    """测试可以创建测试客户端"""
    from app.main import app

    client = TestClient(app)
    assert client is not None


def test_health_endpoint_basic():
    """测试基础健康检查端点"""
    from app.main import app

    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["status"] == "healthy"


def test_github_auth_url_endpoint():
    """测试GitHub认证URL端点"""
    from app.main import app

    client = TestClient(app)

    response = client.get("/api/v1/auth/github/login")
    assert response.status_code == 200

    data = response.json()
    assert "auth_url" in data
    assert "github.com" in data["auth_url"]


def test_auth_profile_requires_authentication():
    """测试认证端点需要认证"""
    from app.main import app

    client = TestClient(app)

    response = client.get("/api/v1/auth/profile")
    assert response.status_code == 403


def test_user_profile_requires_authentication():
    """测试用户档案端点需要认证"""
    from app.main import app

    client = TestClient(app)

    response = client.get("/api/v1/user/profile")
    assert response.status_code == 403


def test_nonexistent_endpoint_returns_404():
    """测试不存在的端点返回404"""
    from app.main import app

    client = TestClient(app)

    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404


def test_invalid_json_returns_422():
    """测试无效JSON返回422"""
    from app.main import app

    client = TestClient(app)

    response = client.post(
        "/api/v1/auth/github/callback",
        data='{"invalid": json}',  # 无效JSON
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_concurrent_health_checks():
    """测试并发健康检查"""
    from app.main import app
    import threading

    client = TestClient(app)
    results = []

    def make_request():
        response = client.get("/health")
        results.append(response.status_code)

    # 创建3个并发请求
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()

    # 等待所有请求完成
    for thread in threads:
        thread.join()

    # 所有请求都应该成功
    assert all(status == 200 for status in results)
    assert len(results) == 3
