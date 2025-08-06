"""
每日记录服务业务逻辑
"""

from datetime import date, datetime, timedelta
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..models import UserDailyRecord, WorkoutSession
from ..schemas import (
    UserDailyRecordCreate,
    UserDailyRecordUpdate,
    WorkoutSessionCreate,
)


class DailyRecordService:
    """每日记录服务类"""

    @staticmethod
    def get_by_user_and_date(db: Session, user_id: int, record_date: date) -> Optional[UserDailyRecord]:
        """根据用户ID和日期获取记录"""
        return (
            db.query(UserDailyRecord)
            .filter(
                UserDailyRecord.user_id == user_id,
                UserDailyRecord.record_date == record_date,
            )
            .first()
        )

    @staticmethod
    def get_user_records(
        db: Session,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 30,
    ) -> List[UserDailyRecord]:
        """获取用户的记录列表"""
        query = db.query(UserDailyRecord).filter(UserDailyRecord.user_id == user_id)

        if start_date:
            query = query.filter(UserDailyRecord.record_date >= start_date)
        if end_date:
            query = query.filter(UserDailyRecord.record_date <= end_date)

        return query.order_by(UserDailyRecord.record_date.desc()).limit(limit).all()

    @staticmethod
    def create_or_update(db: Session, user_id: int, record_data: UserDailyRecordCreate) -> UserDailyRecord:
        """创建或更新每日记录"""
        existing_record = DailyRecordService.get_by_user_and_date(db, user_id, record_data.record_date)

        if existing_record:
            # 更新现有记录
            return DailyRecordService._update_record(db, existing_record, record_data)
        else:
            # 创建新记录
            return DailyRecordService._create_record(db, user_id, record_data)

    @staticmethod
    def _create_record(db: Session, user_id: int, record_data: UserDailyRecordCreate) -> UserDailyRecord:
        """创建新的每日记录"""
        try:
            # 创建主记录
            db_record = UserDailyRecord(
                user_id=user_id,
                **record_data.model_dump(exclude={"workout_sessions"}),
            )
            db.add(db_record)
            db.flush()  # 获取ID但不提交

            # 创建运动记录
            for workout_data in record_data.workout_sessions:
                workout = WorkoutSession(
                    user_daily_record_id=db_record.id,
                    **workout_data.model_dump(),
                )
                db.add(workout)

            db.commit()
            db.refresh(db_record)
            return db_record

        except IntegrityError:
            db.rollback()
            raise ValueError(f"用户{user_id}在{record_data.record_date}的记录已存在")

    @staticmethod
    def _update_record(
        db: Session,
        record: UserDailyRecord,
        record_data: UserDailyRecordCreate,
    ) -> UserDailyRecord:
        """更新现有记录"""
        # 更新主记录字段
        update_data = record_data.model_dump(exclude={"workout_sessions"}, exclude_unset=True)
        for field, value in update_data.items():
            if field != "record_date":  # 日期不能修改
                setattr(record, field, value)

        # 删除现有的运动记录
        db.query(WorkoutSession).filter(WorkoutSession.user_daily_record_id == record.id).delete()

        # 创建新的运动记录
        for workout_data in record_data.workout_sessions:
            workout = WorkoutSession(user_daily_record_id=record.id, **workout_data.model_dump())
            db.add(workout)

        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def add_workout_session(db: Session, record_id: int, workout_data: WorkoutSessionCreate) -> WorkoutSession:
        """为记录添加运动会话"""
        workout = WorkoutSession(user_daily_record_id=record_id, **workout_data.model_dump())
        db.add(workout)
        db.commit()
        db.refresh(workout)
        return workout

    @staticmethod
    def get_recent_trends(db: Session, user_id: int, days: int = 7) -> dict:
        """获取用户最近的趋势数据"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        records = DailyRecordService.get_user_records(db, user_id, start_date, end_date, limit=days)

        if not records:
            return {}

        # 计算平均值和趋势
        total_records = len(records)
        trends = {
            "period_days": days,
            "record_count": total_records,
            "averages": {},
            "latest_record_date": max(r.record_date for r in records) if records else None,
        }

        # 计算各维度平均值
        numeric_fields = [
            "sleep_quality",
            "wake_clarity",
            "calories",
            "protein",
            "fat",
            "carbohydrates",
            "total_workout_duration",
            "daily_steps",
            "overall_mood",
            "stress_level",
            "anxiety_level",
            "energy_level",
            "deep_work_hours",
            "active_breaks",
            "focus_quality",
            "task_completion",
            "work_satisfaction",
            "initiated_social",
            "responded_social",
            "interpersonal_satisfaction",
            "solitude_satisfaction",
        ]

        for field in numeric_fields:
            values = [getattr(r, field) for r in records if getattr(r, field) is not None]
            if values:
                trends["averages"][field] = sum(values) / len(values)

        return trends

    @staticmethod
    def delete_record(db: Session, user_id: int, record_date: date) -> bool:
        """删除指定日期的记录"""
        record = DailyRecordService.get_by_user_and_date(db, user_id, record_date)
        if not record:
            return False

        db.delete(record)  # 级联删除相关的运动记录
        db.commit()
        return True
