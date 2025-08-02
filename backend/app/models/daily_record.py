"""
每日记录相关模型
"""

from sqlalchemy import Column, Integer, Date, Time, String, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.types import Numeric as Decimal
from sqlalchemy.orm import relationship

from .base import BaseModel


class UserDailyRecord(BaseModel):
    """
    用户每日记录模型 - 包含6个维度的所有数据
    """
    __tablename__ = "user_daily_records"
    
    # 基础信息
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    record_date = Column(Date, nullable=False, index=True)
    
    # 睡眠维度
    sleep_start_time = Column(Time, nullable=True, comment="就寝时间")
    sleep_end_time = Column(Time, nullable=True, comment="起床时间")
    sleep_quality = Column(Integer, nullable=True, comment="睡眠质量评分 1-10")
    wake_clarity = Column(Integer, nullable=True, comment="醒来时的清醒度 1-10")
    
    # 饮食维度
    calories = Column(Integer, nullable=True, comment="总热量摄入 0-5000")
    protein = Column(Integer, nullable=True, comment="蛋白质克数 0-500")
    fat = Column(Integer, nullable=True, comment="脂肪克数 0-500")
    carbohydrates = Column(Integer, nullable=True, comment="碳水化合物克数 0-1000")
    
    # 运动维度
    total_workout_duration = Column(Integer, nullable=True, comment="总训练时长（分钟）")
    daily_steps = Column(Decimal(4, 1), nullable=True, comment="每日步数（千步）")
    
    # 情绪维度
    overall_mood = Column(Integer, nullable=True, comment="整体心情评分 1-10")
    stress_level = Column(Integer, nullable=True, comment="压力水平 1-10")
    anxiety_level = Column(Integer, nullable=True, comment="焦虑水平 1-10")
    energy_level = Column(Integer, nullable=True, comment="精力水平 1-10")
    
    # 工作效率维度
    deep_work_hours = Column(Decimal(3, 1), nullable=True, comment="深度工作时长 0-24")
    active_breaks = Column(Integer, nullable=True, comment="主动休息次数")
    focus_quality = Column(Integer, nullable=True, comment="专注质量评分 1-10")
    task_completion = Column(Integer, nullable=True, comment="任务完成度评分 1-10")
    work_satisfaction = Column(Integer, nullable=True, comment="工作满意度评分 1-10")
    work_environment = Column(String(20), nullable=True, comment="工作环境: home/office/cafe/mixed")
    
    # 社交维度
    initiated_social = Column(Integer, nullable=True, comment="发起社交互动次数")
    responded_social = Column(Integer, nullable=True, comment="响应社交互动次数")
    interpersonal_satisfaction = Column(Integer, nullable=True, comment="人际关系满意度 1-10")
    solitude_satisfaction = Column(Integer, nullable=True, comment="独处时光满意度 1-10")
    
    # 关系映射
    user = relationship("User", back_populates="daily_records")
    workout_sessions = relationship("WorkoutSession", back_populates="daily_record", cascade="all, delete-orphan")
    
    # 约束条件
    __table_args__ = (
        # 用户每日记录唯一性约束
        UniqueConstraint('user_id', 'record_date', name='_user_date_uc'),
        
        # 睡眠质量检查约束
        CheckConstraint('sleep_quality >= 1 AND sleep_quality <= 10', name='sleep_quality_range'),
        CheckConstraint('wake_clarity >= 1 AND wake_clarity <= 10', name='wake_clarity_range'),
        
        # 饮食数据检查约束
        CheckConstraint('calories >= 0 AND calories <= 5000', name='calories_range'),
        CheckConstraint('protein >= 0 AND protein <= 500', name='protein_range'),
        CheckConstraint('fat >= 0 AND fat <= 500', name='fat_range'),
        CheckConstraint('carbohydrates >= 0 AND carbohydrates <= 1000', name='carbohydrates_range'),
        
        # 运动数据检查约束
        CheckConstraint('total_workout_duration >= 0', name='workout_duration_positive'),
        CheckConstraint('daily_steps >= 0 AND daily_steps <= 50.0', name='daily_steps_range'),
        
        # 情绪数据检查约束
        CheckConstraint('overall_mood >= 1 AND overall_mood <= 10', name='mood_range'),
        CheckConstraint('stress_level >= 1 AND stress_level <= 10', name='stress_range'),
        CheckConstraint('anxiety_level >= 1 AND anxiety_level <= 10', name='anxiety_range'),
        CheckConstraint('energy_level >= 1 AND energy_level <= 10', name='energy_range'),
        
        # 工作效率数据检查约束
        CheckConstraint('deep_work_hours >= 0 AND deep_work_hours <= 24.0', name='deep_work_hours_range'),
        CheckConstraint('active_breaks >= 0', name='active_breaks_positive'),
        CheckConstraint('focus_quality >= 1 AND focus_quality <= 10', name='focus_quality_range'),
        CheckConstraint('task_completion >= 1 AND task_completion <= 10', name='task_completion_range'),
        CheckConstraint('work_satisfaction >= 1 AND work_satisfaction <= 10', name='work_satisfaction_range'),
        CheckConstraint("work_environment IN ('home', 'office', 'cafe', 'mixed')", name='work_environment_valid'),
        
        # 社交数据检查约束
        CheckConstraint('initiated_social >= 0', name='initiated_social_positive'),
        CheckConstraint('responded_social >= 0', name='responded_social_positive'),
        CheckConstraint('interpersonal_satisfaction >= 1 AND interpersonal_satisfaction <= 10', name='interpersonal_satisfaction_range'),
        CheckConstraint('solitude_satisfaction >= 1 AND solitude_satisfaction <= 10', name='solitude_satisfaction_range'),
    )
    
    def __repr__(self):
        return f"<UserDailyRecord(id={self.id}, user_id={self.user_id}, date='{self.record_date}')>"