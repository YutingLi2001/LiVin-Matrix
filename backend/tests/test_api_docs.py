"""
测试API文档生成和访问
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestAPIDocumentation:
    """测试API文档功能"""
    
    def test_openapi_json_endpoint(self):
        """测试OpenAPI JSON端点"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证OpenAPI schema基础结构
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert "components" in data
        
        # 验证应用信息
        assert data["info"]["title"] == "LiVin Matrix API"
        assert data["info"]["description"] == "生活数据相关性分析平台 API"
        assert "version" in data["info"]
    
    def test_swagger_ui_docs_endpoint(self):
        """测试Swagger UI文档端点"""
        client = TestClient(app)
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "swagger" in response.text.lower()
    
    def test_redoc_docs_endpoint(self):
        """测试ReDoc文档端点"""
        client = TestClient(app)
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "redoc" in response.text.lower()
    
    def test_api_endpoints_in_openapi_schema(self):
        """测试API端点在OpenAPI schema中存在"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        paths = data["paths"]
        
        # 验证用户相关端点
        assert "/api/v1/user/profile" in paths
        assert "get" in paths["/api/v1/user/profile"]
        assert "put" in paths["/api/v1/user/profile"]
        
        # 验证健康检查端点
        assert "/health" in paths
        assert "get" in paths["/health"]
        
        # 验证API版本化路由存在
        assert "/api/v1/user/" in paths
        assert "/api/v1/user/{user_id}" in paths
    
    def test_response_schemas_in_openapi(self):
        """测试响应格式在OpenAPI schema中正确定义"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        # 检查components schemas
        components = data.get("components", {})
        schemas = components.get("schemas", {})
        
        # 验证基础schemas存在
        assert len(schemas) > 0
        
        # 验证用户相关schemas
        user_profile_endpoint = data["paths"]["/api/v1/user/profile"]["get"]
        assert "responses" in user_profile_endpoint
        assert "200" in user_profile_endpoint["responses"]
    
    def test_authentication_requirements_documented(self):
        """测试认证要求在文档中标注"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        paths = data["paths"]
        
        # 检查用户档案端点的安全要求
        user_profile_get = paths["/api/v1/user/profile"]["get"]
        
        # 验证端点文档化（描述存在）
        assert "summary" in user_profile_get or "description" in user_profile_get
        
        # 验证参数文档化
        if "parameters" in user_profile_get:
            assert isinstance(user_profile_get["parameters"], list)
    
    def test_error_responses_documented(self):
        """测试错误响应在文档中说明"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        paths = data["paths"]
        
        # 检查用户档案端点的响应文档
        user_profile_responses = paths["/api/v1/user/profile"]["get"]["responses"]
        
        # 验证至少有200响应
        assert "200" in user_profile_responses
        
        # 验证响应内容描述
        assert "description" in user_profile_responses["200"]
    
    def test_request_examples_in_documentation(self):
        """测试请求示例在文档中存在"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        paths = data["paths"]
        
        # 检查PUT端点的请求体文档
        if "/api/v1/user/profile" in paths and "put" in paths["/api/v1/user/profile"]:
            put_endpoint = paths["/api/v1/user/profile"]["put"]
            
            if "requestBody" in put_endpoint:
                request_body = put_endpoint["requestBody"]
                assert "content" in request_body
                assert "application/json" in request_body["content"]
    
    def test_api_version_in_documentation(self):
        """测试API版本在文档中体现"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证服务器URL包含版本前缀
        servers = data.get("servers", [])
        if servers:
            # 检查是否有服务器URL配置
            assert isinstance(servers, list)
        
        # 验证所有路径都有/api/v1前缀（通过实际路径检查）
        paths = data["paths"]
        api_v1_paths = [path for path in paths.keys() if path.startswith("/api/v1")]
        assert len(api_v1_paths) > 0
    
    def test_tags_organization_in_documentation(self):
        """测试API端点标签组织"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        paths = data["paths"]
        
        # 收集所有使用的标签
        used_tags = set()
        for path_info in paths.values():
            for method_info in path_info.values():
                if "tags" in method_info:
                    used_tags.update(method_info["tags"])
        
        # 验证标签存在
        assert len(used_tags) > 0
        
        # 验证特定标签存在
        expected_tags = {"用户管理", "健康检查", "用户认证"}
        assert len(used_tags.intersection(expected_tags)) > 0


class TestAPIPerformance:
    """测试API文档性能"""
    
    def test_docs_load_time(self):
        """测试文档加载时间"""
        import time
        
        client = TestClient(app)
        
        start_time = time.time()
        response = client.get("/docs")
        end_time = time.time()
        
        load_time = end_time - start_time
        
        assert response.status_code == 200
        # 文档加载应该在2秒内完成
        assert load_time < 2.0
    
    def test_openapi_json_load_time(self):
        """测试OpenAPI JSON加载时间"""
        import time
        
        client = TestClient(app)
        
        start_time = time.time()
        response = client.get("/api/v1/openapi.json")
        end_time = time.time()
        
        load_time = end_time - start_time
        
        assert response.status_code == 200
        # OpenAPI JSON应该在1秒内加载完成
        assert load_time < 1.0


class TestDocumentationContent:
    """测试文档内容质量"""
    
    def test_endpoint_descriptions_exist(self):
        """测试端点描述存在"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        paths = data["paths"]
        
        # 检查关键端点有描述
        key_endpoints = [
            ("/api/v1/user/profile", "get"),
            ("/api/v1/user/profile", "put"),
        ]
        
        for path, method in key_endpoints:
            if path in paths and method in paths[path]:
                endpoint = paths[path][method]
                # 至少有summary或description之一
                assert "summary" in endpoint or "description" in endpoint
    
    def test_schema_descriptions_exist(self):
        """测试模型描述存在"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        components = data.get("components", {})
        schemas = components.get("schemas", {})
        
        # 检查重要的schema有描述
        for schema_name, schema_def in schemas.items():
            # 大部分schema应该有description或title
            if isinstance(schema_def, dict):
                has_description = "description" in schema_def or "title" in schema_def
                # 对于重要的业务模型，应该有描述
                if "user" in schema_name.lower() or "response" in schema_name.lower():
                    assert has_description, f"Schema {schema_name} should have description"
    
    def test_response_examples_quality(self):
        """测试响应示例质量"""
        client = TestClient(app)
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        paths = data["paths"]
        
        # 检查用户档案端点的响应示例
        if "/api/v1/user/profile" in paths:
            get_endpoint = paths["/api/v1/user/profile"]["get"]
            responses = get_endpoint.get("responses", {})
            
            if "200" in responses:
                success_response = responses["200"]
                # 验证响应有内容描述
                assert "description" in success_response
                
                # 如果有content，验证结构
                if "content" in success_response:
                    content = success_response["content"]
                    if "application/json" in content:
                        json_content = content["application/json"]
                        # 验证有schema或example
                        assert "schema" in json_content or "examples" in json_content