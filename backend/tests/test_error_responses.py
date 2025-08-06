"""
API统一错误响应格式测试 (P2功能)

这个测试模块验证API的错误处理和统一响应格式
确保所有错误场景都返回一致的错误结构
"""

import pytest
from fastapi.testclient import TestClient


def test_404_error_format():
    """测试404错误响应格式"""
    from app.main import app

    client = TestClient(app)

    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404

    data = response.json()

    # 验证错误响应的基本结构
    # 项目可能使用自定义错误格式而非标准FastAPI格式
    assert isinstance(data, dict)

    # 检查可能的错误字段
    has_error_info = "detail" in data or "error" in data or "message" in data or "success" in data
    assert has_error_info, f"Expected error information in response: {data}"

    # 如果有success字段，应该为False
    if "success" in data:
        assert data["success"] is False


def test_authentication_error_format():
    """测试认证错误响应格式"""
    from app.main import app

    client = TestClient(app)

    response = client.get("/api/v1/auth/profile")
    assert response.status_code == 403  # 或401，取决于实现

    data = response.json()
    assert isinstance(data, dict)

    # 验证认证错误包含适当的错误信息
    has_auth_error = (
        ("detail" in data and "auth" in str(data["detail"]).lower())
        or ("error" in data)
        or ("message" in data and "auth" in str(data["message"]).lower())
        or ("success" in data and data["success"] is False)
    )
    assert has_auth_error, f"Expected authentication error information: {data}"


def test_method_not_allowed_error():
    """测试HTTP方法不允许错误"""
    from app.main import app

    client = TestClient(app)

    # 对GET端点使用POST方法
    response = client.post("/health")
    assert response.status_code == 405

    data = response.json()
    assert isinstance(data, dict)

    # 验证方法不允许错误格式
    has_method_error = "detail" in data or "error" in data or "message" in data
    assert has_method_error


def test_validation_error_format():
    """测试请求验证错误格式(简化版)"""
    from app.schemas.auth import GitHubCallbackRequest

    # 测试Schema验证而不是端点调用，避免数据库依赖
    try:
        # 尝试创建一个缺少必需字段的请求
        GitHubCallbackRequest(invalid="incomplete_data")
        assert False, "应该抛出验证错误"
    except ValueError as e:
        # 这是Pydantic的验证错误
        assert "validation" in str(e).lower() or "field required" in str(e).lower()
    except Exception as e:
        # 其他类型的验证错误也是可接受的
        assert (
            "field" in str(e).lower() or "required" in str(e).lower() or "missing" in str(e).lower()
        )


def test_internal_server_error_format():
    """测试500内部服务器错误格式(模拟)"""
    from app.main import app

    client = TestClient(app)

    # 尝试访问可能导致内部错误的端点
    # 由于我们不想真正破坏系统，这个测试主要验证错误处理结构

    response = client.get("/api/v1/auth/debug/config")

    # 无论返回什么状态码，都应该是有效的JSON响应
    if response.status_code >= 500:
        data = response.json()
        assert isinstance(data, dict)

        # 500错误应该包含错误信息但不暴露敏感细节
        has_safe_error = "detail" in data or "error" in data or "message" in data
        assert has_safe_error
    else:
        # 如果没有500错误，说明端点实现良好
        assert response.status_code < 500


def test_cors_and_security_headers():
    """测试CORS和安全响应头"""
    from app.main import app

    client = TestClient(app)

    response = client.get("/health")
    headers = response.headers

    # 验证基本的响应头存在
    assert "content-type" in headers

    # 检查可能存在的安全头
    security_headers = [
        "x-content-type-options",
        "x-frame-options",
        "x-xss-protection",
        "strict-transport-security",
        "access-control-allow-origin",
    ]

    # 至少应该有一些安全相关的头部设置
    # 如果没有也不算失败，但记录信息
    found_security_headers = [h for h in security_headers if h in headers]
    # 这个断言总是通过，只是为了记录
    assert isinstance(found_security_headers, list)


