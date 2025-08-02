# E2S4: 运动维度数据录入

## 任务概述

**任务ID**: E2S4  
**任务标题**: 运动维度数据录入  
**所属Epic**: Epic 2 - 数据管理核心  
**预估时间**: 3天  
**优先级**: 高  

## 任务目标

作为用户，我希望记录我的运动情况，以便分析运动对整体健康的影响。实现运动维度的完整数据录入功能，支持分时段训练记录、多种运动类型和自动时长计算。

## 详细的验收标准

### 1. 分时段训练记录组件，支持添加/删除/编辑训练
- [ ] 训练记录列表展示当日所有训练
- [ ] 添加训练按钮：弹窗或展开新的训练输入表单
- [ ] 删除训练功能：确认删除对话框
- [ ] 编辑训练功能：点击训练记录进入编辑模式
- [ ] 训练排序：按开始时间自动排序显示
- [ ] 空状态处理：无训练时显示友好提示

### 2. 力量训练录入：时间窗口、训练强度、练后感受
- [ ] 力量训练开始时间选择器
- [ ] 力量训练结束时间选择器
- [ ] 训练强度评分：1-10星级评分
- [ ] 练后感受评分：1-10星级评分
- [ ] 训练时长自动计算并显示
- [ ] 力量训练图标和标识

### 3. 有氧训练录入：时间窗口、运动类型、训练强度、练后感受
- [ ] 有氧训练开始/结束时间选择
- [ ] 有氧运动类型下拉选择器
- [ ] 训练强度评分组件（复用星级评分）
- [ ] 练后感受评分组件
- [ ] 不同运动类型的图标显示
- [ ] 运动类型可搜索过滤

### 4. 6种有氧类型选择器（跑步、骑行、游泳、HIIT、器械、其他）
- [ ] 跑步：显示跑步图标，适合的强度描述
- [ ] 骑行：骑行图标，户外/室内区分
- [ ] 游泳：游泳图标，泳池/开放水域
- [ ] HIIT：高强度图标，时间建议
- [ ] 器械有氧：器械图标，椭圆机/跑步机等
- [ ] 其他：通用图标，自定义文本输入

### 5. 总训练时长自动计算，今日步数手动输入
- [ ] 总时长实时计算：所有训练时长之和
- [ ] 今日步数输入框：支持千步单位(如8.5千步)
- [ ] 步数验证：合理范围0-50千步
- [ ] 训练摘要显示：总时长、训练次数、步数
- [ ] 数据一致性检查：时间重叠提醒
- [ ] 运动量总结：基于时长和强度的简单评估

## 技术实现要点

### 运动数据模型
```typescript
interface WorkoutSession {
  id: string;
  type: 'strength' | 'cardio';
  cardioType?: 'running' | 'cycling' | 'swimming' | 'hiit' | 'machine' | 'other';
  startTime: string; // HH:MM
  endTime: string;   // HH:MM
  intensity: number; // 1-10
  feeling: number;   // 1-10
  duration?: number; // 自动计算分钟
}

interface ExerciseData {
  workoutSessions: WorkoutSession[];
  totalWorkoutDuration: number; // 自动计算
  dailySteps: number; // 千步
  recordDate: string;
}
```

### 训练记录组件
```typescript
const WorkoutSessionList: React.FC<{
  sessions: WorkoutSession[];
  onAdd: () => void;
  onEdit: (session: WorkoutSession) => void;
  onDelete: (id: string) => void;
}> = ({ sessions, onAdd, onEdit, onDelete }) => {
  
  const totalDuration = sessions.reduce((sum, session) => sum + (session.duration || 0), 0);
  
  return (
    <div className="workout-sessions">
      <div className="sessions-header">
        <h4>训练记录</h4>
        <button onClick={onAdd} className="add-session-btn">
          + 添加训练
        </button>
      </div>
      
      {sessions.length === 0 ? (
        <div className="empty-state">今日暂无训练记录</div>
      ) : (
        <>
          <div className="sessions-summary">
            总时长: {totalDuration}分钟 | 训练次数: {sessions.length}次
          </div>
          <div className="sessions-list">
            {sessions.map(session => (
              <WorkoutSessionCard
                key={session.id}
                session={session}
                onEdit={() => onEdit(session)}
                onDelete={() => onDelete(session.id)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
};
```

## 相关文档

- [运动数据模型设计](../运动数据模型设计.md)
- [运动健康指导](../运动健康指导.md)

---

**任务负责人**: [待分配]  
**创建时间**: 2024年  
**最后更新**: 2024年