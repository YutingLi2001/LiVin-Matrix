# E3S2: 6x6矩阵热力图可视化

## 任务概述

**任务ID**: E3S2
**任务标题**: 6x6矩阵热力图可视化
**所属Epic**: Epic 3 - 矩阵分析与可视化
**预估时间**: 4天
**优先级**: 高

## 任务目标

作为用户，我希望看到不同生活维度间相关性的直观矩阵图，以便发现生活模式。使用Recharts实现6x6相关性热力图，支持颜色编码、交互功能和性能优化。

## 详细的验收标准

### 1. 使用Recharts实现6x6热力图组件
- [ ] 安装和配置Recharts库及相关依赖
- [ ] 创建CorrelationMatrix主组件
- [ ] 6x6网格布局：睡眠、饮食、运动、情绪、工作效率、社交
- [ ] 数据适配器：将API数据转换为Recharts格式
- [ ] 响应式设计：适配不同屏幕尺寸
- [ ] 组件性能优化：避免不必要的重渲染

### 2. 颜色编码表示相关性强弱（红-黄-绿色谱）
- [ ] 颜色映射函数：相关性值(-1到+1)映射到颜色
- [ ] 正相关色谱：浅绿→深绿(0到+1)
- [ ] 负相关色谱：浅红→深红(0到-1)
- [ ] 无相关颜色：接近白色或灰色(接近0值)
- [ ] 色盲友好：确保色盲用户也能区分
- [ ] 颜色图例：显示颜色与相关性强度的对应关系

### 3. 鼠标悬停显示详细相关性数值和显著性
- [ ] Tooltip组件：悬停时显示详细信息
- [ ] 相关性系数：显示精确到小数点后3位的数值
- [ ] 显著性标识：显示p值和显著性符号(*,**,***)
- [ ] 样本量信息：显示计算相关性的数据点数量
- [ ] 维度标签：清晰显示两个相关维度的名称
- [ ] 统计解释：简单的相关性强度描述(强/中/弱)

### 4. 矩阵单元格点击支持数据钻取
- [ ] 点击事件处理：单元格点击触发详细分析
- [ ] 钻取路由：跳转到对应维度的详细分析页面
- [ ] 状态传递：将选中的维度对信息传递给详细页面
- [ ] 视觉反馈：点击时的高亮和动画效果
- [ ] 键盘支持：支持Tab和Enter键操作
- [ ] 点击区域优化：确保小单元格也容易点击

### 5. 矩阵渲染时间小于2秒（符合NFR3要求）
- [ ] 性能测试：在不同数据量下测试渲染时间
- [ ] 数据预处理：在后端完成复杂计算
- [ ] 虚拟化渲染：大矩阵的性能优化
- [ ] 缓存策略：相同数据的渲染结果缓存
- [ ] 懒加载：非关键元素的延迟加载
- [ ] 性能监控：集成渲染时间监控

## 技术实现要点

### 热力图组件架构
```typescript
// components/Analysis/CorrelationMatrix.tsx
interface CorrelationMatrixProps {
  correlationData: CorrelationData;
  onCellClick: (dimension1: string, dimension2: string) => void;
  loading?: boolean;
}

interface CorrelationData {
  correlations: Record<string, Record<string, number>>;
  p_values: Record<string, Record<string, number>>;
  sample_size: number;
  time_window: number;
  calculated_at: string;
}

const CorrelationMatrix: React.FC<CorrelationMatrixProps> = ({
  correlationData,
  onCellClick,
  loading = false
}) => {
  const dimensions = [
    { key: 'sleep', label: '睡眠', color: '#3b82f6' },
    { key: 'nutrition', label: '饮食', color: '#10b981' },
    { key: 'exercise', label: '运动', color: '#f59e0b' },
    { key: 'mood', label: '情绪', color: '#8b5cf6' },
    { key: 'productivity', label: '工作效率', color: '#ef4444' },
    { key: 'social', label: '社交', color: '#06b6d4' }
  ];

  const getCorrelationColor = useCallback((value: number): string => {
    if (value > 0) {
      // 正相关：白色到绿色
      const intensity = Math.abs(value);
      return `rgba(34, 197, 94, ${intensity})`;
    } else if (value < 0) {
      // 负相关：白色到红色
      const intensity = Math.abs(value);
      return `rgba(239, 68, 68, ${intensity})`;
    }
    return '#f3f4f6'; // 无相关
  }, []);

  return (
    <div className="correlation-matrix">
      <div className="matrix-header">
        <h3>维度相关性矩阵</h3>
        <div className="matrix-info">
          样本数：{correlationData.sample_size} |
          时间窗口：{correlationData.time_window}天
        </div>
      </div>

      <div className="matrix-container">
        <div className="matrix-grid">
          {/* 行标签 */}
          <div className="row-labels">
            {dimensions.map(dim => (
              <div key={dim.key} className="row-label">
                {dim.label}
              </div>
            ))}
          </div>

          {/* 矩阵单元格 */}
          <div className="matrix-cells">
            {dimensions.map((rowDim, i) =>
              dimensions.map((colDim, j) => (
                <CorrelationCell
                  key={`${rowDim.key}-${colDim.key}`}
                  row={i}
                  col={j}
                  value={correlationData.correlations[rowDim.key][colDim.key]}
                  pValue={correlationData.p_values[rowDim.key][colDim.key]}
                  rowDimension={rowDim}
                  colDimension={colDim}
                  color={getCorrelationColor(correlationData.correlations[rowDim.key][colDim.key])}
                  onClick={() => onCellClick(rowDim.key, colDim.key)}
                />
              ))
            )}
          </div>

          {/* 列标签 */}
          <div className="col-labels">
            {dimensions.map(dim => (
              <div key={dim.key} className="col-label">
                {dim.label}
              </div>
            ))}
          </div>
        </div>

        <ColorLegend />
      </div>
    </div>
  );
};
```

