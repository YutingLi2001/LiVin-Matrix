"""
健康检查 API 测试
"""


def test_health_check(client):
    """测试健康检查端点"""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "livin-matrix-backend"
    assert "version" in data
    assert "environment" in data


def test_database_health(client):
    """测试数据库健康检查"""
    response = client.get("/api/v1/health/database")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["component"] == "database"


def test_redis_health(client):
    """测试 Redis 健康检查"""
    response = client.get("/api/v1/health/redis")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["component"] == "redis"
