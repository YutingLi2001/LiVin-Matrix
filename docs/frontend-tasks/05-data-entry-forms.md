# 任务05：数据录入表单系统

## 任务概述
创建LiVin Matrix的6维度数据录入表单系统，实现3-4分钟快速录入目标，采用折叠卡片布局和赛博朋克样式。

## 任务目标
建立高效的数据录入界面，支持6个生活维度的快速数据输入，优化用户体验和数据质量。

## 验收标准

### 1. 折叠卡片布局实现
- [ ] 创建6个维度的折叠卡片组件
- [ ] 实现卡片展开/收起动画效果
- [ ] 添加进度指示器（已完成X/6维度）
- [ ] 实现卡片状态管理（未开始/进行中/已完成）
- [ ] 支持任意顺序完成各维度录入

### 2. 睡眠维度录入组件
- [ ] 时间段选择器（就寝时间→起床时间）
- [ ] 睡眠质量星级评分（1-10分）
- [ ] 晨起清醒度评分（1-10分）
- [ ] 跨午夜睡眠时间正确处理
- [ ] 数据验证（睡眠时长2-16小时）

### 3. 饮食维度录入组件
- [ ] 营养素数值输入（卡路里、蛋白质、脂肪、碳水）
- [ ] 快速预设模板（减脂餐/正常餐/增肌餐）
- [ ] 营养建议提示系统
- [ ] 数据范围验证（0-5000kcal等）
- [ ] 智能默认值填充

### 4. 运动维度录入组件
- [ ] 分时段训练记录组件
- [ ] 力量训练录入（时间、强度、感受）
- [ ] 有氧训练录入（类型、强度、感受）
- [ ] 6种运动类型选择器
- [ ] 总训练时长自动计算

### 5. 情绪、工作效率、社交维度
- [ ] 情绪4项星级评分组件
- [ ] 工作效率数值+评分+环境选择
- [ ] 社交计数输入+满意度评分
- [ ] 快捷模板支持
- [ ] 批量操作功能

## 技术实现要点

### 主数据录入页面结构
```typescript
interface DataEntryFormData {
  sleep: SleepData;
  nutrition: NutritionData;
  exercise: ExerciseData;
  mood: MoodData;
  productivity: ProductivityData;
  social: SocialData;
}

const DataEntryPage: React.FC = () => {
  const [formData, setFormData] = useState<DataEntryFormData>(initialFormData);
  const [completedDimensions, setCompletedDimensions] = useState<string[]>([]);
  const [currentExpanded, setCurrentExpanded] = useState<string | null>(null);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-primary font-display mb-4">
          今日数据录入
        </h1>
        <ProgressIndicator 
          completed={completedDimensions.length}
          total={6}
          estimatedTimeRemaining={getEstimatedTime(completedDimensions)}
        />
      </div>

      <div className="grid gap-4">
        <DimensionCard
          dimension="sleep"
          title="睡眠维度"
          icon={<MoonIcon />}
          estimatedTime="30秒"
          isCompleted={completedDimensions.includes('sleep')}
          isExpanded={currentExpanded === 'sleep'}
          onToggle={() => toggleCard('sleep')}
        >
          <SleepForm 
            data={formData.sleep}
            onChange={(data) => updateFormData('sleep', data)}
            onComplete={() => markCompleted('sleep')}
          />
        </DimensionCard>

        {/* 其他维度卡片... */}
      </div>

      <div className="flex justify-between mt-8">
        <Button variant="secondary">保存草稿</Button>
        <Button 
          variant="primary"
          disabled={completedDimensions.length < 6}
        >
          提交今日数据
        </Button>
      </div>
    </div>
  );
};
```

### 折叠维度卡片组件
```typescript
interface DimensionCardProps {
  dimension: string;
  title: string;
  icon: ReactNode;
  estimatedTime: string;
  isCompleted: boolean;
  isExpanded: boolean;
  onToggle: () => void;
  children: ReactNode;
}

const DimensionCard: React.FC<DimensionCardProps> = ({
  dimension,
  title,
  icon,
  estimatedTime,
  isCompleted,
  isExpanded,
  onToggle,
  children
}) => {
  return (
    <Card 
      variant="outlined" 
      padding="md"
      className={cn(
        'transition-all duration-300',
        isCompleted && 'border-green-500 bg-green-500/5',
        isExpanded && 'border-neon-purple shadow-neon-glow'
      )}
    >
      <div 
        className="flex items-center justify-between cursor-pointer"
        onClick={onToggle}
      >
        <div className="flex items-center space-x-4">
          <div className={cn(
            'w-10 h-10 rounded-lg flex items-center justify-center',
            isCompleted ? 'bg-green-500 text-primary' : 'bg-primary-500/20 text-primary'
          )}>
            {isCompleted ? <CheckIcon /> : icon}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-primary">{title}</h3>
            <p className="text-sm text-secondary">预计用时: {estimatedTime}</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {isCompleted && (
            <Badge variant="success">已完成</Badge>
          )}
          <ChevronDownIcon 
            className={cn(
              'w-5 h-5 text-secondary transition-transform',
              isExpanded && 'rotate-180'
            )}
          />
        </div>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="mt-6 pt-6 border-t border-primary-500/20"
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};
```