### 矩阵单元格组件
```typescript
// components/Analysis/CorrelationCell.tsx
interface CorrelationCellProps {
  row: number;
  col: number;
  value: number;
  pValue: number;
  rowDimension: Dimension;
  colDimension: Dimension;
  color: string;
  onClick: () => void;
}

const CorrelationCell: React.FC<CorrelationCellProps> = ({
  value, pValue, rowDimension, colDimension, color, onClick
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const getSignificanceSymbol = (p: number): string => {
    if (p < 0.001) return '***';
    if (p < 0.01) return '**';
    if (p < 0.05) return '*';
    return '';
  };

  const getCorrelationStrength = (r: number): string => {
    const abs_r = Math.abs(r);
    if (abs_r >= 0.7) return '强';
    if (abs_r >= 0.3) return '中';
    if (abs_r >= 0.1) return '弱';
    return '无';
  };

  return (
    <div
      className={`correlation-cell ${isHovered ? 'hovered' : ''}`}
      style={{ backgroundColor: color }}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="cell-value">
        {value.toFixed(3)}
      </div>
      <div className="cell-significance">
        {getSignificanceSymbol(pValue)}
      </div>

      {isHovered && (
        <div className="cell-tooltip">
          <div className="tooltip-content">
            <div className="dimensions">
              {rowDimension.label} × {colDimension.label}
            </div>
            <div className="correlation">
              相关系数: {value.toFixed(3)} ({getCorrelationStrength(value)}相关)
            </div>
            <div className="significance">
              显著性: p = {pValue.toFixed(4)} {getSignificanceSymbol(pValue)}
            </div>
            <div className="hint">
              点击查看详细分析
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

### 颜色图例组件
```typescript
// components/Analysis/ColorLegend.tsx
const ColorLegend: React.FC = () => {
  const legendSteps = [-1, -0.7, -0.3, 0, 0.3, 0.7, 1];

  return (
    <div className="color-legend">
      <div className="legend-title">相关性强度</div>
      <div className="legend-bar">
        {legendSteps.map((value, index) => (
          <div
            key={index}
            className="legend-step"
            style={{
              backgroundColor: getCorrelationColor(value),
              width: `${100 / (legendSteps.length - 1)}%`
            }}
          >
            <span className="legend-value">{value}</span>
          </div>
        ))}
      </div>
      <div className="legend-labels">
        <span>强负相关</span>
        <span>无相关</span>
        <span>强正相关</span>
      </div>
    </div>
  );
};
```

## 依赖关系

**前置依赖**: E3S1 (相关性算法实现) - 需要相关性计算API
**后续任务**: E3S3 (矩阵交互和数据钻取) - 需要基础热力图组件

## 预估时间分解

- **第1天**: Recharts集成，基础6x6矩阵布局
- **第2天**: 颜色编码系统，热力图渲染
- **第3天**: 交互功能(悬停、点击)，Tooltip实现
- **第4天**: 性能优化，响应式设计和测试

## 风险点和缓解策略

### 风险点
1. **Recharts局限性**: 可能不支持复杂的热力图需求
2. **性能问题**: 复杂的6x6矩阵渲染可能缓慢
3. **颜色可访问性**: 色盲用户无法区分颜色差异
4. **移动端适配**: 小屏幕上矩阵显示困难

### 缓解策略
1. 准备Canvas/SVG自定义实现作为备选方案
2. 使用React.memo和useMemo优化渲染性能
3. 添加图案和文字标识辅助颜色编码
4. 设计简化的移动端矩阵视图

## 验证方法

### 功能验证
1. **渲染准确性**: 相关性数值与颜色编码一致
2. **交互功能**: 悬停和点击事件正常工作
3. **响应式适配**: 不同屏幕尺寸下正常显示
4. **可访问性**: 键盘导航和屏幕阅读器兼容

### 性能验证
- 初始渲染时间 < 2秒
- 交互响应时间 < 100ms
- 内存使用稳定，无内存泄漏

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 6x6热力图正确渲染相关性数据
- [ ] 颜色编码准确反映相关性强度
- [ ] 交互功能完整且响应迅速
- [ ] 性能指标达到要求
- [ ] 可访问性和响应式设计良好
- [ ] 组件有充分的单元测试

---

**任务负责人**: [待分配]
**创建时间**: 2024年
**最后更新**: 2024年