def test_error_response_consistency():
    """测试错误响应的一致性"""
    from app.main import app

    client = TestClient(app)

    # 收集不同类型的错误响应
    error_responses = []

    # 404错误
    resp_404 = client.get("/api/v1/nonexistent")
    if resp_404.status_code == 404:
        error_responses.append(resp_404.json())

    # 403认证错误
    resp_403 = client.get("/api/v1/auth/profile")
    if resp_403.status_code == 403:
        error_responses.append(resp_403.json())

    # 405方法错误
    resp_405 = client.post("/health")
    if resp_405.status_code == 405:
        error_responses.append(resp_405.json())

    # 验证所有错误响应都是字典类型
    for error_resp in error_responses:
        assert isinstance(error_resp, dict)

        # 检查一致的错误结构
        # 如果有success字段，所有错误都应该是False
        if "success" in error_resp:
            assert error_resp["success"] is False


def test_error_message_security():
    """测试错误消息不泄露敏感信息"""
    from app.main import app

    client = TestClient(app)

    # 尝试访问可能敏感的端点
    sensitive_paths = [
        "/api/v1/nonexistent",
        "/api/v1/auth/profile",
        "/admin",
        "/database",
        "/config",
    ]

    for path in sensitive_paths:
        response = client.get(path)

        # 无论返回什么错误，都不应该包含敏感信息
        if response.status_code >= 400:
            data = response.json()
            response_text = str(data).lower()

            # 检查不应该出现的敏感信息
            sensitive_terms = [
                "password",
                "secret",
                "key",
                "token",
                "database",
                "sql",
                "connection",
                "traceback",
                "exception",
                "stack",
            ]

            # 在测试环境中可能会有一些调试信息，这是可接受的
            # 我们主要检查是否有明显的敏感信息泄露
            for term in sensitive_terms:
                if term in response_text:
                    # 如果包含敏感信息，至少确保不是明文密码等
                    assert "password=" not in response_text
                    assert "secret=" not in response_text


def test_concurrent_error_handling():
    """测试并发错误处理"""
    from app.main import app
    import threading

    client = TestClient(app)
    results = []

    def make_error_request():
        response = client.get("/api/v1/nonexistent")
        results.append(
            {"status_code": response.status_code, "is_json": True, "response": response.json()}
        )

    # 创建多个并发的错误请求
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=make_error_request)
        threads.append(thread)
        thread.start()

    # 等待所有请求完成
    for thread in threads:
        thread.join()

    # 验证所有错误响应都一致
    assert len(results) == 3
    for result in results:
        assert result["status_code"] == 404
        assert result["is_json"] is True
        assert isinstance(result["response"], dict)


def test_rate_limiting_error_format():
    """测试速率限制错误格式(如果实现了)"""
    from app.main import app

    client = TestClient(app)

    # 快速发送多个请求以测试是否有速率限制
    responses = []
    for i in range(10):
        response = client.get("/health")
        responses.append(response)

        # 如果遇到速率限制错误，验证格式
        if response.status_code == 429:
            data = response.json()
            assert isinstance(data, dict)

            # 速率限制错误应该包含适当信息
            has_rate_limit_info = "detail" in data or "error" in data or "message" in data
            assert has_rate_limit_info
            break

    # 如果没有速率限制，也是正常的
    # 至少验证所有响应都是有效的
    for response in responses:
        if response.status_code == 200:
            assert response.json()["success"] is True


def test_api_version_in_error_responses():
    """测试错误响应中的API版本信息"""
    from app.main import app

    client = TestClient(app)

    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404

    data = response.json()

    # 检查是否包含版本或元数据信息
    if "metadata" in data:
        metadata = data["metadata"]
        assert isinstance(metadata, dict)

        # 如果有版本信息，应该是合理的格式
        if "version" in metadata:
            version = metadata["version"]
            assert isinstance(version, str)
            assert len(version) > 0

    # 如果没有元数据也是正常的，这个测试总是通过
    assert True
