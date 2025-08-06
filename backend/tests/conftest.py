"""
测试配置文件
提供测试所需的fixtures和配置
"""

import os
import asyncio
from typing import Generator, AsyncGenerator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile

# 设置测试环境变量
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "False"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_app():
    """创建测试应用实例"""
    from app.main import create_application
    app = create_application()
    return app


@pytest.fixture(scope="session")  
def client(test_app) -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    with TestClient(test_app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_client(client):
    """创建已认证的测试客户端"""
    class AuthenticatedTestClient:
        def __init__(self, client):
            self.client = client
            self.headers = {"Authorization": "Bearer test_token"}
        
        def get(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.get(url, **kwargs)
        
        def post(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.post(url, **kwargs)
        
        def put(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.put(url, **kwargs)
        
        def delete(self, url, **kwargs):
            kwargs.setdefault("headers", {}).update(self.headers)
            return self.client.delete(url, **kwargs)
    
    return lambda: AuthenticatedTestClient(client)


@pytest.fixture
def mock_github_user():
    """模拟GitHub用户数据"""
    return {
        "id": "123456",
        "login": "testuser",
        "name": "Test User",
        "email": "test@example.com",
        "avatar_url": "https://github.com/images/test.jpg"
    }


@pytest.fixture
def mock_settings():
    """模拟测试配置"""
    class MockSettings:
        PROJECT_NAME = "LiVin Matrix API Test"
        VERSION = "1.0.0-test"
        ENVIRONMENT = "test"
        DEBUG = False
        SECRET_KEY = "test-secret-key"
        DATABASE_URL = "sqlite:///./test.db"
        GITHUB_CLIENT_ID = "test_client_id"
        GITHUB_CLIENT_SECRET = "test_client_secret"
        GITHUB_REDIRECT_URI = "http://localhost:3000/auth/callback"
    
    return MockSettings()


# 数据库测试fixtures（如果需要真实数据库测试）
@pytest.fixture(scope="session")
def test_db():
    """创建测试数据库"""
    # 使用临时文件作为SQLite数据库
    db_fd, db_path = tempfile.mkstemp()
    test_database_url = f"sqlite:///{db_path}"
    
    # 这里可以设置数据库初始化逻辑
    yield test_database_url
    
    # 清理
    os.close(db_fd)
    os.unlink(db_path)


# 测试用户数据
@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "github_user_id": "123456",
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True
    }