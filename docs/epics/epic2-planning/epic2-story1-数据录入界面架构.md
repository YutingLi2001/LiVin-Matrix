# E2S1: 数据录入界面架构

## 任务概述

**任务ID**: E2S1  
**任务标题**: 数据录入界面架构  
**所属Epic**: Epic 2 - 数据管理核心  
**预估时间**: 3天  
**优先级**: 高  

## 任务目标

作为用户，我希望有直观的数据录入界面，以便快速记录我的日常生活数据。建立统一的数据录入界面架构，包含6个维度的折叠卡片布局、进度跟踪、自动保存和响应式设计，为后续各维度的数据录入功能提供基础框架。

## 详细的验收标准

### 1. 单页面6个折叠卡片布局实现完成
- [ ] 创建DataEntryPage主页面组件
- [ ] 6个折叠卡片组件：睡眠、饮食、运动、情绪、工作效率、社交
- [ ] 卡片展开/折叠动画效果（使用CSS transition）
- [ ] 卡片状态管理：已完成、进行中、未开始
- [ ] 卡片标题和图标设计符合深色主题
- [ ] 卡片可以按任意顺序展开和填写

### 2. 进度可视化组件（已完成X/6维度，预计剩余时间）
- [ ] ProgressIndicator组件显示整体完成进度
- [ ] 进度条可视化（已完成维度/总维度）
- [ ] 预计剩余时间计算（基于历史填写时间）
- [ ] 实时更新：维度完成时自动更新进度
- [ ] 进度百分比显示和动画效果
- [ ] 完成度颜色编码（红色<50%，黄色50-80%，绿色>80%）

### 3. 自动保存草稿功能，避免数据丢失
- [ ] 表单数据实时保存到localStorage
- [ ] 页面刷新后恢复草稿数据
- [ ] 自动保存状态指示器（"已保存"/"保存中"）
- [ ] 草稿数据过期策略（24小时后清除）
- [ ] 草稿与已提交数据的区分标识
- [ ] 清除草稿功能（用户主动清除或提交后清除）

### 4. 响应式设计，支持桌面和平板设备
- [ ] 桌面端（>1024px）：6个卡片2x3布局
- [ ] 平板端（768-1024px）：6个卡片单列布局
- [ ] 卡片内部组件响应式适配
- [ ] 触摸友好的交互设计（点击区域足够大）
- [ ] 不同屏幕尺寸下的视觉效果测试
- [ ] 横屏和竖屏模式适配

### 5. 页面加载时间小于2秒
- [ ] 组件懒加载实现，只加载当前展开的卡片内容
- [ ] 图片和图标优化，使用WebP格式
- [ ] CSS代码分割，避免阻塞渲染
- [ ] JavaScript代码分割，按需加载
- [ ] 网络请求优化，减少初始加载数据量
- [ ] 性能监控集成，实时监控加载时间

## 技术实现要点

### 主页面组件架构
```typescript
// components/DataEntry/DataEntryPage.tsx
interface DataEntryState {
  sleepData: SleepData;
  nutritionData: NutritionData;
  exerciseData: ExerciseData;
  moodData: MoodData;
  productivityData: ProductivityData;
  socialData: SocialData;
  completedDimensions: string[];
  isDraftMode: boolean;
}

const DataEntryPage: React.FC = () => {
  const [entryState, setEntryState] = useState<DataEntryState>(initialState);
  const [expandedCard, setExpandedCard] = useState<string>('');
  
  // 自动保存逻辑
  useEffect(() => {
    const saveTimer = setTimeout(() => {
      saveDraftToLocalStorage(entryState);
    }, 1000);
    return () => clearTimeout(saveTimer);
  }, [entryState]);

  return (
    <div className="data-entry-container">
      <ProgressIndicator completed={entryState.completedDimensions.length} total={6} />
      <div className="cards-grid">
        {dimensionCards.map(card => (
          <DimensionCard
            key={card.id}
            {...card}
            isExpanded={expandedCard === card.id}
            onToggle={() => setExpandedCard(card.id)}
            data={entryState[card.dataKey]}
            onDataChange={(data) => updateDimensionData(card.id, data)}
          />
        ))}
      </div>
    </div>
  );
};
```

