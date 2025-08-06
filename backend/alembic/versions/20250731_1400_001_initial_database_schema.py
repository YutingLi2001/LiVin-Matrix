"""初始数据库结构 - 用户表、每日记录表和运动记录表

Revision ID: 001
Revises:
Create Date: 2025-07-31 14:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    执行数据库升级操作 - 创建所有表
    """
    # 创建用户表
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("auth0_user_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=True),
        sa.Column("timezone", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_auth0_user_id"), "users", ["auth0_user_id"], unique=True)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    # 创建每日记录表
    op.create_table(
        "user_daily_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("record_date", sa.Date(), nullable=False),
        # 睡眠维度
        sa.Column("sleep_start_time", sa.Time(), nullable=True, comment="就寝时间"),
        sa.Column("sleep_end_time", sa.Time(), nullable=True, comment="起床时间"),
        sa.Column("sleep_quality", sa.Integer(), nullable=True, comment="睡眠质量评分 1-10"),
        sa.Column("wake_clarity", sa.Integer(), nullable=True, comment="醒来时的清醒度 1-10"),
        # 饮食维度
        sa.Column("calories", sa.Integer(), nullable=True, comment="总热量摄入 0-5000"),
        sa.Column("protein", sa.Integer(), nullable=True, comment="蛋白质克数 0-500"),
        sa.Column("fat", sa.Integer(), nullable=True, comment="脂肪克数 0-500"),
        sa.Column("carbohydrates", sa.Integer(), nullable=True, comment="碳水化合物克数 0-1000"),
        # 运动维度
        sa.Column(
            "total_workout_duration", sa.Integer(), nullable=True, comment="总训练时长（分钟）"
        ),
        sa.Column(
            "daily_steps",
            sa.Numeric(precision=4, scale=1),
            nullable=True,
            comment="每日步数（千步）",
        ),
        # 情绪维度
        sa.Column("overall_mood", sa.Integer(), nullable=True, comment="整体心情评分 1-10"),
        sa.Column("stress_level", sa.Integer(), nullable=True, comment="压力水平 1-10"),
        sa.Column("anxiety_level", sa.Integer(), nullable=True, comment="焦虑水平 1-10"),
        sa.Column("energy_level", sa.Integer(), nullable=True, comment="精力水平 1-10"),
        # 工作效率维度
        sa.Column(
            "deep_work_hours",
            sa.Numeric(precision=3, scale=1),
            nullable=True,
            comment="深度工作时长 0-24",
        ),
        sa.Column("active_breaks", sa.Integer(), nullable=True, comment="主动休息次数"),
        sa.Column("focus_quality", sa.Integer(), nullable=True, comment="专注质量评分 1-10"),
        sa.Column("task_completion", sa.Integer(), nullable=True, comment="任务完成度评分 1-10"),
        sa.Column("work_satisfaction", sa.Integer(), nullable=True, comment="工作满意度评分 1-10"),
        sa.Column(
            "work_environment",
            sa.String(length=20),
            nullable=True,
            comment="工作环境: home/office/cafe/mixed",
        ),
        # 社交维度
        sa.Column("initiated_social", sa.Integer(), nullable=True, comment="发起社交互动次数"),
        sa.Column("responded_social", sa.Integer(), nullable=True, comment="响应社交互动次数"),
        sa.Column(
            "interpersonal_satisfaction", sa.Integer(), nullable=True, comment="人际关系满意度 1-10"
        ),
        sa.Column(
            "solitude_satisfaction", sa.Integer(), nullable=True, comment="独处时光满意度 1-10"
        ),
        sa.CheckConstraint("active_breaks >= 0", name="active_breaks_positive"),
        sa.CheckConstraint("anxiety_level >= 1 AND anxiety_level <= 10", name="anxiety_range"),
        sa.CheckConstraint("calories >= 0 AND calories <= 5000", name="calories_range"),
        sa.CheckConstraint(
            "carbohydrates >= 0 AND carbohydrates <= 1000", name="carbohydrates_range"
        ),
        sa.CheckConstraint("daily_steps >= 0 AND daily_steps <= 50.0", name="daily_steps_range"),
        sa.CheckConstraint(
            "deep_work_hours >= 0 AND deep_work_hours <= 24.0", name="deep_work_hours_range"
        ),
        sa.CheckConstraint("energy_level >= 1 AND energy_level <= 10", name="energy_range"),
        sa.CheckConstraint("fat >= 0 AND fat <= 500", name="fat_range"),
        sa.CheckConstraint(
            "focus_quality >= 1 AND focus_quality <= 10", name="focus_quality_range"
        ),
        sa.CheckConstraint("initiated_social >= 0", name="initiated_social_positive"),
        sa.CheckConstraint(
            "interpersonal_satisfaction >= 1 AND interpersonal_satisfaction <= 10",
            name="interpersonal_satisfaction_range",
        ),
        sa.CheckConstraint("overall_mood >= 1 AND overall_mood <= 10", name="mood_range"),
        sa.CheckConstraint("protein >= 0 AND protein <= 500", name="protein_range"),
        sa.CheckConstraint("responded_social >= 0", name="responded_social_positive"),
        sa.CheckConstraint(
            "sleep_quality >= 1 AND sleep_quality <= 10", name="sleep_quality_range"
        ),
        sa.CheckConstraint(
            "solitude_satisfaction >= 1 AND solitude_satisfaction <= 10",
            name="solitude_satisfaction_range",
        ),
        sa.CheckConstraint("stress_level >= 1 AND stress_level <= 10", name="stress_range"),
        sa.CheckConstraint(
            "task_completion >= 1 AND task_completion <= 10", name="task_completion_range"
        ),
        sa.CheckConstraint("total_workout_duration >= 0", name="workout_duration_positive"),
        sa.CheckConstraint("wake_clarity >= 1 AND wake_clarity <= 10", name="wake_clarity_range"),
        sa.CheckConstraint(
            "work_environment IN ('home', 'office', 'cafe', 'mixed')", name="work_environment_valid"
        ),
        sa.CheckConstraint(
            "work_satisfaction >= 1 AND work_satisfaction <= 10", name="work_satisfaction_range"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "record_date", name="_user_date_uc"),
    )
    op.create_index(op.f("ix_user_daily_records_id"), "user_daily_records", ["id"], unique=False)
    op.create_index(
        op.f("ix_user_daily_records_record_date"),
        "user_daily_records",
        ["record_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_daily_records_user_id"), "user_daily_records", ["user_id"], unique=False
    )

    # 创建运动记录表
    op.create_table(
        "workout_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("user_daily_record_id", sa.Integer(), nullable=False),
        sa.Column(
            "workout_type",
            sa.String(length=20),
            nullable=False,
            comment="训练类型: strength/cardio",
        ),
        sa.Column(
            "cardio_type",
            sa.String(length=20),
            nullable=True,
            comment="有氧类型: running/cycling/swimming/hiit/machine/other",
        ),
        sa.Column("start_time", sa.Time(), nullable=False, comment="训练开始时间"),
        sa.Column("end_time", sa.Time(), nullable=False, comment="训练结束时间"),
        sa.Column("intensity", sa.Integer(), nullable=False, comment="训练强度 1-10"),
        sa.Column("feeling", sa.Integer(), nullable=False, comment="训练感受 1-10"),
        sa.CheckConstraint(
            "(workout_type = 'cardio' AND cardio_type IS NOT NULL) OR workout_type = 'strength'",
            name="cardio_type_required",
        ),
        sa.CheckConstraint(
            "cardio_type IS NULL OR cardio_type IN ('running', 'cycling', 'swimming', 'hiit', 'machine', 'other')",
            name="cardio_type_valid",
        ),
        sa.CheckConstraint("feeling >= 1 AND feeling <= 10", name="feeling_range"),
        sa.CheckConstraint("intensity >= 1 AND intensity <= 10", name="intensity_range"),
        sa.CheckConstraint("end_time > start_time", name="time_logic_valid"),
        sa.CheckConstraint("workout_type IN ('strength', 'cardio')", name="workout_type_valid"),
        sa.ForeignKeyConstraint(
            ["user_daily_record_id"], ["user_daily_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workout_sessions_id"), "workout_sessions", ["id"], unique=False)
    op.create_index(
        op.f("ix_workout_sessions_user_daily_record_id"),
        "workout_sessions",
        ["user_daily_record_id"],
        unique=False,
    )


def downgrade() -> None:
    """
    执行数据库降级操作 - 删除所有表
    """
    op.drop_index(op.f("ix_workout_sessions_user_daily_record_id"), table_name="workout_sessions")
    op.drop_index(op.f("ix_workout_sessions_id"), table_name="workout_sessions")
    op.drop_table("workout_sessions")

    op.drop_index(op.f("ix_user_daily_records_user_id"), table_name="user_daily_records")
    op.drop_index(op.f("ix_user_daily_records_record_date"), table_name="user_daily_records")
    op.drop_index(op.f("ix_user_daily_records_id"), table_name="user_daily_records")
    op.drop_table("user_daily_records")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_auth0_user_id"), table_name="users")
    op.drop_table("users")
