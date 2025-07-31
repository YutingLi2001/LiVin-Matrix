# 任务07：矩阵分析页面

## 任务概述
创建完整的矩阵分析界面，提供6x6相关性热力图的详细分析功能，包括时间范围选择、维度过滤和数据钻取。

## 验收标准

### 1. 完整矩阵分析界面
- [ ] 全屏6x6相关性热力图显示
- [ ] 时间范围选择器（日/周/月/全部）
- [ ] 维度选择器（显示/隐藏特定维度）
- [ ] 数据加载和错误状态处理
- [ ] 分析结果缓存机制

### 2. 交互式数据钻取
- [ ] 矩阵单元格点击详细分析
- [ ] 弹出模态框显示详细数据
- [ ] 相关性趋势时间序列图
- [ ] 散点图展示数据分布
- [ ] 统计显著性检验结果

### 3. 高级分析功能
- [ ] 相关性强度排序
- [ ] 异常数据点识别
- [ ] 相关性变化趋势分析
- [ ] 多时间段对比
- [ ] 个性化洞察生成

## 技术实现要点

### 矩阵分析页面结构
```typescript
const MatrixAnalysisPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState<TimeRange>('month');
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>(ALL_DIMENSIONS);
  const [selectedCell, setSelectedCell] = useState<[number, number] | null>(null);
  
  const { matrixData, loading, error } = useMatrixAnalysis(timeRange, selectedDimensions);

  return (
    <div className="space-y-6">
      <AnalysisHeader 
        timeRange={timeRange}
        onTimeRangeChange={setTimeRange}
        dimensions={selectedDimensions}
        onDimensionsChange={setSelectedDimensions}
      />
      
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        <div className="xl:col-span-3">
          <MatrixHeatmap
            data={matrixData}
            onCellClick={(row, col) => setSelectedCell([row, col])}
            selectedCell={selectedCell}
            timeRange={timeRange}
            loading={loading}
          />
        </div>
        
        <div className="space-y-4">
          <CorrelationRankings data={matrixData} />
          <InsightPanel correlations={matrixData} />
        </div>
      </div>

      {selectedCell && (
        <DrillDownModal
          rowIndex={selectedCell[0]}
          colIndex={selectedCell[1]}
          data={matrixData}
          onClose={() => setSelectedCell(null)}
        />
      )}
    </div>
  );
};
```

## 创建的文件列表
- `src/pages/MatrixAnalysisPage.tsx` - 矩阵分析主页面
- `src/components/matrix/AnalysisHeader.tsx` - 分析控制头部
- `src/components/matrix/DrillDownModal.tsx` - 数据钻取模态框
- `src/components/matrix/CorrelationRankings.tsx` - 相关性排名
- `src/components/matrix/InsightPanel.tsx` - 洞察面板
- `src/hooks/useMatrixAnalysis.ts` - 矩阵分析数据Hook

## 预估时间
**22-26小时**

## 优先级
**高优先级** - 核心分析功能