# E2S2: 睡眠维度数据录入

## 任务概述

**任务ID**: E2S2
**任务标题**: 睡眠维度数据录入
**所属Epic**: Epic 2 - 数据管理核心
**预估时间**: 2天
**优先级**: 高

## 任务目标

作为用户，我希望记录我的睡眠情况，以便了解睡眠对我的影响。实现睡眠维度的完整数据录入功能，包括睡眠时间段选择、睡眠质量和晨起清醒度评分，支持跨午夜睡眠时间的正确处理。

## 详细的验收标准

### 1. 睡眠时间段选择器（开始时间→结束时间）
- [ ] 睡眠开始时间选择器：支持小时和分钟选择
- [ ] 睡眠结束时间选择器：支持小时和分钟选择
- [ ] 时间选择器UI：使用滚轮选择或时间输入框
- [ ] 默认时间设置：23:00 → 07:30（基于PRD推荐）
- [ ] 时间格式支持：24小时制显示
- [ ] 时间选择的快捷按钮：常见睡眠时间模板

### 2. 睡眠质量星级评分组件（1-10分）
- [ ] 星级评分组件：10颗星星，支持点击选择
- [ ] 评分值显示：当前选择的分数数字显示
- [ ] 评分标签：1-3(差)，4-6(一般)，7-8(良好)，9-10(优秀)
- [ ] 鼠标悬停效果：显示对应分数和评价
- [ ] 键盘支持：方向键调整评分，数字键直接设置
- [ ] 重置功能：清除当前评分选择

### 3. 晨起清醒度星级评分组件（1-10分）
- [ ] 独立的星级评分组件（与睡眠质量组件类似）
- [ ] 清醒度评分标签：1-3(昏沉)，4-6(普通)，7-8(清醒)，9-10(精神饱满)
- [ ] 评分组件复用：使用通用的StarRating组件
- [ ] 实时反馈：选择评分后立即显示对应状态描述
- [ ] 默认值处理：未选择时显示提示文本
- [ ] 评分变更动画：平滑的视觉过渡效果

### 4. 跨午夜睡眠时间的正确处理
- [ ] 跨夜逻辑检测：结束时间早于开始时间时自动识别跨夜
- [ ] 睡眠时长计算：正确计算跨午夜的睡眠总时长
- [ ] 时间显示优化：跨夜情况下显示"23:00 → 次日07:30"
- [ ] 数据验证：确保跨夜时间的逻辑正确性
- [ ] 用户提示：跨夜情况下的友好提示信息
- [ ] 边界情况处理：处理特殊时间输入（如24小时睡眠）

### 5. 数据验证：睡眠时长在2-16小时范围内
- [ ] 睡眠时长自动计算：基于开始和结束时间
- [ ] 合理范围验证：睡眠时长必须在2-16小时之间
- [ ] 错误提示显示：超出范围时显示清晰的错误信息
- [ ] 实时验证：时间修改时立即验证并提示
- [ ] 警告阈值：睡眠时长<6小时或>12小时时显示健康提醒
- [ ] 数据提交阻断：验证失败时阻止数据提交

## 技术实现要点

### 睡眠数据模型
```typescript
// types/SleepData.ts
interface SleepData {
  sleepStartTime: string; // HH:MM格式
  sleepEndTime: string;   // HH:MM格式
  sleepQuality: number;   // 1-10
  wakeClarity: number;    // 1-10
  sleepDuration?: number; // 自动计算，分钟
  isCrossNight?: boolean; // 是否跨夜
}

interface SleepValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}
```

### 时间选择器组件
```typescript
// components/SleepEntry/TimeSelector.tsx
interface TimeSelectorProps {
  value: string; // HH:MM
  onChange: (time: string) => void;
  label: string;
  placeholder?: string;
}

const TimeSelector: React.FC<TimeSelectorProps> = ({
  value, onChange, label, placeholder = "00:00"
}) => {
  const [hours, minutes] = value.split(':').map(Number);

  return (
    <div className="time-selector">
      <label className="time-label">{label}</label>
      <div className="time-inputs">
        <select
          value={hours}
          onChange={(e) => updateTime(parseInt(e.target.value), minutes)}
        >
          {Array.from({length: 24}, (_, i) => (
            <option key={i} value={i}>{i.toString().padStart(2, '0')}</option>
          ))}
        </select>
        <span>:</span>
        <select
          value={minutes}
          onChange={(e) => updateTime(hours, parseInt(e.target.value))}
        >
          {[0, 15, 30, 45].map(m => (
            <option key={m} value={m}>{m.toString().padStart(2, '0')}</option>
          ))}
        </select>
      </div>
    </div>
  );
};
```

### 星级评分组件
```typescript
// components/common/StarRating.tsx
interface StarRatingProps {
  value: number;
  onChange: (rating: number) => void;
  maxRating?: number;
  label?: string;
  labels?: Record<number, string>;
}

const StarRating: React.FC<StarRatingProps> = ({
  value, onChange, maxRating = 10, label, labels
}) => {
  const [hoverRating, setHoverRating] = useState(0);

  return (
    <div className="star-rating">
      {label && <label className="rating-label">{label}</label>}
      <div className="stars-container">
        {Array.from({length: maxRating}, (_, i) => {
          const starValue = i + 1;
          return (
            <button
              key={starValue}
              className={`star ${starValue <= (hoverRating || value) ? 'active' : ''}`}
              onClick={() => onChange(starValue)}
              onMouseEnter={() => setHoverRating(starValue)}
              onMouseLeave={() => setHoverRating(0)}
            >
              ★
            </button>
          );
        })}
      </div>
      <div className="rating-text">
        {(hoverRating || value) > 0 && (
          <span>
            {hoverRating || value}/10
            {labels && labels[hoverRating || value] && ` - ${labels[hoverRating || value]}`}
          </span>
        )}
      </div>
    </div>
  );
};
```

