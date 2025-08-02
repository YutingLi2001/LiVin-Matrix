"""
运动训练记录模型
"""

from sqlalchemy import Column, Integer, String, Time, ForeignKey, CheckConstraint, Computed
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import BaseModel


class WorkoutSession(BaseModel):
    """
    运动训练记录模型 - 支持分时段记录
    """
    __tablename__ = "workout_sessions"
    
    # 关联信息
    user_daily_record_id = Column(
        Integer, 
        ForeignKey("user_daily_records.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # 训练基本信息
    workout_type = Column(
        String(20), 
        nullable=False, 
        comment="训练类型: strength/cardio"
    )
    cardio_type = Column(
        String(20), 
        nullable=True, 
        comment="有氧类型: running/cycling/swimming/hiit/machine/other"
    )
    
    # 时间信息
    start_time = Column(Time, nullable=False, comment="训练开始时间")
    end_time = Column(Time, nullable=False, comment="训练结束时间")
    
    # 训练质量评分
    intensity = Column(Integer, nullable=False, comment="训练强度 1-10")
    feeling = Column(Integer, nullable=False, comment="训练感受 1-10")
    
    # 关系映射
    daily_record = relationship("UserDailyRecord", back_populates="workout_sessions")
    
    # 约束条件
    __table_args__ = (
        # 训练类型检查约束
        CheckConstraint(
            "workout_type IN ('strength', 'cardio')", 
            name='workout_type_valid'
        ),
        
        # 有氧训练类型检查约束
        CheckConstraint(
            "cardio_type IS NULL OR cardio_type IN ('running', 'cycling', 'swimming', 'hiit', 'machine', 'other')", 
            name='cardio_type_valid'
        ),
        
        # 强度和感受评分检查约束
        CheckConstraint('intensity >= 1 AND intensity <= 10', name='intensity_range'),
        CheckConstraint('feeling >= 1 AND feeling <= 10', name='feeling_range'),
        
        # 时间逻辑检查约束
        CheckConstraint('end_time > start_time', name='time_logic_valid'),
        
        # 有氧训练必须指定类型
        CheckConstraint(
            "(workout_type = 'cardio' AND cardio_type IS NOT NULL) OR workout_type = 'strength'",
            name='cardio_type_required'
        )
    )
    
    @property
    def duration_minutes(self):
        """
        计算训练时长（分钟）
        """
        if self.start_time and self.end_time:
            # 将时间转换为分钟数进行计算
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            
            # 处理跨日情况（如23:30开始，00:30结束）
            if end_minutes < start_minutes:
                end_minutes += 24 * 60
                
            return end_minutes - start_minutes
        return 0
    
    def __repr__(self):
        return f"<WorkoutSession(id={self.id}, type='{self.workout_type}', duration={self.duration_minutes}min)>"