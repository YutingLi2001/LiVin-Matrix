"""
用户 API 测试
"""

def test_get_users(client):
    """测试获取用户列表"""
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert isinstance(data["users"], list)


def test_get_user_by_id(client):
    """测试根据 ID 获取用户"""
    user_id = 1
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id


def test_create_user(client, sample_user_data):
    """测试创建用户"""
    response = client.post("/api/v1/users/", json=sample_user_data)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data