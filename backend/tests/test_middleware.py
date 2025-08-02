"""
测试中间件功能
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.middleware.error_handler import (
    setup_exception_handlers,
    RequestIDMiddleware,
    APIVersionMiddleware,
    _get_error_code_from_status
)
from app.schemas.responses import ErrorCodes


class TestExceptionHandlers:
    """测试异常处理器"""
    
    def test_http_exception_handler(self):
        """测试HTTP异常处理"""
        app = FastAPI()
        setup_exception_handlers(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise HTTPException(status_code=404, detail="Resource not found")
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Resource not found"
        assert data["error"]["code"] == ErrorCodes.NOT_FOUND
        assert "metadata" in data
        assert "request_id" in data["metadata"]
    
    def test_starlette_http_exception_handler(self):
        """测试Starlette HTTP异常处理"""
        app = FastAPI()
        setup_exception_handlers(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise StarletteHTTPException(status_code=500, detail="Internal error")
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Internal error"
        assert data["error"]["code"] == ErrorCodes.INTERNAL_ERROR
    
    def test_validation_exception_handler(self):
        """测试验证异常处理"""
        from fastapi.exceptions import RequestValidationError
        from pydantic import BaseModel
        
        app = FastAPI()
        setup_exception_handlers(app)
        
        class TestModel(BaseModel):
            name: str
            age: int
        
        @app.post("/test")
        async def test_endpoint(data: TestModel):
            return {"message": "success"}
        
        client = TestClient(app)
        response = client.post("/test", json={"name": "test"})  # 缺少age字段
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "请求数据验证失败"
        assert data["error"]["code"] == ErrorCodes.VALIDATION_ERROR
    
    def test_general_exception_handler(self):
        """测试通用异常处理"""
        app = FastAPI()
        setup_exception_handlers(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise ValueError("Something went wrong")
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "服务器内部错误"
        assert data["error"]["code"] == ErrorCodes.INTERNAL_ERROR


class TestRequestIDMiddleware:
    """测试请求ID中间件"""
    
    def test_request_id_added_to_response(self):
        """测试请求ID添加到响应头"""
        app = FastAPI()
        app.add_middleware(RequestIDMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) > 0


class TestAPIVersionMiddleware:
    """测试API版本中间件"""
    
    def test_api_version_added_to_response(self):
        """测试API版本添加到响应头"""
        app = FastAPI()
        app.add_middleware(APIVersionMiddleware, version="v1")
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.headers["x-api-version"] == "v1"
    
    def test_custom_version(self):
        """测试自定义版本"""
        app = FastAPI()
        app.add_middleware(APIVersionMiddleware, version="v2.1")
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.headers["x-api-version"] == "v2.1"


class TestErrorCodeMapping:
    """测试状态码到错误代码的映射"""
    
    def test_get_error_code_from_status(self):
        """测试状态码映射"""
        assert _get_error_code_from_status(400) == ErrorCodes.BAD_REQUEST
        assert _get_error_code_from_status(401) == ErrorCodes.AUTHENTICATION_ERROR
        assert _get_error_code_from_status(403) == ErrorCodes.AUTHORIZATION_ERROR
        assert _get_error_code_from_status(404) == ErrorCodes.NOT_FOUND
        assert _get_error_code_from_status(409) == ErrorCodes.CONFLICT
        assert _get_error_code_from_status(422) == ErrorCodes.VALIDATION_ERROR
        assert _get_error_code_from_status(429) == ErrorCodes.TOO_MANY_REQUESTS
        assert _get_error_code_from_status(500) == ErrorCodes.INTERNAL_ERROR
        assert _get_error_code_from_status(503) == ErrorCodes.SERVICE_UNAVAILABLE
    
    def test_unknown_status_code(self):
        """测试未知状态码映射"""
        assert _get_error_code_from_status(418) == ErrorCodes.INTERNAL_ERROR
        assert _get_error_code_from_status(999) == ErrorCodes.INTERNAL_ERROR


class TestMiddlewareIntegration:
    """测试中间件集成"""
    
    def test_middleware_order(self):
        """测试中间件执行顺序"""
        app = FastAPI()
        
        # 添加中间件的顺序很重要
        app.add_middleware(RequestIDMiddleware)
        app.add_middleware(APIVersionMiddleware, version="v1")
        setup_exception_handlers(app)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        # 验证所有中间件都正常工作
        assert response.status_code == 200
        assert "x-request-id" in response.headers
        assert response.headers["x-api-version"] == "v1"
    
    def test_middleware_with_exception(self):
        """测试中间件与异常处理的配合"""
        app = FastAPI()
        
        app.add_middleware(RequestIDMiddleware)
        app.add_middleware(APIVersionMiddleware, version="v1")
        setup_exception_handlers(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise HTTPException(status_code=400, detail="Bad request")
        
        client = TestClient(app)
        response = client.get("/test")
        
        assert response.status_code == 400
        # 验证中间件仍然正常工作
        assert "x-request-id" in response.headers
        assert response.headers["x-api-version"] == "v1"
        
        # 验证异常处理格式
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == ErrorCodes.BAD_REQUEST


class TestLogging:
    """测试日志记录"""
    
    @patch('app.middleware.error_handler.logger')
    def test_error_logging(self, mock_logger):
        """测试错误日志记录"""
        app = FastAPI()
        setup_exception_handlers(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise HTTPException(status_code=404, detail="Not found")
        
        client = TestClient(app)
        response = client.get("/test")
        
        # 验证日志被调用
        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args
        assert "HTTP Exception - 404" in call_args[0][0]
    
    @patch('app.middleware.error_handler.logger')
    def test_general_exception_logging(self, mock_logger):
        """测试通用异常日志记录"""
        app = FastAPI()
        setup_exception_handlers(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise ValueError("Test error")
        
        client = TestClient(app)
        response = client.get("/test")
        
        # 验证错误级别日志被调用
        mock_logger.error.assert_called()
        call_args = mock_logger.error.call_args
        assert "Unhandled Exception" in call_args[0][0]