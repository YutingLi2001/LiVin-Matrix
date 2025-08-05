"""
测试统一响应格式模型
"""

from datetime import datetime
from typing import List

import pytest

from app.schemas.responses import (
    APIError,
    APIMetadata,
    APIResponse,
    ErrorCodes,
    ErrorDetail,
    PaginatedResponse,
    create_error_response,
    create_paginated_response,
    create_success_response,
)


class TestAPIResponse:
    """测试API响应格式"""

    def test_api_response_success(self):
        """测试成功响应"""
        response = APIResponse[dict](success=True, data={"test": "data"}, message="Success")

        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.message == "Success"
        assert response.error is None
        assert response.metadata is not None

    def test_api_response_error(self):
        """测试错误响应"""
        error_detail = ErrorDetail(
            code="test_error", message="Test error message", details={"field": "invalid"}
        )

        response = APIResponse[None](
            success=False, data=None, message="Error occurred", error=error_detail
        )

        assert response.success is False
        assert response.data is None
        assert response.message == "Error occurred"
        assert response.error.code == "test_error"
        assert response.error.message == "Test error message"
        assert response.error.details == {"field": "invalid"}


class TestAPIError:
    """测试API错误响应"""

    def test_api_error_creation(self):
        """测试错误响应创建"""
        error_detail = ErrorDetail(
            code=ErrorCodes.VALIDATION_ERROR, message="Invalid input"
        )

        error_response = APIError(
            message="Validation failed", error=error_detail
        )

        assert error_response.success is False
        assert error_response.data is None
        assert error_response.message == "Validation failed"
        assert error_response.error.code == ErrorCodes.VALIDATION_ERROR


class TestPaginatedResponse:
    """测试分页响应"""

    def test_paginated_response(self):
        """测试分页响应创建"""
        from app.schemas.responses import PaginationMeta

        pagination = PaginationMeta(
            page=1, size=10, total=25, pages=3, has_next=True, has_prev=False
        )

        response = PaginatedResponse[dict](
            data=[{"id": 1}, {"id": 2}],
            pagination=pagination,
            message="Data retrieved"
        )

        assert response.success is True
        assert len(response.data) == 2
        assert response.pagination.page == 1
        assert response.pagination.total == 25
        assert response.pagination.has_next is True
        assert response.pagination.has_prev is False


class TestResponseHelpers:
    """测试响应格式化工具函数"""

    def test_create_success_response(self):
        """测试创建成功响应"""
        response = create_success_response(
            data={"user_id": 123}, message="User created", request_id="req-123"
        )

        assert response["success"] is True
        assert response["data"] == {"user_id": 123}
        assert response["message"] == "User created"
        assert response["error"] is None
        assert response["metadata"]["request_id"] == "req-123"
        assert "timestamp" in response["metadata"]
        assert response["metadata"]["version"] == "v1"

    def test_create_error_response(self):
        """测试创建错误响应"""
        response = create_error_response(
            message="User not found",
            error_code=ErrorCodes.NOT_FOUND,
            details={"user_id": 123},
            request_id="req-456",
        )

        assert response["success"] is False
        assert response["data"] is None
        assert response["message"] == "User not found"
        assert response["error"]["code"] == ErrorCodes.NOT_FOUND
        assert response["error"]["message"] == "User not found"
        assert response["error"]["details"] == {"user_id": 123}
        assert response["metadata"]["request_id"] == "req-456"

    def test_create_paginated_response(self):
        """测试创建分页响应"""
        data = [{"id": i} for i in range(1, 11)]

        response = create_paginated_response(
            data=data,
            page=2,
            size=10,
            total=45,
            message="Users retrieved",
            request_id="req-789"
        )

        assert response["success"] is True
        assert len(response["data"]) == 10
        assert response["message"] == "Users retrieved"
        assert response["pagination"]["page"] == 2
        assert response["pagination"]["size"] == 10
        assert response["pagination"]["total"] == 45
        assert response["pagination"]["pages"] == 5
        assert response["pagination"]["has_next"] is True
        assert response["pagination"]["has_prev"] is True
        assert response["metadata"]["request_id"] == "req-789"

    def test_create_paginated_response_edge_cases(self):
        """测试分页响应边界情况"""
        # 测试空数据
        response = create_paginated_response(
            data=[], page=1, size=10, total=0
        )

        assert response["pagination"]["pages"] == 0
        assert response["pagination"]["has_next"] is False
        assert response["pagination"]["has_prev"] is False

        # 测试单页数据
        response = create_paginated_response(data=[{"id": 1}], page=1, size=10, total=1)

        assert response["pagination"]["pages"] == 1
        assert response["pagination"]["has_next"] is False
        assert response["pagination"]["has_prev"] is False


class TestErrorCodes:
    """测试错误代码常量"""

    def test_error_codes_constants(self):
        """测试错误代码常量值"""
        assert ErrorCodes.VALIDATION_ERROR == "validation_error"
        assert ErrorCodes.AUTHENTICATION_ERROR == "authentication_error"
        assert ErrorCodes.AUTHORIZATION_ERROR == "authorization_error"
        assert ErrorCodes.NOT_FOUND == "not_found"
        assert ErrorCodes.CONFLICT == "conflict"
        assert ErrorCodes.INTERNAL_ERROR == "internal_error"
        assert ErrorCodes.BAD_REQUEST == "bad_request"
        assert ErrorCodes.TOO_MANY_REQUESTS == "too_many_requests"
        assert ErrorCodes.SERVICE_UNAVAILABLE == "service_unavailable"


class TestAPIMetadata:
    """测试API元数据"""

    def test_metadata_creation(self):
        """测试元数据创建"""
        metadata = APIMetadata(request_id="test-123")

        assert metadata.request_id == "test-123"
        assert metadata.version == "v1"
        assert isinstance(metadata.timestamp, datetime)

    def test_metadata_defaults(self):
        """测试元数据默认值"""
        metadata = APIMetadata()

        assert metadata.request_id is None
        assert metadata.version == "v1"
        assert isinstance(metadata.timestamp, datetime)