### 睡眠维度表单组件
```typescript
interface SleepFormProps {
  data: SleepData;
  onChange: (data: SleepData) => void;
  onComplete: () => void;
}

const SleepForm: React.FC<SleepFormProps> = ({ data, onChange, onComplete }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-secondary mb-2">
            就寝时间
          </label>
          <Input
            type="time"
            value={data.bedtime}
            onChange={(e) => onChange({ ...data, bedtime: e.target.value })}
            className="font-mono"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-secondary mb-2">
            起床时间
          </label>
          <Input
            type="time"
            value={data.wakeTime}
            onChange={(e) => onChange({ ...data, wakeTime: e.target.value })}
            className="font-mono"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-secondary mb-2">
          睡眠质量 (1-10分)
        </label>
        <RatingInput
          value={data.quality}
          onChange={(value) => onChange({ ...data, quality: value })}
          max={10}
          icon="star"
          size="md"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-secondary mb-2">
          晨起清醒度 (1-10分)
        </label>
        <RatingInput
          value={data.alertness}
          onChange={(value) => onChange({ ...data, alertness: value })}
          max={10}
          icon="sun"
          size="md"
        />
      </div>

      <div className="bg-primary-500/10 rounded-lg p-4">
        <p className="text-sm text-secondary">
          睡眠时长: <span className="text-primary font-mono">
            {calculateSleepDuration(data.bedtime, data.wakeTime)}小时
          </span>
        </p>
      </div>

      <div className="flex justify-end">
        <Button 
          variant="primary"
          onClick={onComplete}
          disabled={!isFormValid(data)}
        >
          完成睡眠数据
        </Button>
      </div>
    </div>
  );
};
```

### 星级评分组件
```typescript
interface RatingInputProps {
  value: number;
  onChange: (value: number) => void;
  max: number;
  icon: 'star' | 'circle' | 'heart' | 'sun';
  size: 'sm' | 'md' | 'lg';
  color?: string;
}

const RatingInput: React.FC<RatingInputProps> = ({
  value,
  onChange,
  max,
  icon,
  size,
  color = 'neon-purple'
}) => {
  const IconComponent = {
    star: StarIcon,
    circle: CircleIcon,
    heart: HeartIcon,
    sun: SunIcon
  }[icon];

  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  return (
    <div className="flex items-center space-x-1">
      {Array.from({ length: max }, (_, index) => (
        <button
          key={index}
          type="button"
          onClick={() => onChange(index + 1)}
          className={cn(
            'transition-all duration-200 hover:scale-110',
            index < value 
              ? `text-${color} drop-shadow-glow`
              : 'text-gray-400 hover:text-gray-300'
          )}
        >
          <IconComponent className={sizes[size]} />
        </button>
      ))}
      <span className="ml-3 text-sm text-secondary font-mono">
        {value}/{max}
      </span>
    </div>
  );
};
```

## 创建的文件列表
- `src/pages/DataEntryPage.tsx` - 主数据录入页面
- `src/components/forms/DimensionCard.tsx` - 维度折叠卡片
- `src/components/forms/SleepForm.tsx` - 睡眠维度表单
- `src/components/forms/NutritionForm.tsx` - 饮食维度表单
- `src/components/forms/ExerciseForm.tsx` - 运动维度表单
- `src/components/forms/MoodForm.tsx` - 情绪维度表单
- `src/components/forms/ProductivityForm.tsx` - 工作效率表单
- `src/components/forms/SocialForm.tsx` - 社交维度表单
- `src/components/ui/RatingInput.tsx` - 星级评分组件
- `src/components/ui/ProgressIndicator.tsx` - 进度指示器
- `src/types/formData.ts` - 表单数据类型定义
- `src/utils/formValidation.ts` - 表单验证工具
- `src/hooks/useDataEntry.ts` - 数据录入管理Hook

## 依赖关系
- **前置条件**: 01-design-system-setup、02-base-ui-components完成
- **后续任务**: 需要连接后端API进行数据提交

## 预估时间
**24-28小时**

## 优先级
**高优先级** - 核心用户功能

## 风险点和缓解策略
- **风险**: 表单复杂度影响用户体验
- **缓解**: 实施智能默认值和快捷模板

- **风险**: 3-4分钟目标难以达成
- **缓解**: 通过用户测试优化交互流程

## 验证方法
1. **时间验证**: 实际录入时间符合3-4分钟目标
2. **数据验证**: 所有输入数据格式正确，范围合理
3. **体验验证**: 界面流畅，交互直观
4. **无障碍验证**: 支持键盘导航和屏幕阅读器