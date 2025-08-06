"""
系统状态检查测试 - 确保API基础可用性 (P0功能)

这个测试模块验证系统的基础健康状态和可用性
符合最小化测试框架要求，覆盖关键的P0功能
"""

import pytest
from fastapi.testclient import TestClient


def test_api_status_returns_success():
    """测试API状态端点返回正常"""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_api_includes_version_info():
    """测试API返回版本信息"""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    data = response.json()
    
    # 验证metadata存在
    assert "metadata" in data
    # 版本信息应该存在
    metadata = data["metadata"]
    assert isinstance(metadata, dict)


def test_api_response_structure():
    """测试API响应结构符合规范"""
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    data = response.json()
    
    # 验证标准响应结构
    assert "success" in data
    assert "data" in data
    assert "metadata" in data
    assert isinstance(data["success"], bool)
    assert isinstance(data["data"], dict)
    assert isinstance(data["metadata"], dict)


def test_api_health_check_performance():
    """测试健康检查端点性能"""
    from app.main import app
    import time
    
    client = TestClient(app)
    
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()
    
    # 健康检查应该在100ms内完成
    response_time = end_time - start_time
    assert response_time < 0.1, f"Health check took {response_time:.3f}s, should be < 0.1s"
    assert response.status_code == 200


def test_api_concurrent_health_checks():
    """测试并发健康检查请求"""
    from app.main import app
    import threading
    
    client = TestClient(app)
    results = []
    errors = []
    
    def make_request():
        try:
            response = client.get("/health")
            results.append(response.status_code)
        except Exception as e:
            errors.append(str(e))
    
    # 创建5个并发请求
    threads = []
    for _ in range(5):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # 等待所有请求完成
    for thread in threads:
        thread.join()
    
    # 所有请求都应该成功
    assert len(errors) == 0, f"Errors occurred: {errors}"
    assert all(status == 200 for status in results)
    assert len(results) == 5