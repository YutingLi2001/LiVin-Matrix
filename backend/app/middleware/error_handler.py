"""
全局错误处理中间件
"""

import logging
import traceback
import uuid
from typing import Dict, Any
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from app.schemas.responses import create_error_response, ErrorCodes

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI) -> None:
    """设置全局异常处理器"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """HTTP异常处理器"""
        request_id = str(uuid.uuid4())
        
        # 记录错误日志
        logger.warning(
            f"HTTP Exception - {exc.status_code}: {exc.detail}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code
            }
        )
        
        # 根据状态码确定错误类型
        error_code = _get_error_code_from_status(exc.status_code)
        
        response_data = create_error_response(
            message=str(exc.detail),
            error_code=error_code,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Starlette HTTP异常处理器"""
        request_id = str(uuid.uuid4())
        
        logger.warning(
            f"Starlette HTTP Exception - {exc.status_code}: {exc.detail}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code
            }
        )
        
        error_code = _get_error_code_from_status(exc.status_code)
        
        response_data = create_error_response(
            message=str(exc.detail),
            error_code=error_code,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """请求验证错误处理器"""
        request_id = str(uuid.uuid4())
        
        # 格式化验证错误信息
        validation_errors = []
        for error in exc.errors():
            validation_errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Validation Error: {validation_errors}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "validation_errors": validation_errors
            }
        )
        
        response_data = create_error_response(
            message="请求数据验证失败",
            error_code=ErrorCodes.VALIDATION_ERROR,
            details={"validation_errors": validation_errors},
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_data
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Pydantic验证错误处理器"""
        request_id = str(uuid.uuid4())
        
        # 格式化Pydantic验证错误
        validation_errors = []
        for error in exc.errors():
            validation_errors.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Pydantic Validation Error: {validation_errors}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "validation_errors": validation_errors
            }
        )
        
        response_data = create_error_response(
            message="数据模型验证失败",
            error_code=ErrorCodes.VALIDATION_ERROR,
            details={"validation_errors": validation_errors},
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_data
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """数据库错误处理器"""
        request_id = str(uuid.uuid4())
        
        logger.error(
            f"Database Error: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__
            }
        )
        
        response_data = create_error_response(
            message="数据库操作失败",
            error_code=ErrorCodes.INTERNAL_ERROR,
            details={"database_error": str(exc)} if logger.level <= logging.DEBUG else None,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_data
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """通用异常处理器"""
        request_id = str(uuid.uuid4())
        
        # 记录完整的异常信息
        logger.error(
            f"Unhandled Exception: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc()
            }
        )
        
        response_data = create_error_response(
            message="服务器内部错误",
            error_code=ErrorCodes.INTERNAL_ERROR,
            details={"error_detail": str(exc)} if logger.level <= logging.DEBUG else None,
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_data
        )


def _get_error_code_from_status(status_code: int) -> str:
    """根据HTTP状态码获取对应的错误代码"""
    status_to_code = {
        400: ErrorCodes.BAD_REQUEST,
        401: ErrorCodes.AUTHENTICATION_ERROR,
        403: ErrorCodes.AUTHORIZATION_ERROR,
        404: ErrorCodes.NOT_FOUND,
        409: ErrorCodes.CONFLICT,
        422: ErrorCodes.VALIDATION_ERROR,
        429: ErrorCodes.TOO_MANY_REQUESTS,
        500: ErrorCodes.INTERNAL_ERROR,
        503: ErrorCodes.SERVICE_UNAVAILABLE,
    }
    return status_to_code.get(status_code, ErrorCodes.INTERNAL_ERROR)


class RequestIDMiddleware:
    """请求ID中间件，为每个请求生成唯一ID"""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request_id = str(uuid.uuid4())
            scope["request_id"] = request_id
            
            # 添加到响应头
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append([b"x-request-id", request_id.encode()])
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


def setup_logging():
    """配置结构化日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
        ]
    )
    
    # 配置不同模块的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


class APIVersionMiddleware:
    """API版本中间件，在响应头中添加版本信息"""
    
    def __init__(self, app: FastAPI, version: str = "v1"):
        self.app = app
        self.version = version
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append([b"x-api-version", self.version.encode()])
                    message["headers"] = headers
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)