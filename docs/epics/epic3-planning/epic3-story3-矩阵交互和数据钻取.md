# E3S3: 矩阵交互和数据钻取

## 任务概述

**任务ID**: E3S3  
**任务标题**: 矩阵交互和数据钻取  
**所属Epic**: Epic 3 - 矩阵分析与可视化  
**预估时间**: 3天  
**优先级**: 高  

## 任务目标

作为用户，我希望点击矩阵中的关系能看到详细的数据分析，以便深入理解相关性的原因。实现矩阵单元格的深度交互功能，包括详细分析面板、散点图展示和异常数据识别。

## 详细的验收标准

### 1. 点击矩阵单元格弹出详细分析面板
- [ ] 模态窗口或侧边面板展示详细分析
- [ ] 面板标题显示两个维度的名称和相关性系数
- [ ] 面板内容区域分为多个分析模块
- [ ] 关闭按钮和ESC键关闭功能
- [ ] 面板动画效果：平滑的打开和关闭过渡
- [ ] 响应式设计：移动端适配为全屏显示

### 2. 散点图展示两个维度的数据分布
- [ ] 使用Recharts ScatterChart展示数据点分布
- [ ] X轴和Y轴分别代表选中的两个维度
- [ ] 数据点颜色编码：按时间或其他维度区分
- [ ] 趋势线绘制：显示线性回归拟合线
- [ ] 坐标轴标签：清晰的维度名称和单位
- [ ] 缩放和平移：支持图表的交互式探索

### 3. 趋势线和相关性统计信息展示
- [ ] 线性回归趋势线：y = ax + b形式
- [ ] 回归方程显示：截距和斜率数值
- [ ] R²决定系数：解释变异程度
- [ ] 95%置信区间：趋势线的置信带
- [ ] 统计摘要：均值、标准差、样本数量
- [ ] 相关性强度解释：文字描述相关关系

### 4. 异常数据点的高亮显示和说明
- [ ] 异常检测算法：基于Z-score或IQR方法
- [ ] 异常点视觉高亮：不同颜色和大小标识
- [ ] 异常点标注：显示具体日期和数值
- [ ] 异常原因推测：基于其他维度数据的分析
- [ ] 异常点列表：详细的异常数据清单
- [ ] 移除异常点选项：查看去除异常后的相关性

### 5. 支持时间维度的数据筛选和对比
- [ ] 时间范围选择器：用户可选择特定时间段
- [ ] 分时段对比：不同时间段的相关性对比
- [ ] 季节性分析：工作日vs周末的相关性差异
- [ ] 时间序列视图：相关性随时间的变化趋势
- [ ] 筛选结果更新：选择时间段后实时更新分析
- [ ] 时间标记：在散点图上显示时间信息

## 技术实现要点

### 详细分析面板组件
```typescript
// components/Analysis/DetailAnalysisPanel.tsx
interface DetailAnalysisPanelProps {
  isOpen: boolean;
  onClose: () => void;
  dimension1: string;
  dimension2: string;
  correlationData: CorrelationDetailData;
}

interface CorrelationDetailData {
  correlation: number;
  pValue: number;
  sampleSize: number;
  dataPoints: Array<{
    date: string;
    value1: number;
    value2: number;
    isOutlier?: boolean;
  }>;
  rSquared: number;
  regressionEquation: {
    slope: number;
    intercept: number;
  };
}

const DetailAnalysisPanel: React.FC<DetailAnalysisPanelProps> = ({
  isOpen, onClose, dimension1, dimension2, correlationData
}) => {
  const [timeRange, setTimeRange] = useState<[Date, Date]>([
    new Date(Date.now() - 90 * 24 * 60 * 60 * 1000),
    new Date()
  ]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="detail-analysis-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="detail-analysis-panel"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
          >
            <div className="panel-header">
              <h3>{getDimensionLabel(dimension1)} × {getDimensionLabel(dimension2)}</h3>
              <div className="correlation-summary">
                相关系数: {correlationData.correlation.toFixed(3)}
                <span className="significance">
                  {getSignificanceLabel(correlationData.pValue)}
                </span>
              </div>
              <button onClick={onClose} className="close-button">×</button>
            </div>

            <div className="panel-content">
              <div className="analysis-tabs">
                <AnalysisTab title="散点图分析">
                  <ScatterPlotAnalysis
                    data={correlationData.dataPoints}
                    dimension1={dimension1}
                    dimension2={dimension2}
                    regressionLine={correlationData.regressionEquation}
                    timeRange={timeRange}
                    onTimeRangeChange={setTimeRange}
                  />
                </AnalysisTab>

                <AnalysisTab title="统计摘要">
                  <StatisticalSummary
                    correlationData={correlationData}
                    dimension1={dimension1}
                    dimension2={dimension2}
                  />
                </AnalysisTab>

                <AnalysisTab title="异常分析">
                  <OutlierAnalysis
                    dataPoints={correlationData.dataPoints}
                    dimension1={dimension1}
                    dimension2={dimension2}
                  />
                </AnalysisTab>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
```

