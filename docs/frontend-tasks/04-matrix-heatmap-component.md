# 任务04：矩阵热力图组件

## 任务概述
实现LiVin Matrix应用的核心6x6相关性矩阵热力图组件，使用Recharts库创建交互式数据可视化。

## 任务目标
创建专业级的矩阵数据可视化组件，支持相关性数据展示、交互式单元格点击和赛博朋克视觉效果。

## 验收标准

### 1. 基础矩阵热力图实现
- [ ] 创建6x6矩阵网格布局
- [ ] 集成Recharts热力图组件
- [ ] 实现相关性数据映射（-1到1的数值范围）
- [ ] 添加坐标轴标签（6个生活维度）
- [ ] 实现矩阵单元格的基础渲染

### 2. 赛博朋克视觉设计
- [ ] 实现渐变色彩映射（负相关红色→无相关灰色→正相关绿色）
- [ ] 添加霓虹边框效果和网格线
- [ ] 实现单元格悬停时的发光效果
- [ ] 使用赛博朋克配色方案
- [ ] 添加矩阵标题和图例

### 3. 交互功能实现
- [ ] 实现单元格点击事件处理
- [ ] 添加悬停时的Tooltip显示（相关系数、p值、置信区间）
- [ ] 支持单元格选择状态管理
- [ ] 实现矩阵数据钻取功能
- [ ] 添加矩阵重置和刷新功能

### 4. 数据处理和状态管理
- [ ] 创建相关性数据类型定义
- [ ] 实现数据预处理和验证
- [ ] 支持时间范围数据过滤
- [ ] 添加加载状态和错误处理
- [ ] 实现数据缓存机制

### 5. 响应式和性能优化
- [ ] 实现桌面端完整矩阵显示
- [ ] 添加平板端简化视图
- [ ] 优化大数据量的渲染性能
- [ ] 实现虚拟化滚动（如需要）
- [ ] 添加动画过渡效果

## 技术实现要点

### MatrixHeatmap组件接口
```typescript
interface CorrelationData {
  dimensions: string[];
  matrix: number[][];
  pValues?: number[][];
  confidenceIntervals?: Array<Array<[number, number]>>;
  lastUpdated: Date;
}

interface MatrixHeatmapProps {
  data: CorrelationData;
  onCellClick: (rowIndex: number, colIndex: number, value: number) => void;
  onCellHover?: (rowIndex: number, colIndex: number, value: number) => void;
  selectedCell?: [number, number];
  timeRange: 'week' | 'month' | 'quarter' | 'all';
  loading?: boolean;
  className?: string;
}

const MatrixHeatmap: React.FC<MatrixHeatmapProps> = ({
  data,
  onCellClick,
  onCellHover,
  selectedCell,
  timeRange,
  loading = false,
  className
}) => {
  // 组件实现
};
```

### 色彩映射函数
```typescript
const getColorByValue = (value: number): string => {
  if (value < -0.5) return '#ff0066'; // 强负相关 - 霓虹红
  if (value < -0.2) return '#ff3399'; // 中负相关
  if (value < 0.2)  return '#404040'; // 无相关 - 暗灰
  if (value < 0.5)  return '#66ff99'; // 中正相关
  if (value >= 0.5) return '#00ff88'; // 强正相关 - 霓虹绿
  return '#8b5cf6'; // 极强相关 - 主紫色
};

const getCellIntensity = (value: number): number => {
  return Math.abs(value) * 0.8 + 0.2; // 0.2-1.0 的不透明度
};
```

### 自定义矩阵单元格组件
```typescript
interface MatrixCellProps {
  value: number;
  rowIndex: number;
  colIndex: number;
  isSelected: boolean;
  onCellClick: (row: number, col: number, value: number) => void;
  onCellHover: (row: number, col: number, value: number) => void;
}

const MatrixCell: React.FC<MatrixCellProps> = ({
  value,
  rowIndex,
  colIndex,
  isSelected,
  onCellClick,
  onCellHover
}) => {
  return (
    <div
      className={cn(
        'relative w-12 h-12 border border-primary-500/20 cursor-pointer',
        'transition-all duration-200 hover:border-neon-purple',
        'flex items-center justify-center text-xs font-mono',
        isSelected && 'ring-2 ring-neon-purple shadow-neon-glow'
      )}
      style={{
        backgroundColor: getColorByValue(value),
        opacity: getCellIntensity(value)
      }}
      onClick={() => onCellClick(rowIndex, colIndex, value)}
      onMouseEnter={() => onCellHover(rowIndex, colIndex, value)}
    >
      <span className="text-white font-bold drop-shadow-lg">
        {value.toFixed(2)}
      </span>
      
      {/* 悬停发光效果 */}
      <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity">
        <div className="w-full h-full border-2 border-neon-purple shadow-neon-glow rounded-sm" />
      </div>
    </div>
  );
};
```

### Tooltip组件实现
```typescript
interface MatrixTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
  rowIndex?: number;
  colIndex?: number;
  dimensions?: string[];
}

const MatrixTooltip: React.FC<MatrixTooltipProps> = ({
  active,
  payload,
  rowIndex,
  colIndex,
  dimensions
}) => {
  if (!active || !payload?.[0]) return null;

  const value = payload[0].value;
  const rowDimension = dimensions?.[rowIndex] || '';
  const colDimension = dimensions?.[colIndex] || '';

  return (
    <Card variant="elevated" padding="sm" className="bg-secondary/90 backdrop-blur-lg border border-neon-purple/50">
      <div className="space-y-2 text-sm">
        <div className="font-semibold text-neon-purple">
          {rowDimension} ↔ {colDimension}
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <span className="text-secondary">相关系数:</span>
          <span className="font-mono text-primary">{value.toFixed(3)}</span>
          <span className="text-secondary">相关强度:</span>
          <span className="text-primary">
            {Math.abs(value) > 0.7 ? '强' : Math.abs(value) > 0.3 ? '中' : '弱'}
          </span>
        </div>
      </div>
    </Card>
  );
};
```

## 创建的文件列表
- `src/components/matrix/MatrixHeatmap.tsx` - 主热力图组件
- `src/components/matrix/MatrixCell.tsx` - 矩阵单元格组件
- `src/components/matrix/MatrixTooltip.tsx` - 悬停提示组件
- `src/components/matrix/MatrixLegend.tsx` - 图例组件
- `src/types/matrix.ts` - 矩阵数据类型定义
- `src/utils/matrixCalculations.ts` - 相关性计算工具
- `src/hooks/useMatrixData.ts` - 矩阵数据管理Hook

## 依赖关系
- **前置条件**: 01-design-system-setup、02-base-ui-components完成
- **后续任务**: 矩阵分析页面需要使用此组件

## 预估时间
**20-24小时**

## 优先级
**高优先级** - 应用核心功能组件

## 风险点和缓解策略
- **风险**: Recharts性能问题
- **缓解**: 实现数据虚拟化和懒加载

- **风险**: 色彩可访问性问题
- **缓解**: 添加纹理图案辅助色盲用户识别

## 验证方法
1. **功能验证**: 矩阵数据正确显示，交互响应正常
2. **视觉验证**: 色彩映射准确，赛博朋克效果符合设计
3. **性能验证**: 大数据量下渲染流畅
4. **无障碍验证**: 支持键盘导航和屏幕阅读器