### 睡眠时长计算
```typescript
// utils/sleepCalculations.ts
export const calculateSleepDuration = (startTime: string, endTime: string): {
  duration: number; // 分钟
  isCrossNight: boolean;
} => {
  const [startHour, startMin] = startTime.split(':').map(Number);
  const [endHour, endMin] = endTime.split(':').map(Number);

  const startMinutes = startHour * 60 + startMin;
  let endMinutes = endHour * 60 + endMin;

  // 检测跨夜情况
  const isCrossNight = endMinutes <= startMinutes;
  if (isCrossNight) {
    endMinutes += 24 * 60; // 加一天
  }

  const duration = endMinutes - startMinutes;

  return { duration, isCrossNight };
};

export const validateSleepData = (data: SleepData): SleepValidation => {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!data.sleepStartTime || !data.sleepEndTime) {
    errors.push('请设置睡眠开始和结束时间');
  }

  if (data.sleepQuality < 1 || data.sleepQuality > 10) {
    errors.push('睡眠质量评分必须在1-10之间');
  }

  if (data.wakeClarity < 1 || data.wakeClarity > 10) {
    errors.push('晨起清醒度评分必须在1-10之间');
  }

  const { duration } = calculateSleepDuration(data.sleepStartTime, data.sleepEndTime);
  const hours = duration / 60;

  if (hours < 2 || hours > 16) {
    errors.push(`睡眠时长(${hours.toFixed(1)}小时)必须在2-16小时之间`);
  } else if (hours < 6) {
    warnings.push('睡眠时长较短，建议保证充足睡眠');
  } else if (hours > 12) {
    warnings.push('睡眠时长较长，建议检查睡眠质量');
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
};
```

## 依赖关系

**前置依赖**: E2S1 (数据录入界面架构) - 需要卡片组件和状态管理
**后续任务**: E2S6 (数据持久化) - 需要睡眠数据结构

## 预估时间分解

- **第1天**: 时间选择器组件，星级评分组件开发
- **第2天**: 跨夜逻辑处理，数据验证，集成测试

## 风险点和缓解策略

### 风险点
1. **跨夜时间计算复杂**: 时区和日期边界处理可能出错
2. **用户体验**: 时间选择器可能不够直观
3. **数据验证遗漏**: 边界情况的验证逻辑不完整
4. **移动端适配**: 时间选择器在移动设备上的可用性

### 缓解策略
1. 充分测试跨夜场景，使用标准时间处理库
2. 提供多种时间输入方式，包括快捷选择按钮
3. 建立完整的测试用例覆盖各种边界情况
4. 响应式设计确保移动端良好体验

## 验证方法

### 功能验证
1. **时间选择测试**: 各种时间组合的选择和显示
2. **跨夜处理测试**: 23:00-07:00等跨夜时间的正确计算
3. **评分功能测试**: 星级评分的选择和显示
4. **数据验证测试**: 各种无效输入的错误处理
5. **集成测试**: 与主界面的数据流转

### 用户体验验证
- 睡眠数据录入时间 < 30秒
- 界面操作直观，无需说明文档
- 错误提示清晰易懂

### 数据准确性验证
- 跨夜睡眠时长计算准确率 100%
- 数据验证覆盖所有边界情况
- 时间格式转换无精度丢失

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 时间选择器支持各种睡眠时间输入
- [ ] 星级评分组件交互流畅
- [ ] 跨夜睡眠时间正确处理
- [ ] 数据验证完整且用户友好
- [ ] 组件有充分的单元测试
- [ ] 与主界面集成正常
- [ ] 用户体验测试通过

## 睡眠健康参考标准

### 睡眠时长建议
- **成年人**: 7-9小时为最佳睡眠时长
- **警告阈值**: <6小时或>12小时需要关注
- **极限范围**: 2-16小时为系统接受范围

### 睡眠质量评分参考
- **1-3分**: 睡眠质量差，频繁醒来，难以入睡
- **4-6分**: 睡眠质量一般，偶尔醒来
- **7-8分**: 睡眠质量良好，基本连续睡眠
- **9-10分**: 睡眠质量优秀，深度睡眠充足

### 晨起清醒度评分参考
- **1-3分**: 昏沉，需要很长时间清醒
- **4-6分**: 普通，需要一些时间适应
- **7-8分**: 清醒，能较快进入状态
- **9-10分**: 精神饱满，立即精力充沛

## 相关文档

- [睡眠数据模型设计](../睡眠数据模型设计.md)
- [时间处理工具库](../时间处理工具库.md)
- [星级评分组件规范](../星级评分组件规范.md)
- [睡眠健康指导](../睡眠健康指导.md)

---

**任务负责人**: [待分配]
**创建时间**: 2024年
**最后更新**: 2024年
