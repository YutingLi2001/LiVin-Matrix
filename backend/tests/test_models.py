"""
数据库模型单元测试
"""

from datetime import date, datetime, time
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models import User, UserDailyRecord, WorkoutSession

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        auth0_user_id="auth0|test123",
        email="test@example.com",
        username="testuser",
        timezone="Asia/Shanghai",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestUserModel:
    """用户模型测试"""

    def test_create_user(self, db_session):
        """测试创建用户"""
        user = User(auth0_user_id="auth0|test456", email="user@test.com", username="newuser")
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.auth0_user_id == "auth0|test456"
        assert user.email == "user@test.com"
        assert user.username == "newuser"
        assert user.timezone == "UTC"  # 默认值
        assert user.is_active is True  # 默认值
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_unique_constraints(self, db_session):
        """测试用户唯一约束"""
        # 创建第一个用户
        user1 = User(auth0_user_id="auth0|unique1", email="unique@test.com")
        db_session.add(user1)
        db_session.commit()

        # 尝试创建具有相同auth0_user_id的用户
        user2 = User(auth0_user_id="auth0|unique1", email="different@test.com")  # 重复的auth0_user_id
        db_session.add(user2)

        with pytest.raises(Exception):  # 应该抛出唯一约束异常
            db_session.commit()

    def test_user_repr(self, test_user):
        """测试用户字符串表示"""
        expected = f"<User(id={test_user.id}, email='test@example.com', auth0_id='auth0|test123')>"
        assert str(test_user) == expected


class TestUserDailyRecordModel:
    """每日记录模型测试"""

    def test_create_daily_record(self, db_session, test_user):
        """测试创建每日记录"""
        record = UserDailyRecord(
            user_id=test_user.id,
            record_date=date(2025, 7, 31),
            sleep_quality=8,
            sleep_start_time=time(23, 30),
            sleep_end_time=time(7, 0),
            calories=2000,
            protein=120,
            overall_mood=7,
            deep_work_hours=Decimal("6.5"),
            daily_steps=Decimal("8.5"),
        )
        db_session.add(record)
        db_session.commit()

        assert record.id is not None
        assert record.user_id == test_user.id
        assert record.record_date == date(2025, 7, 31)
        assert record.sleep_quality == 8
        assert record.calories == 2000
        assert record.protein == 120
        assert record.overall_mood == 7
        assert record.deep_work_hours == Decimal("6.5")
        assert record.daily_steps == Decimal("8.5")

    def test_daily_record_constraints(self, db_session, test_user):
        """测试每日记录约束条件"""
        # 测试无效的睡眠质量评分
        record = UserDailyRecord(
            user_id=test_user.id, record_date=date(2025, 7, 31), sleep_quality=11  # 无效值：超过10
        )
        db_session.add(record)

        with pytest.raises(Exception):  # 应该抛出检查约束异常
            db_session.commit()

    def test_user_date_unique_constraint(self, db_session, test_user):
        """测试用户日期唯一约束"""
        # 创建第一条记录
        record1 = UserDailyRecord(
            user_id=test_user.id, record_date=date(2025, 7, 31), sleep_quality=8
        )
        db_session.add(record1)
        db_session.commit()

        # 尝试为同一用户同一天创建另一条记录
        record2 = UserDailyRecord(
            user_id=test_user.id, record_date=date(2025, 7, 31), overall_mood=7  # 相同日期
        )
        db_session.add(record2)

        with pytest.raises(Exception):  # 应该抛出唯一约束异常
            db_session.commit()

    def test_work_environment_constraint(self, db_session, test_user):
        """测试工作环境约束"""
        record = UserDailyRecord(
            user_id=test_user.id,
            record_date=date(2025, 7, 31),
            work_environment="invalid_env",  # 无效的工作环境
        )
        db_session.add(record)

        with pytest.raises(Exception):  # 应该抛出检查约束异常
            db_session.commit()

    def test_daily_record_repr(self, db_session, test_user):
        """测试每日记录字符串表示"""
        record = UserDailyRecord(user_id=test_user.id, record_date=date(2025, 7, 31))
        db_session.add(record)
        db_session.commit()

        expected = f"<UserDailyRecord(id={record.id}, user_id={test_user.id}, date='2025-07-31')>"
        assert str(record) == expected


