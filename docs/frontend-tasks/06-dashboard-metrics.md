# 任务06：主仪表盘界面

## 任务概述
创建LiVin Matrix的主仪表盘页面，展示关键指标概览、6x6矩阵预览和最新数据趋势。

## 任务目标
提供直观的数据概览界面，让用户快速了解个人状态和数据洞察。

## 验收标准

### 1. 指标卡片网格布局
- [ ] 4列指标卡片网格（桌面端）
- [ ] 2列布局（平板端）
- [ ] 1列堆叠布局（移动端）
- [ ] 响应式断点切换动画
- [ ] 卡片加载骨架屏

### 2. 核心指标展示
- [ ] 今日数据完成度指标
- [ ] 本周趋势变化指标
- [ ] 最强相关性发现
- [ ] 数据质量评分
- [ ] 连续记录天数

### 3. 矩阵预览组件
- [ ] 6x6简化矩阵热力图
- [ ] 点击跳转完整矩阵分析
- [ ] 最新相关性数据展示
- [ ] 加载状态和错误处理
- [ ] 时间范围快速切换

### 4. 趋势图表组件
- [ ] 最近7天数据趋势
- [ ] 多维度对比图表
- [ ] 交互式图例
- [ ] 数据点悬停详情
- [ ] 图表响应式适配

### 5. 快速操作区域
- [ ] 今日数据录入快捷入口
- [ ] 数据导出功能
- [ ] 设置和个人资料入口
- [ ] 帮助和反馈链接
- [ ] 夜间模式切换

## 技术实现要点

### Dashboard主页面结构
```typescript
const DashboardPage: React.FC = () => {
  const { metrics, loading, error } = useDashboardData();
  const { matrixPreview } = useMatrixPreview('week');

  if (loading) return <DashboardSkeleton />;
  if (error) return <ErrorState error={error} />;

  return (
    <div className="space-y-8">
      <DashboardHeader />
      <MetricsGrid metrics={metrics} />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <MatrixPreviewCard data={matrixPreview} />
        <TrendChartCard />
      </div>
      <QuickActionsPanel />
    </div>
  );
};
```

### 指标卡片组件
```typescript
interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: number;
  sparkline?: number[];
  icon?: ReactNode;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  trend,
  trendValue,
  sparkline,
  icon
}) => {
  return (
    <Card variant="default" padding="md" className="neon-glow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-secondary mb-1">{title}</p>
          <div className="flex items-baseline space-x-1">
            <span className="text-2xl font-bold font-mono text-primary">
              {value}
            </span>
            {unit && <span className="text-sm text-secondary">{unit}</span>}
          </div>
        </div>
        {icon && (
          <div className="text-neon-purple opacity-60">
            {icon}
          </div>
        )}
      </div>

      {trend && (
        <div className="flex items-center mt-2 space-x-2">
          <TrendIndicator trend={trend} value={trendValue} />
          {sparkline && <Sparkline data={sparkline} />}
        </div>
      )}
    </Card>
  );
};
```

## 创建的文件列表
- `src/pages/DashboardPage.tsx` - 主仪表盘页面
- `src/components/dashboard/MetricsGrid.tsx` - 指标网格
- `src/components/dashboard/MetricCard.tsx` - 指标卡片
- `src/components/dashboard/MatrixPreviewCard.tsx` - 矩阵预览
- `src/components/dashboard/TrendChartCard.tsx` - 趋势图表
- `src/components/dashboard/QuickActionsPanel.tsx` - 快速操作
- `src/components/ui/TrendIndicator.tsx` - 趋势指示器
- `src/components/ui/Sparkline.tsx` - 迷你图表
- `src/hooks/useDashboardData.ts` - 仪表盘数据Hook

## 预估时间
**18-22小时**

## 优先级
**高优先级** - 用户主要交互界面
