# E2S6: 数据持久化和基础展示

## 任务概述

**任务ID**: E2S6  
**任务标题**: 数据持久化和基础展示  
**所属Epic**: Epic 2 - 数据管理核心  
**预估时间**: 2天  
**优先级**: 高  

## 任务目标

作为用户，我希望我的数据能够安全保存并能查看历史记录，以便跟踪长期趋势。实现完整的6维度数据持久化API，历史数据展示和编辑功能，以及基础的数据统计展示。

## 详细的验收标准

### 1. 所有6维度数据的后端API完整实现（POST/GET/PUT）
- [ ] POST /api/v1/daily-records：创建新的每日记录
- [ ] GET /api/v1/daily-records：获取用户历史记录(支持分页和日期筛选)
- [ ] GET /api/v1/daily-records/{date}：获取特定日期的记录
- [ ] PUT /api/v1/daily-records/{date}：更新特定日期的记录
- [ ] DELETE /api/v1/daily-records/{date}：删除特定日期的记录
- [ ] API支持部分更新：允许只更新某些维度的数据

### 2. 数据完整性验证和错误处理
- [ ] 请求数据验证：Pydantic模型验证所有输入
- [ ] 数据库约束检查：外键、唯一性、数值范围验证
- [ ] 事务处理：确保数据写入的原子性
- [ ] 错误响应标准化：详细的错误信息和错误代码
- [ ] 并发控制：防止同一日期数据的并发写入冲突
- [ ] 数据备份：关键操作前的数据快照

### 3. 历史数据列表展示页面（按日期倒序）
- [ ] 历史记录页面：显示用户所有历史数据
- [ ] 日期倒序排列：最新数据在顶部
- [ ] 数据卡片展示：每日数据以卡片形式展示
- [ ] 6维度概览：每个卡片显示6维度的关键指标
- [ ] 分页加载：支持大量历史数据的分页显示
- [ ] 搜索和筛选：按日期范围筛选历史记录

### 4. 历史数据编辑功能，支持回溯修改
- [ ] 编辑入口：历史记录卡片的编辑按钮
- [ ] 编辑模式：复用数据录入组件进行编辑
- [ ] 数据预填充：编辑时显示历史数据
- [ ] 修改确认：编辑完成后的确认机制
- [ ] 修改历史：记录数据修改的时间戳和变更内容
- [ ] 权限控制：只能编辑自己的数据

### 5. 基础的数据统计展示（最近7天平均值等）
- [ ] 7天统计摘要：最近7天各维度平均值
- [ ] 趋势指示器：相比上周的变化趋势（上升/下降/持平）
- [ ] 数据完整度：7天内数据记录的完整性统计
- [ ] 关键洞察：基于7天数据的简单分析
- [ ] 可视化图表：简单的趋势线图或柱状图
- [ ] 统计数据缓存：提高统计查询性能

## 技术实现要点

### 后端API实现
```python
# app/routers/daily_records.py
from fastapi import APIRouter, Depends, HTTPException
from app.models.daily_record import DailyRecordCreate, DailyRecordUpdate, DailyRecordResponse
from app.services.daily_record_service import DailyRecordService

router = APIRouter()

@router.post("/daily-records", response_model=APIResponse[DailyRecordResponse])
async def create_daily_record(
    record: DailyRecordCreate,
    current_user: User = Depends(get_current_user),
    service: DailyRecordService = Depends()
):
    try:
        created_record = await service.create_record(current_user.id, record)
        return APIResponse(
            success=True,
            data=created_record,
            message="日常记录创建成功"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/daily-records", response_model=APIResponse[List[DailyRecordResponse]])
async def get_daily_records(
    skip: int = 0,
    limit: int = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    service: DailyRecordService = Depends()
):
    records = await service.get_user_records(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date
    )
    return APIResponse(success=True, data=records)
```

### 数据模型定义
```python
# app/models/daily_record.py
from pydantic import BaseModel, validator
from datetime import date, time
from typing import Optional, List

class DailyRecordBase(BaseModel):
    record_date: date
    
    # 睡眠维度
    sleep_start_time: Optional[time]
    sleep_end_time: Optional[time] 
    sleep_quality: Optional[int]
    wake_clarity: Optional[int]
    
    # 饮食维度
    calories: Optional[int]
    protein: Optional[int]
    fat: Optional[int]
    carbohydrates: Optional[int]
    
    # 运动维度
    total_workout_duration: Optional[int]
    daily_steps: Optional[float]
    
    # 情绪维度
    overall_mood: Optional[int]
    stress_level: Optional[int]
    anxiety_level: Optional[int]
    energy_level: Optional[int]
    
    # 工作效率维度
    deep_work_hours: Optional[float]
    active_breaks: Optional[int]
    focus_quality: Optional[int]
    task_completion: Optional[int]
    work_satisfaction: Optional[int]
    work_environment: Optional[str]
    
    # 社交维度
    initiated_social: Optional[int]
    responded_social: Optional[int]
    interpersonal_satisfaction: Optional[int]
    solitude_satisfaction: Optional[int]

    @validator('sleep_quality', 'wake_clarity', 'overall_mood', 'stress_level', 
              'anxiety_level', 'energy_level', 'focus_quality', 'task_completion', 
              'work_satisfaction', 'interpersonal_satisfaction', 'solitude_satisfaction')
    def validate_rating_range(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('评分必须在1-10之间')
        return v

class DailyRecordCreate(DailyRecordBase):
    pass

class DailyRecordUpdate(DailyRecordBase):
    record_date: Optional[date] = None  # 更新时日期可选

class DailyRecordResponse(DailyRecordBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### 前端历史数据组件
```typescript
// components/History/HistoryPage.tsx
const HistoryPage: React.FC = () => {
  const [records, setRecords] = useState<DailyRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<WeeklyStats | null>(null);

  useEffect(() => {
    loadHistoryData();
    loadWeeklyStats();
  }, []);

  const loadHistoryData = async () => {
    try {
      const response = await api.get('/daily-records?limit=30');
      setRecords(response.data);
    } catch (error) {
      console.error('加载历史数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="history-page">
      <div className="page-header">
        <h1>历史记录</h1>
        <WeeklyStatsCard stats={stats} />
      </div>
      
      <div className="records-list">
        {records.map(record => (
          <HistoryRecordCard
            key={record.id}
            record={record}
            onEdit={(record) => openEditModal(record)}
            onDelete={(id) => handleDelete(id)}
          />
        ))}
      </div>
      
      {loading && <LoadingSpinner />}
    </div>
  );
};
```

## 依赖关系

**前置依赖**: E2S2-E2S5 (各维度数据录入) - 需要完整的数据结构  
**后续任务**: Epic 3 - 矩阵分析功能需要历史数据

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 6维度数据API功能完整
- [ ] 数据验证和错误处理完善
- [ ] 历史数据展示和编辑功能正常
- [ ] 基础统计功能准确
- [ ] API性能满足要求(<500ms)
- [ ] 数据安全和完整性保障

---

**任务负责人**: [待分配]  
**创建时间**: 2024年  
**最后更新**: 2024年