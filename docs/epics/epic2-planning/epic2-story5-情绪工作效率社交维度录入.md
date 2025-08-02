# E2S5: 情绪、工作效率、社交维度录入

## 任务概述

**任务ID**: E2S5  
**任务标题**: 情绪、工作效率、社交维度录入  
**所属Epic**: Epic 2 - 数据管理核心  
**预估时间**: 3天  
**优先级**: 高  

## 任务目标

作为用户，我希望记录我的情绪状态、工作表现和社交活动，以便全面了解我的生活状态。实现剩余三个维度的数据录入功能，包括情绪评分、工作效率指标和社交活动统计。

## 详细的验收标准

### 1. 情绪维度：4个星级评分（整体心情、压力感、焦虑程度、精力水平）
- [ ] 整体心情评分：1-10星级，带有情绪描述标签
- [ ] 压力感评分：1-10星级，压力程度说明
- [ ] 焦虑程度评分：1-10星级，焦虑状态描述
- [ ] 精力水平评分：1-10星级，精力状态指示
- [ ] 情绪雷达图：4个维度的可视化展示
- [ ] 情绪建议：基于评分提供简单的心理健康建议

### 2. 工作效率维度：数值输入+评分+环境选择组件
- [ ] 深度工作时长：数值输入，小时(可含小数)，范围0-16
- [ ] 主动休息次数：整数输入，范围0-20
- [ ] 专注质量评分：1-10星级评分
- [ ] 任务完成度评分：1-10星级评分
- [ ] 工作满意度评分：1-10星级评分
- [ ] 工作环境选择：单选按钮(家中/办公室/咖啡厅/混合)

### 3. 社交维度：计数输入+星级评分组件
- [ ] 发起社交次数：数值输入，整数，范围0-20
- [ ] 响应社交次数：数值输入，整数，范围0-50
- [ ] 人际满意度评分：1-10星级评分
- [ ] 独处满足度评分：1-10星级评分
- [ ] 社交平衡指示器：发起/响应比例可视化
- [ ] 社交类型标签：可选择社交活动类型

### 4. 工作环境单选组件（家中/办公室/咖啡厅/混合）
- [ ] 环境选项卡片式布局，带图标
- [ ] 家中：居家图标，舒适环境描述
- [ ] 办公室：办公图标，正式环境描述
- [ ] 咖啡厅：咖啡图标，社交环境描述
- [ ] 混合：混合图标，多场所工作描述
- [ ] 选中状态视觉反馈
- [ ] 环境对效率的影响提示

### 5. 快捷模板支持（高效日、普通日、休息日等）
- [ ] 高效日模板：高工作效率，好心情，适度社交
- [ ] 普通日模板：中等各项指标的平衡配置
- [ ] 休息日模板：低工作强度，高休息满足度
- [ ] 压力日模板：高压力，低心情的真实记录
- [ ] 一键应用模板功能
- [ ] 自定义模板保存功能

## 技术实现要点

### 数据模型
```typescript
// 情绪维度
interface MoodData {
  overallMood: number;      // 1-10 整体心情
  stressLevel: number;      // 1-10 压力感
  anxietyLevel: number;     // 1-10 焦虑程度
  energyLevel: number;      // 1-10 精力水平
}

// 工作效率维度
interface ProductivityData {
  deepWorkHours: number;        // 深度工作时长(小时)
  activeBreaks: number;         // 主动休息次数
  focusQuality: number;         // 1-10 专注质量
  taskCompletion: number;       // 1-10 任务完成度
  workSatisfaction: number;     // 1-10 工作满意度
  workEnvironment: 'home' | 'office' | 'cafe' | 'mixed';
}

// 社交维度
interface SocialData {
  initiatedSocial: number;           // 发起社交次数
  respondedSocial: number;           // 响应社交次数
  interpersonalSatisfaction: number; // 1-10 人际满意度
  solitudeSatisfaction: number;      // 1-10 独处满足度
}
```

### 多维度评分组件
```typescript
const MultiDimensionRating: React.FC<{
  dimensions: Array<{
    key: string;
    label: string;
    value: number;
    onChange: (value: number) => void;
    labels?: Record<number, string>;
  }>;
  title: string;
}> = ({ dimensions, title }) => {
  return (
    <div className="multi-dimension-rating">
      <h4>{title}</h4>
      <div className="dimensions-grid">
        {dimensions.map(dim => (
          <div key={dim.key} className="dimension-item">
            <StarRating
              label={dim.label}
              value={dim.value}
              onChange={dim.onChange}
              labels={dim.labels}
            />
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 工作环境选择器
```typescript
const WorkEnvironmentSelector: React.FC<{
  value: string;
  onChange: (env: string) => void;
}> = ({ value, onChange }) => {
  
  const environments = [
    { id: 'home', label: '家中', icon: '🏠', description: '舒适自在的工作环境' },
    { id: 'office', label: '办公室', icon: '🏢', description: '专业正式的工作场所' },
    { id: 'cafe', label: '咖啡厅', icon: '☕', description: '轻松社交的工作环境' },
    { id: 'mixed', label: '混合', icon: '🔄', description: '多个场所切换工作' }
  ];

  return (
    <div className="work-environment-selector">
      <label>工作环境</label>
      <div className="environment-options">
        {environments.map(env => (
          <button
            key={env.id}
            className={`env-option ${value === env.id ? 'selected' : ''}`}
            onClick={() => onChange(env.id)}
          >
            <span className="env-icon">{env.icon}</span>
            <span className="env-label">{env.label}</span>
            <span className="env-desc">{env.description}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
```

## 依赖关系

**前置依赖**: E2S1 (数据录入界面架构) - 需要卡片组件和星级评分组件  
**后续任务**: E2S6 (数据持久化) - 需要完整的数据结构

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 三个维度的数据录入功能完整
- [ ] 快捷模板功能正常工作
- [ ] 数据验证和用户体验良好
- [ ] 组件复用度高，代码质量优秀

---

**任务负责人**: [待分配]  
**创建时间**: 2024年  
**最后更新**: 2024年