### 散点图分析组件
```typescript
// components/Analysis/ScatterPlotAnalysis.tsx
const ScatterPlotAnalysis: React.FC<{
  data: DataPoint[];
  dimension1: string;
  dimension2: string;
  regressionLine: RegressionEquation;
  timeRange: [Date, Date];
  onTimeRangeChange: (range: [Date, Date]) => void;
}> = ({ data, dimension1, dimension2, regressionLine, timeRange, onTimeRangeChange }) => {
  
  const filteredData = useMemo(() => {
    return data.filter(point => {
      const pointDate = new Date(point.date);
      return pointDate >= timeRange[0] && pointDate <= timeRange[1];
    });
  }, [data, timeRange]);

  const regressionLineData = useMemo(() => {
    const xValues = filteredData.map(d => d.value1);
    const minX = Math.min(...xValues);
    const maxX = Math.max(...xValues);
    
    return [
      { x: minX, y: regressionLine.slope * minX + regressionLine.intercept },
      { x: maxX, y: regressionLine.slope * maxX + regressionLine.intercept }
    ];
  }, [filteredData, regressionLine]);

  return (
    <div className="scatter-plot-analysis">
      <div className="time-range-selector">
        <DateRangePicker
          value={timeRange}
          onChange={onTimeRangeChange}
          maxDate={new Date()}
        />
      </div>

      <div className="scatter-plot-container">
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart data={filteredData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              type="number"
              dataKey="value1"
              name={getDimensionLabel(dimension1)}
              domain={['dataMin', 'dataMax']}
            />
            <YAxis
              type="number"
              dataKey="value2"
              name={getDimensionLabel(dimension2)}
              domain={['dataMin', 'dataMax']}
            />
            <Tooltip
              content={<CustomScatterTooltip dimension1={dimension1} dimension2={dimension2} />}
            />
            
            {/* 正常数据点 */}
            <Scatter
              data={filteredData.filter(d => !d.isOutlier)}
              fill="#3b82f6"
              fillOpacity={0.6}
            />
            
            {/* 异常数据点 */}
            <Scatter
              data={filteredData.filter(d => d.isOutlier)}
              fill="#ef4444"
              fillOpacity={0.8}
              shape="triangle"
            />
            
            {/* 回归趋势线 */}
            <Line
              type="linear"
              data={regressionLineData}
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="regression-info">
        <div className="regression-equation">
          回归方程: y = {regressionLine.slope.toFixed(3)}x + {regressionLine.intercept.toFixed(3)}
        </div>
        <div className="r-squared">
          决定系数: R² = {correlationData.rSquared.toFixed(3)}
        </div>
      </div>
    </div>
  );
};
```

## 依赖关系

**前置依赖**: E3S2 (6x6矩阵热力图可视化) - 需要基础矩阵组件  
**后续任务**: E3S4 (时间维度分析) - 可以复用时间筛选功能

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 详细分析面板功能完整
- [ ] 散点图和趋势线准确显示
- [ ] 异常检测和高亮功能正常
- [ ] 时间筛选和对比功能工作正常
- [ ] 用户体验流畅，交互响应迅速

---

**任务负责人**: [待分配]  
**创建时间**: 2024年  
**最后更新**: 2024年