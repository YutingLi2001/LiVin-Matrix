"""
每日记录相关的Pydantic模式
"""

from datetime import date, time
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator


class WorkoutSessionBase(BaseModel):
    """运动记录基础模式"""
    workout_type: str = Field(..., pattern="^(strength|cardio)$", description="训练类型")
    cardio_type: Optional[str] = Field(None, pattern="^(running|cycling|swimming|hiit|machine|other)$", description="有氧类型")
    start_time: time = Field(..., description="开始时间")
    end_time: time = Field(..., description="结束时间")
    intensity: int = Field(..., ge=1, le=10, description="训练强度 1-10")
    feeling: int = Field(..., ge=1, le=10, description="训练感受 1-10")

    @model_validator(mode='after')
    def validate_workout_session(self):
        """验证运动记录的业务逻辑"""
        # 验证有氧训练必须指定类型
        if self.workout_type == 'cardio' and self.cardio_type is None:
            raise ValueError('有氧训练必须指定cardio_type')
        if self.workout_type == 'strength' and self.cardio_type is not None:
            raise ValueError('力量训练不应该指定cardio_type')
        
        # 验证时间逻辑
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError('结束时间必须晚于开始时间')
        
        return self


class WorkoutSessionCreate(WorkoutSessionBase):
    """创建运动记录模式"""
    pass


class WorkoutSessionUpdate(BaseModel):
    """更新运动记录模式"""
    workout_type: Optional[str] = Field(None, pattern="^(strength|cardio)$")
    cardio_type: Optional[str] = Field(None, pattern="^(running|cycling|swimming|hiit|machine|other)$")
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    intensity: Optional[int] = Field(None, ge=1, le=10)
    feeling: Optional[int] = Field(None, ge=1, le=10)


class WorkoutSession(WorkoutSessionBase):
    """运动记录完整模式"""
    id: int
    user_daily_record_id: int
    duration_minutes: int = Field(..., description="训练时长（分钟）")

    class Config:
        from_attributes = True


class UserDailyRecordBase(BaseModel):
    """每日记录基础模式"""
    record_date: date = Field(..., description="记录日期")
    
    # 睡眠维度
    sleep_start_time: Optional[time] = Field(None, description="就寝时间")
    sleep_end_time: Optional[time] = Field(None, description="起床时间")
    sleep_quality: Optional[int] = Field(None, ge=1, le=10, description="睡眠质量 1-10")
    wake_clarity: Optional[int] = Field(None, ge=1, le=10, description="醒来清醒度 1-10")
    
    # 饮食维度
    calories: Optional[int] = Field(None, ge=0, le=5000, description="总热量 0-5000")
    protein: Optional[int] = Field(None, ge=0, le=500, description="蛋白质克数 0-500")
    fat: Optional[int] = Field(None, ge=0, le=500, description="脂肪克数 0-500")
    carbohydrates: Optional[int] = Field(None, ge=0, le=1000, description="碳水化合物克数 0-1000")
    
    # 运动维度
    total_workout_duration: Optional[int] = Field(None, ge=0, description="总训练时长（分钟）")
    daily_steps: Optional[Decimal] = Field(None, ge=0, le=50.0, description="每日步数（千步）")
    
    # 情绪维度
    overall_mood: Optional[int] = Field(None, ge=1, le=10, description="整体心情 1-10")
    stress_level: Optional[int] = Field(None, ge=1, le=10, description="压力水平 1-10")
    anxiety_level: Optional[int] = Field(None, ge=1, le=10, description="焦虑水平 1-10")
    energy_level: Optional[int] = Field(None, ge=1, le=10, description="精力水平 1-10")
    
    # 工作效率维度
    deep_work_hours: Optional[Decimal] = Field(None, ge=0, le=24.0, description="深度工作时长 0-24")
    active_breaks: Optional[int] = Field(None, ge=0, description="主动休息次数")
    focus_quality: Optional[int] = Field(None, ge=1, le=10, description="专注质量 1-10")
    task_completion: Optional[int] = Field(None, ge=1, le=10, description="任务完成度 1-10")
    work_satisfaction: Optional[int] = Field(None, ge=1, le=10, description="工作满意度 1-10")
    work_environment: Optional[str] = Field(None, pattern="^(home|office|cafe|mixed)$", description="工作环境")
    
    # 社交维度
    initiated_social: Optional[int] = Field(None, ge=0, description="发起社交次数")
    responded_social: Optional[int] = Field(None, ge=0, description="响应社交次数")
    interpersonal_satisfaction: Optional[int] = Field(None, ge=1, le=10, description="人际关系满意度 1-10")
    solitude_satisfaction: Optional[int] = Field(None, ge=1, le=10, description="独处满意度 1-10")


class UserDailyRecordCreate(UserDailyRecordBase):
    """创建每日记录模式"""
    workout_sessions: Optional[List[WorkoutSessionCreate]] = Field(default_factory=list, description="运动记录")


class UserDailyRecordUpdate(BaseModel):
    """更新每日记录模式"""
    # 睡眠维度
    sleep_start_time: Optional[time] = None
    sleep_end_time: Optional[time] = None
    sleep_quality: Optional[int] = Field(None, ge=1, le=10)
    wake_clarity: Optional[int] = Field(None, ge=1, le=10)
    
    # 饮食维度
    calories: Optional[int] = Field(None, ge=0, le=5000)
    protein: Optional[int] = Field(None, ge=0, le=500)
    fat: Optional[int] = Field(None, ge=0, le=500)
    carbohydrates: Optional[int] = Field(None, ge=0, le=1000)
    
    # 运动维度
    total_workout_duration: Optional[int] = Field(None, ge=0)
    daily_steps: Optional[Decimal] = Field(None, ge=0, le=50.0)
    
    # 情绪维度
    overall_mood: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    anxiety_level: Optional[int] = Field(None, ge=1, le=10)
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    
    # 工作效率维度
    deep_work_hours: Optional[Decimal] = Field(None, ge=0, le=24.0)
    active_breaks: Optional[int] = Field(None, ge=0)
    focus_quality: Optional[int] = Field(None, ge=1, le=10)
    task_completion: Optional[int] = Field(None, ge=1, le=10)
    work_satisfaction: Optional[int] = Field(None, ge=1, le=10)
    work_environment: Optional[str] = Field(None, pattern="^(home|office|cafe|mixed)$")
    
    # 社交维度
    initiated_social: Optional[int] = Field(None, ge=0)
    responded_social: Optional[int] = Field(None, ge=0)
    interpersonal_satisfaction: Optional[int] = Field(None, ge=1, le=10)
    solitude_satisfaction: Optional[int] = Field(None, ge=1, le=10)


class UserDailyRecord(UserDailyRecordBase):
    """每日记录完整模式"""
    id: int
    user_id: int
    workout_sessions: List[WorkoutSession] = Field(default_factory=list, description="运动记录")

    class Config:
        from_attributes = True


class DailyRecordSummary(BaseModel):
    """每日记录摘要模式"""
    id: int
    user_id: int
    record_date: date
    has_sleep_data: bool = Field(..., description="是否有睡眠数据")
    has_diet_data: bool = Field(..., description="是否有饮食数据")
    has_workout_data: bool = Field(..., description="是否有运动数据")
    has_mood_data: bool = Field(..., description="是否有情绪数据")
    has_work_data: bool = Field(..., description="是否有工作数据")
    has_social_data: bool = Field(..., description="是否有社交数据")
    workout_sessions_count: int = Field(..., description="运动记录数量")

    class Config:
        from_attributes = True