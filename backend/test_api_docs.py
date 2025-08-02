#!/usr/bin/env python3
"""
验证API文档可访问性的简单测试脚本
"""

import os
from fastapi.testclient import TestClient

# 设置测试环境变量
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
os.environ["ENVIRONMENT"] = "development"

from app.main import app

client = TestClient(app)

def test_openapi_json():
    """测试OpenAPI JSON端点"""
    response = client.get("/api/v1/openapi.json")
    print(f"OpenAPI JSON status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"OpenAPI version: {data.get('openapi')}")
        print(f"API title: {data['info']['title']}")
        print(f"API version: {data['info']['version']}")
        print(f"Number of paths: {len(data.get('paths', {}))}")
        
        # 检查用户端点是否存在
        paths = data.get('paths', {})
        user_profile_path = "/api/v1/user/profile"
        if user_profile_path in paths:
            print(f"✓ {user_profile_path} 端点存在")
            methods = list(paths[user_profile_path].keys())
            print(f"  支持的方法: {methods}")
        else:
            print(f"✗ {user_profile_path} 端点不存在")
    else:
        print(f"Error: {response.text}")

def test_swagger_docs():
    """测试Swagger文档端点"""
    response = client.get("/docs")
    print(f"Swagger UI status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Swagger UI 可访问")
        if "swagger" in response.text.lower():
            print("✓ 页面包含Swagger内容")
    else:
        print(f"Error accessing Swagger UI: {response.text}")

def test_redoc_docs():
    """测试ReDoc文档端点"""
    response = client.get("/redoc")
    print(f"ReDoc status: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ ReDoc 可访问")
        if "redoc" in response.text.lower():
            print("✓ 页面包含ReDoc内容")
    else:
        print(f"Error accessing ReDoc: {response.text}")

def test_health_endpoint():
    """测试健康检查端点"""
    response = client.get("/health")
    print(f"Health check status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 健康检查响应: {data}")
        
        # 验证统一响应格式
        if "success" in data and "data" in data:
            print("✓ 使用统一响应格式")
        else:
            print("✗ 未使用统一响应格式")
    else:
        print(f"Error: {response.text}")

def test_api_version_headers():
    """测试API版本响应头"""
    response = client.get("/health")
    
    if "x-api-version" in response.headers:
        print(f"✓ API版本头存在: {response.headers['x-api-version']}")
    else:
        print("✗ API版本头不存在")
    
    if "x-request-id" in response.headers:
        print(f"✓ 请求ID头存在: {response.headers['x-request-id']}")
    else:
        print("✗ 请求ID头不存在")

def test_cors_configuration():
    """测试CORS配置"""
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    
    if "access-control-allow-origin" in response.headers:
        print(f"✓ CORS配置正确: {response.headers['access-control-allow-origin']}")
    else:
        print("✗ CORS未正确配置")

if __name__ == "__main__":
    print("=== API文档可访问性验证 ===\n")
    
    print("1. OpenAPI JSON 端点测试:")
    test_openapi_json()
    
    print("\n2. Swagger UI 文档测试:")
    test_swagger_docs()
    
    print("\n3. ReDoc 文档测试:")
    test_redoc_docs()
    
    print("\n4. 健康检查端点测试:")
    test_health_endpoint()
    
    print("\n5. API版本头测试:")
    test_api_version_headers()
    
    print("\n6. CORS配置测试:")
    test_cors_configuration()
    
    print("\n=== 验证完成 ===")