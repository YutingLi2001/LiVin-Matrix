# 任务02：基础UI组件库

## 任务概述
创建LiVin Matrix应用的核心UI组件库，包括Button、Input、Card等基础组件，实现赛博朋克风格的霓虹发光效果和交互。

## 任务目标
建立可复用的基础组件系统，为整个应用提供一致的交互体验和视觉效果。

## 验收标准

### 1. Button组件实现
- [ ] 创建多种Button变体（Primary、Secondary、Ghost、Neon）
- [ ] 实现TypeScript接口定义
- [ ] 添加霓虹发光悬停效果
- [ ] 支持不同尺寸（sm、md、lg）和加载状态
- [ ] 确保最小点击区域44px×44px（无障碍要求）

### 2. Input组件实现
- [ ] 支持多种输入类型（text、number、email、password、time）
- [ ] 实现聚焦时紫色霓虹发光效果
- [ ] 添加前缀和后缀图标支持
- [ ] 实现错误状态的霓虹红色发光
- [ ] 支持标签、帮助文本和验证信息

### 3. Card组件实现
- [ ] 创建多种Card变体（default、elevated、outlined）
- [ ] 实现玻璃质感效果（backdrop-filter）
- [ ] 添加悬停时紫色霓虹边框辉光
- [ ] 支持不同内边距尺寸
- [ ] 实现交互式卡片点击状态

### 4. TypeScript接口定义
- [ ] 完整的组件Props接口定义
- [ ] 支持React.forwardRef类型安全
- [ ] 导出所有组件类型供其他组件使用
- [ ] 添加JSDoc注释说明

### 5. Storybook文档（可选）
- [ ] 创建组件使用示例
- [ ] 展示所有变体和状态
- [ ] 提供交互式属性调试
- [ ] 记录最佳使用实践

## 技术实现要点

### Button组件示例
```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant: 'primary' | 'secondary' | 'ghost' | 'neon';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  fullWidth?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
  variant = 'primary',
  size = 'md',
  loading = false,
  children,
  className,
  ...props
}, ref) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-black';
  
  const variantClasses = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 neon-glow',
    secondary: 'border border-primary-500 text-primary-400 hover:bg-primary-500/10 neon-border',
    ghost: 'text-primary-400 hover:bg-primary-500/20 neon-text',
    neon: 'border-2 border-neon-purple text-neon-purple hover:shadow-neon-purple neon-flicker'
  };

  return (
    <button
      ref={ref}
      className={cn(baseClasses, variantClasses[variant], className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Spinner className="mr-2" />}
      {children}
    </button>
  );
});
```

### Input组件示例
```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helper?: string;
  prefix?: ReactNode;
  suffix?: ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  helper,
  prefix,
  suffix,
  className,
  ...props
}, ref) => {
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-secondary">
          {label}
        </label>
      )}
      <div className="relative">
        {prefix && (
          <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted">
            {prefix}
          </div>
        )}
        <input
          ref={ref}
          className={cn(
            'w-full bg-secondary border border-primary-500/30 rounded-lg px-4 py-2',
            'text-primary placeholder-muted',
            'focus:border-neon-purple focus:ring-1 focus:ring-neon-purple focus:shadow-neon-glow',
            'transition-all duration-200',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
            prefix && 'pl-10',
            suffix && 'pr-10',
            className
          )}
          {...props}
        />
        {suffix && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted">
            {suffix}
          </div>
        )}
      </div>
      {error && <p className="text-sm text-red-400">{error}</p>}
      {helper && <p className="text-sm text-muted">{helper}</p>}
    </div>
  );
});
```

### Card组件示例
```typescript
interface CardProps {
  variant: 'default' | 'elevated' | 'outlined';
  padding: 'sm' | 'md' | 'lg';
  interactive?: boolean;
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

const Card: React.FC<CardProps> = ({
  variant = 'default',
  padding = 'md',
  interactive = false,
  children,
  className,
  onClick
}) => {
  const baseClasses = 'bg-secondary rounded-lg transition-all duration-200';
  const variantClasses = {
    default: 'border border-primary-500/30',
    elevated: 'shadow-lg backdrop-blur-10',
    outlined: 'border-2 border-primary-500/50'
  };
  
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        paddingClasses[padding],
        interactive && 'cursor-pointer hover:border-neon-purple hover:shadow-neon-glow neon-glow',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
};
```

## 创建的文件列表
- `src/components/ui/Button.tsx` - Button组件及类型定义
- `src/components/ui/Input.tsx` - Input组件及类型定义
- `src/components/ui/Card.tsx` - Card组件及类型定义
- `src/components/ui/index.ts` - 组件导出文件
- `src/styles/components.css` - 组件专用样式
- `src/utils/cn.ts` - className合并工具函数

## 依赖关系
- **前置条件**: 01-design-system-setup完成
- **后续任务**: 所有其他UI组件都依赖于这些基础组件

## 预估时间
**12-16小时**

## 优先级
**高优先级** - 所有其他UI组件的基础

## 风险点和缓解策略
- **风险**: 组件API设计不够灵活
- **缓解**: 参考Material-UI和Ant Design的组件API设计

- **风险**: 霓虹效果影响性能
- **缓解**: 使用CSS硬件加速，谨慎使用box-shadow

## 验证方法
1. **功能验证**: 所有Props正常工作，事件处理正确
2. **样式验证**: 霓虹效果在不同状态下显示正确
3. **无障碍验证**: 支持键盘导航，屏幕阅读器兼容
4. **类型验证**: TypeScript类型检查无错误