"""
主应用测试
"""

def test_read_main_health(client):
    """测试主健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "livin-matrix-backend"
    assert "version" in data


def test_read_root_redirects(client):
    """测试根路径重定向"""
    response = client.get("/")
    # 期望 404 或重定向，因为我们没有根路径处理
    assert response.status_code in [404, 307, 308]