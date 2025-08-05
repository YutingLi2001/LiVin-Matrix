"""
Pydantic 模式定义
"""

from .daily_record import (
    DailyRecordSummary,
    UserDailyRecord,
    UserDailyRecordCreate,
    UserDailyRecordUpdate,
    WorkoutSession,
    WorkoutSessionCreate,
    WorkoutSessionUpdate,
)
from .user import User, UserCreate, UserUpdate, UserWithRecords

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserWithRecords",
    "UserDailyRecord",
    "UserDailyRecordCreate",
    "UserDailyRecordUpdate",
    "DailyRecordSummary",
    "WorkoutSession",
    "WorkoutSessionCreate",
    "WorkoutSessionUpdate",
]