class TestWorkoutSessionModel:
    """运动记录模型测试"""

    @pytest.fixture
    def test_daily_record(self, db_session, test_user):
        """创建测试每日记录"""
        record = UserDailyRecord(user_id=test_user.id, record_date=date(2025, 7, 31))
        db_session.add(record)
        db_session.commit()
        db_session.refresh(record)
        return record

    def test_create_strength_workout(self, db_session, test_daily_record):
        """测试创建力量训练记录"""
        workout = WorkoutSession(
            user_daily_record_id=test_daily_record.id,
            workout_type="strength",
            start_time=time(9, 0),
            end_time=time(10, 30),
            intensity=8,
            feeling=7,
        )
        db_session.add(workout)
        db_session.commit()

        assert workout.id is not None
        assert workout.workout_type == "strength"
        assert workout.cardio_type is None
        assert workout.start_time == time(9, 0)
        assert workout.end_time == time(10, 30)
        assert workout.intensity == 8
        assert workout.feeling == 7

    def test_create_cardio_workout(self, db_session, test_daily_record):
        """测试创建有氧训练记录"""
        workout = WorkoutSession(
            user_daily_record_id=test_daily_record.id,
            workout_type="cardio",
            cardio_type="running",
            start_time=time(6, 0),
            end_time=time(7, 0),
            intensity=6,
            feeling=8,
        )
        db_session.add(workout)
        db_session.commit()

        assert workout.workout_type == "cardio"
        assert workout.cardio_type == "running"

    def test_workout_duration_property(self, db_session, test_daily_record):
        """测试训练时长计算属性"""
        workout = WorkoutSession(
            user_daily_record_id=test_daily_record.id,
            workout_type="strength",
            start_time=time(9, 0),
            end_time=time(10, 30),
            intensity=8,
            feeling=7,
        )
        db_session.add(workout)
        db_session.commit()

        assert workout.duration_minutes == 90  # 1.5小时 = 90分钟

    def test_workout_cross_day_duration(self, db_session, test_daily_record):
        """测试跨日训练时长计算"""
        workout = WorkoutSession(
            user_daily_record_id=test_daily_record.id,
            workout_type="strength",
            start_time=time(23, 30),  # 23:30开始
            end_time=time(0, 30),  # 00:30结束（次日）
            intensity=8,
            feeling=7,
        )
        db_session.add(workout)
        db_session.commit()

        assert workout.duration_minutes == 60  # 1小时 = 60分钟

    def test_workout_constraints(self, db_session, test_daily_record):
        """测试运动记录约束条件"""
        # 测试无效的训练类型
        workout = WorkoutSession(
            user_daily_record_id=test_daily_record.id,
            workout_type="invalid_type",
            start_time=time(9, 0),
            end_time=time(10, 0),
            intensity=8,
            feeling=7,
        )
        db_session.add(workout)

        with pytest.raises(Exception):  # 应该抛出检查约束异常
            db_session.commit()

    def test_cardio_type_required_constraint(self, db_session, test_daily_record):
        """测试有氧训练类型必需约束"""
        # 有氧训练未指定类型
        workout = WorkoutSession(
            user_daily_record_id=test_daily_record.id,
            workout_type="cardio",
            cardio_type=None,  # 有氧训练必须指定类型
            start_time=time(9, 0),
            end_time=time(10, 0),
            intensity=8,
            feeling=7,
        )
        db_session.add(workout)

        with pytest.raises(Exception):  # 应该抛出检查约束异常
            db_session.commit()

    def test_time_logic_constraint(self, db_session, test_daily_record):
        """测试时间逻辑约束"""
        # 结束时间早于开始时间
        workout = WorkoutSession(
            user_daily_record_id=test_daily_record.id,
            workout_type="strength",
            start_time=time(10, 0),
            end_time=time(9, 0),  # 结束时间早于开始时间
            intensity=8,
            feeling=7,
        )
        db_session.add(workout)

        with pytest.raises(Exception):  # 应该抛出检查约束异常
            db_session.commit()

    def test_workout_repr(self, db_session, test_daily_record):
        """测试运动记录字符串表示"""
        workout = WorkoutSession(
            user_daily_record_id=test_daily_record.id,
            workout_type="strength",
            start_time=time(9, 0),
            end_time=time(10, 30),
            intensity=8,
            feeling=7,
        )
        db_session.add(workout)
        db_session.commit()

        expected = f"<WorkoutSession(id={workout.id}, type='strength', duration=90min)>"
        assert str(workout) == expected