### 卡片组件架构
```typescript
// components/DataEntry/DimensionCard.tsx
interface DimensionCardProps {
  id: string;
  title: string;
  icon: React.ReactNode;
  isExpanded: boolean;
  isCompleted: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

const DimensionCard: React.FC<DimensionCardProps> = ({
  id, title, icon, isExpanded, isCompleted, onToggle, children
}) => {
  return (
    <div className={`dimension-card ${isExpanded ? 'expanded' : ''}`}>
      <div className="card-header" onClick={onToggle}>
        <div className="card-title">
          {icon}
          <span>{title}</span>
        </div>
        <div className="card-status">
          {isCompleted && <CheckIcon className="completed-icon" />}
          <ChevronIcon className={`chevron ${isExpanded ? 'rotated' : ''}`} />
        </div>
      </div>
      <div className="card-content">
        {isExpanded && children}
      </div>
    </div>
  );
};
```

### 进度跟踪组件
```typescript
// components/DataEntry/ProgressIndicator.tsx
interface ProgressIndicatorProps {
  completed: number;
  total: number;
  estimatedTimeRemaining?: number;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({
  completed, total, estimatedTimeRemaining
}) => {
  const progress = (completed / total) * 100;
  
  return (
    <div className="progress-indicator">
      <div className="progress-text">
        已完成 {completed}/{total} 个维度
        {estimatedTimeRemaining && (
          <span className="time-estimate">
            预计剩余时间: {estimatedTimeRemaining}分钟
          </span>
        )}
      </div>
      <div className="progress-bar">
        <div 
          className="progress-fill"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};
```

### 自动保存机制
- **实时保存**: 使用useEffect监听数据变化，延迟1秒保存
- **localStorage**: 存储结构化的草稿数据
- **恢复机制**: 页面加载时检查并恢复草稿
- **过期清理**: 定期清理过期草稿数据

## 依赖关系

**前置依赖**: Epic 1完成 - 需要用户认证和基础API框架  
**后续任务**: 
- E2S2-E2S5 (各维度数据录入) - 需要卡片架构和状态管理
- E2S6 (数据持久化) - 需要完整的数据录入界面

## 预估时间分解

- **第1天**: 主页面架构设计，卡片组件基础实现
- **第2天**: 进度跟踪组件，自动保存功能实现
- **第3天**: 响应式设计优化，性能优化和测试

## 风险点和缓解策略

### 风险点
1. **状态管理复杂性**: 6个维度的数据状态管理可能导致性能问题
2. **自动保存冲突**: 多个维度同时编辑时的数据冲突
3. **响应式设计挑战**: 不同设备上的布局适配困难
4. **性能问题**: 页面加载时间超出预期

### 缓解策略
1. 使用React Context和useReducer优化状态管理
2. 实现防抖机制，避免频繁的自动保存操作
3. 使用CSS Grid和Flexbox实现响应式布局
4. 实施代码分割和懒加载策略

## 验证方法

### 功能验证
1. **卡片交互测试**: 6个卡片可以正常展开和折叠
2. **进度跟踪测试**: 进度指示器正确反映完成状态
3. **自动保存测试**: 数据修改后自动保存到localStorage
4. **草稿恢复测试**: 页面刷新后正确恢复草稿数据
5. **响应式测试**: 不同屏幕尺寸下布局正确

### 性能验证
- 页面首次加载时间 < 2秒
- 卡片展开/折叠动画流畅（60fps）
- 自动保存操作响应时间 < 100ms

### 可用性验证
- 用户可以在3-4分钟内完成所有维度数据录入
- 界面操作直观，无需额外说明
- 错误状态和加载状态有清晰的视觉反馈

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 6个维度卡片布局和交互正常
- [ ] 进度跟踪功能准确显示
- [ ] 自动保存和草稿恢复功能正常
- [ ] 响应式设计适配桌面和平板
- [ ] 页面性能达到预期指标
- [ ] 组件代码有充分的单元测试
- [ ] 用户体验测试通过

## 设计规范

### 视觉设计
- **深色主题**: 背景色 `#1a1a1a`，卡片背景 `#2d2d2d`
- **青绿色调**: 主色调 `#10b981`，辅助色 `#34d399`
- **卡片设计**: 圆角 `8px`，阴影 `0 2px 8px rgba(0,0,0,0.1)`
- **字体**: 主要字体 `Inter`，等宽字体 `Fira Code`

### 交互设计
- **动画时长**: 卡片展开/折叠 `300ms ease-in-out`
- **点击反馈**: 按钮点击有视觉反馈和触觉反馈
- **键盘导航**: 支持Tab键在卡片间导航
- **触摸优化**: 最小点击区域 `44px x 44px`

## 相关文档

- [数据录入用户体验设计](../数据录入UX设计.md)
- [React组件架构指南](../React组件架构指南.md)
- [响应式设计规范](../响应式设计规范.md)
- [自动保存实现方案](../自动保存实现方案.md)

---

**任务负责人**: [待分配]  
**创建时间**: 2024年  
**最后更新**: 2024年