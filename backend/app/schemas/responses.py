"""
统一API响应格式模型
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """错误详情模型"""

    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误信息")
    details: Optional[Dict[str, Any]] = Field(None, description="详细错误信息")


class APIMetadata(BaseModel):
    """API响应元数据"""

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}, use_enum_values=True
    )

    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    version: str = Field(default="v1", description="API版本")
    request_id: Optional[str] = Field(None, description="请求ID")


class APIResponse(BaseModel, Generic[T]):
    """标准API响应格式"""

    success: bool = Field(..., description="请求是否成功")
    data: Optional[T] = Field(None, description="响应数据")
    message: Optional[str] = Field(None, description="响应消息")
    error: Optional[ErrorDetail] = Field(None, description="错误信息")
    metadata: Optional[APIMetadata] = Field(default_factory=APIMetadata, description="元数据")


class APIError(BaseModel):
    """API错误响应格式"""

    success: bool = Field(default=False, description="请求是否成功")
    data: Optional[Any] = Field(default=None, description="响应数据")
    message: str = Field(..., description="错误消息")
    error: ErrorDetail = Field(..., description="详细错误信息")
    metadata: APIMetadata = Field(default_factory=APIMetadata, description="元数据")


class PaginationMeta(BaseModel):
    """分页元数据"""

    page: int = Field(..., description="当前页码", ge=1)
    size: int = Field(..., description="每页大小", ge=1)
    total: int = Field(..., description="总记录数", ge=0)
    pages: int = Field(..., description="总页数", ge=0)
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""

    success: bool = Field(default=True, description="请求是否成功")
    data: List[T] = Field(default_factory=list, description="数据列表")
    message: Optional[str] = Field(None, description="响应消息")
    pagination: PaginationMeta = Field(..., description="分页信息")
    metadata: APIMetadata = Field(default_factory=APIMetadata, description="元数据")


# 响应格式化工具函数
def create_success_response(
    data: Any = None, message: Optional[str] = None, request_id: Optional[str] = None
) -> Dict[str, Any]:
    """创建成功响应"""
    metadata = APIMetadata(request_id=request_id)
    return {
        "success": True,
        "data": data,
        "message": message,
        "error": None,
        "metadata": {
            "timestamp": metadata.timestamp.isoformat(),
            "version": metadata.version,
            "request_id": metadata.request_id,
        },
    }


def create_error_response(
    message: str,
    error_code: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """创建错误响应"""
    metadata = APIMetadata(request_id=request_id)
    error_detail = ErrorDetail(code=error_code, message=message, details=details)
    return {
        "success": False,
        "data": None,
        "message": message,
        "error": error_detail.model_dump(),
        "metadata": {
            "timestamp": metadata.timestamp.isoformat(),
            "version": metadata.version,
            "request_id": metadata.request_id,
        },
    }


def create_paginated_response(
    data: List[Any],
    page: int,
    size: int,
    total: int,
    message: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """创建分页响应"""
    import math

    pages = math.ceil(total / size) if total > 0 else 0
    has_next = page < pages
    has_prev = page > 1

    pagination = PaginationMeta(
        page=page, size=size, total=total, pages=pages, has_next=has_next, has_prev=has_prev
    )

    metadata = APIMetadata(request_id=request_id)

    return {
        "success": True,
        "data": data,
        "message": message,
        "pagination": pagination.model_dump(),
        "metadata": {
            "timestamp": metadata.timestamp.isoformat(),
            "version": metadata.version,
            "request_id": metadata.request_id,
        },
    }


# 常用错误代码常量
class ErrorCodes:
    """标准错误代码"""

    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    INTERNAL_ERROR = "internal_error"
    BAD_REQUEST = "bad_request"
    TOO_MANY_REQUESTS = "too_many_requests"
    SERVICE_UNAVAILABLE = "service_unavailable"