class TestModelRelationships:
    """模型关系测试"""

    def test_user_daily_records_relationship(self, db_session, test_user):
        """测试用户和每日记录的关系"""
        # 创建两条每日记录
        record1 = UserDailyRecord(user_id=test_user.id, record_date=date(2025, 7, 30))
        record2 = UserDailyRecord(user_id=test_user.id, record_date=date(2025, 7, 31))
        db_session.add_all([record1, record2])
        db_session.commit()

        # 通过用户访问每日记录
        db_session.refresh(test_user)
        assert len(test_user.daily_records) == 2
        assert record1 in test_user.daily_records
        assert record2 in test_user.daily_records

    def test_daily_record_workout_sessions_relationship(self, db_session, test_user):
        """测试每日记录和运动记录的关系"""
        # 创建每日记录
        daily_record = UserDailyRecord(user_id=test_user.id, record_date=date(2025, 7, 31))
        db_session.add(daily_record)
        db_session.commit()
        db_session.refresh(daily_record)

        # 创建两条运动记录
        workout1 = WorkoutSession(
            user_daily_record_id=daily_record.id,
            workout_type="strength",
            start_time=time(9, 0),
            end_time=time(10, 0),
            intensity=8,
            feeling=7,
        )
        workout2 = WorkoutSession(
            user_daily_record_id=daily_record.id,
            workout_type="cardio",
            cardio_type="running",
            start_time=time(18, 0),
            end_time=time(19, 0),
            intensity=6,
            feeling=8,
        )
        db_session.add_all([workout1, workout2])
        db_session.commit()

        # 通过每日记录访问运动记录
        db_session.refresh(daily_record)
        assert len(daily_record.workout_sessions) == 2
        assert workout1 in daily_record.workout_sessions
        assert workout2 in daily_record.workout_sessions

    def test_cascade_delete(self, db_session, test_user):
        """测试级联删除"""
        # 创建每日记录和运动记录
        daily_record = UserDailyRecord(user_id=test_user.id, record_date=date(2025, 7, 31))
        db_session.add(daily_record)
        db_session.commit()
        db_session.refresh(daily_record)

        workout = WorkoutSession(
            user_daily_record_id=daily_record.id,
            workout_type="strength",
            start_time=time(9, 0),
            end_time=time(10, 0),
            intensity=8,
            feeling=7,
        )
        db_session.add(workout)
        db_session.commit()

        # 删除用户，应该级联删除每日记录和运动记录
        db_session.delete(test_user)
        db_session.commit()

        # 验证记录被删除
        assert db_session.query(UserDailyRecord).count() == 0
        assert db_session.query(WorkoutSession).count() == 0

    def test_boundary_values(self, db_session, test_user):
        """测试边界值"""
        # 测试最大值
        record = UserDailyRecord(
            user_id=test_user.id,
            record_date=date(2025, 7, 31),
            sleep_quality=10,  # 最大值
            calories=5000,  # 最大值
            daily_steps=Decimal("50.0"),  # 最大值
            deep_work_hours=Decimal("24.0"),  # 最大值
        )
        db_session.add(record)
        db_session.commit()

        assert record.sleep_quality == 10
        assert record.calories == 5000
        assert record.daily_steps == Decimal("50.0")
        assert record.deep_work_hours == Decimal("24.0")

    def test_data_integrity_constraints(self, db_session, test_user):
        """测试数据完整性约束"""
        # 测试负值约束
        record = UserDailyRecord(
            user_id=test_user.id,
            record_date=date(2025, 7, 31),
            active_breaks=0,  # 边界值：0是允许的
            initiated_social=0,  # 边界值：0是允许的
            responded_social=0,  # 边界值：0是允许的
        )
        db_session.add(record)
        db_session.commit()

        assert record.active_breaks == 0
        assert record.initiated_social == 0
        assert record.responded_social == 0
