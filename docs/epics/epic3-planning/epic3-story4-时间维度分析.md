# E3S4: 时间维度分析

## 任务概述

**任务ID**: E3S4  
**任务标题**: 时间维度分析  
**所属Epic**: Epic 3 - 矩阵分析与可视化  
**预估时间**: 3天  
**优先级**: 高  

## 任务目标

作为用户，我希望能看到数据随时间的变化趋势，以便了解我的改进进展。实现时间序列分析功能，包括趋势图表、周期性模式识别和简单的预测功能。

## 详细的验收标准

### 1. 单维度时间序列图表（最近30天趋势）
- [ ] 使用Recharts LineChart展示时间序列数据
- [ ] 支持6个维度的独立时间序列图表
- [ ] X轴时间刻度：日期格式化显示
- [ ] Y轴数值范围：自适应维度数据范围
- [ ] 趋势线平滑：使用移动平均或样条插值
- [ ] 缺失数据处理：虚线连接或数据点标记

### 2. 按周/月的数据汇总和对比分析
- [ ] 周汇总视图：每周平均值的对比
- [ ] 月汇总视图：每月平均值的趋势
- [ ] 同期对比：本周vs上周，本月vs上月
- [ ] 汇总统计：平均值、最大值、最小值、变化幅度
- [ ] 柱状图展示：周/月汇总数据的可视化
- [ ] 变化率计算：显示相比上期的百分比变化

### 3. 季节性模式识别（工作日vs周末差异）
- [ ] 工作日模式分析：周一至周五的平均模式
- [ ] 周末模式分析：周六日的平均模式
- [ ] 模式对比图表：工作日与周末的差异可视化
- [ ] 统计显著性检验：工作日与周末差异的显著性
- [ ] 季节性指标：各维度的季节性强度评分
- [ ] 模式建议：基于模式识别的个性化建议

### 4. 数据异常检测和标注
- [ ] 异常检测算法：基于Z-score、IQR或时间序列异常检测
- [ ] 异常点标注：在时间序列图上高亮异常数据点
- [ ] 异常类型分类：数值异常、模式异常、趋势异常
- [ ] 异常原因分析：结合其他维度数据推测异常原因
- [ ] 异常点详情：点击异常点显示详细信息
- [ ] 异常处理建议：提供数据修正或解释建议

### 5. 趋势预测功能（简单线性回归）
- [ ] 线性趋势预测：基于历史数据的线性回归预测
- [ ] 预测时间范围：未来7-30天的趋势预测
- [ ] 置信区间：预测结果的不确定性范围
- [ ] 预测准确性评估：基于历史数据的预测准确性
- [ ] 多模型对比：线性、多项式、指数趋势对比
- [ ] 预测可视化：预测线与置信带的图表展示

## 技术实现要点

### 时间序列分析服务
```python
# app/services/time_series_service.py
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class TimeSeriesService:
    
    def analyze_dimension_trends(self, 
                               user_data: List[Dict], 
                               dimension: str,
                               days: int = 30) -> Dict:
        """
        分析单个维度的时间序列趋势
        """
        # 构建时间序列数据
        df = pd.DataFrame(user_data)
        df['record_date'] = pd.to_datetime(df['record_date'])
        df = df.sort_values('record_date')
        
        # 填充缺失日期
        date_range = pd.date_range(
            start=df['record_date'].min(),
            end=df['record_date'].max(),
            freq='D'
        )
        df_full = df.set_index('record_date').reindex(date_range)
        
        series = df_full[dimension].dropna()
        
        return {
            'raw_data': series.to_dict(),
            'trend_analysis': self._analyze_trend(series),
            'seasonality': self._analyze_seasonality(df_full, dimension),
            'anomalies': self._detect_anomalies(series),
            'forecast': self._forecast_trend(series, days=7)
        }
    
    def _analyze_trend(self, series: pd.Series) -> Dict:
        """
        趋势分析
        """
        x = np.arange(len(series)).reshape(-1, 1)
        y = series.values
        
        model = LinearRegression()
        model.fit(x, y)
        
        trend_slope = model.coef_[0]
        r_squared = model.score(x, y)
        
        # 趋势方向判断
        if abs(trend_slope) < 0.01:
            trend_direction = "稳定"
        elif trend_slope > 0:
            trend_direction = "上升"
        else:
            trend_direction = "下降"
        
        return {
            'slope': trend_slope,
            'r_squared': r_squared,
            'direction': trend_direction,
            'strength': 'strong' if r_squared > 0.7 else 'moderate' if r_squared > 0.3 else 'weak'
        }
    
    def _analyze_seasonality(self, df: pd.DataFrame, dimension: str) -> Dict:
        """
        季节性模式分析
        """
        df['weekday'] = df.index.weekday
        df['is_weekend'] = df['weekday'].isin([5, 6])
        
        weekday_data = df[~df['is_weekend']][dimension].dropna()
        weekend_data = df[df['is_weekend']][dimension].dropna()
        
        if len(weekday_data) > 0 and len(weekend_data) > 0:
            # t检验比较工作日与周末差异
            t_stat, p_value = stats.ttest_ind(weekday_data, weekend_data)
            
            return {
                'weekday_mean': weekday_data.mean(),
                'weekend_mean': weekend_data.mean(),
                'difference': weekend_data.mean() - weekday_data.mean(),
                'significant': p_value < 0.05,
                'p_value': p_value
            }
        
        return {'significant': False}
    
    def _detect_anomalies(self, series: pd.Series) -> List[Dict]:
        """
        异常检测
        """
        # Z-score方法
        z_scores = np.abs(stats.zscore(series))
        anomalies = []
        
        for idx, (date, value) in enumerate(series.items()):
            if z_scores[idx] > 2.5:  # 异常阈值
                anomalies.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': value,
                    'z_score': z_scores[idx],
                    'type': 'statistical_outlier'
                })
        
        return anomalies
    
    def _forecast_trend(self, series: pd.Series, days: int = 7) -> Dict:
        """
        趋势预测
        """
        x = np.arange(len(series)).reshape(-1, 1)
        y = series.values
        
        model = LinearRegression()
        model.fit(x, y)
        
        # 预测未来数值
        future_x = np.arange(len(series), len(series) + days).reshape(-1, 1)
        forecast = model.predict(future_x)
        
        # 计算预测区间(简化版)
        residuals = y - model.predict(x)
        mse = np.mean(residuals ** 2)
        std_error = np.sqrt(mse)
        
        forecast_dates = pd.date_range(
            start=series.index[-1] + timedelta(days=1),
            periods=days,
            freq='D'
        )
        
        forecast_data = []
        for i, date in enumerate(forecast_dates):
            forecast_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'predicted_value': forecast[i],
                'lower_bound': forecast[i] - 1.96 * std_error,
                'upper_bound': forecast[i] + 1.96 * std_error
            })
        
        return {
            'forecasts': forecast_data,
            'model_accuracy': model.score(x, y),
            'prediction_interval': '95%'
        }
```

### 时间序列图表组件
```typescript
// components/Analysis/TimeSeriesChart.tsx
interface TimeSeriesChartProps {
  dimension: string;
  timeSeriesData: TimeSeriesData;
  showForecast?: boolean;
  showAnomalies?: boolean;
}

interface TimeSeriesData {
  raw_data: Record<string, number>;
  trend_analysis: TrendAnalysis;
  seasonality: SeasonalityAnalysis;
  anomalies: Anomaly[];
  forecast: ForecastData;
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({
  dimension,
  timeSeriesData,
  showForecast = true,
  showAnomalies = true
}) => {
  const chartData = useMemo(() => {
    const historical = Object.entries(timeSeriesData.raw_data).map(([date, value]) => ({
      date,
      value,
      type: 'historical',
      isAnomaly: timeSeriesData.anomalies.some(a => a.date === date)
    }));

    const forecast = showForecast ? timeSeriesData.forecast.forecasts.map(f => ({
      date: f.date,
      value: f.predicted_value,
      type: 'forecast',
      lowerBound: f.lower_bound,
      upperBound: f.upper_bound
    })) : [];

    return [...historical, ...forecast];
  }, [timeSeriesData, showForecast]);

  return (
    <div className="time-series-chart">
      <div className="chart-header">
        <h4>{getDimensionLabel(dimension)} 时间趋势</h4>
        <div className="trend-info">
          趋势: {timeSeriesData.trend_analysis.direction} 
          ({timeSeriesData.trend_analysis.strength})
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tickFormatter={(date) => new Date(date).toLocaleDateString()}
          />
          <YAxis domain={['dataMin - 5%', 'dataMax + 5%']} />
          <Tooltip content={<CustomTimeSeriesTooltip />} />
          
          {/* 历史数据线 */}
          <Line
            type="monotone"
            dataKey="value"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            connectNulls={false}
          />
          
          {/* 预测数据线 */}
          {showForecast && (
            <Line
              type="monotone"
              dataKey="value"
              stroke="#10b981"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              connectNulls={false}
            />
          )}
          
          {/* 异常点标记 */}
          {showAnomalies && (
            <Scatter
              data={chartData.filter(d => d.isAnomaly)}
              fill="#ef4444"
              shape="triangle"
            />
          )}
        </LineChart>
      </ResponsiveContainer>

      <div className="chart-insights">
        <TrendInsights trendAnalysis={timeSeriesData.trend_analysis} />
        {timeSeriesData.seasonality.significant && (
          <SeasonalityInsights seasonality={timeSeriesData.seasonality} />
        )}
      </div>
    </div>
  );
};
```

## 依赖关系

**前置依赖**: E3S1 (相关性算法实现) - 需要数据分析能力  
**后续任务**: E3S5 (个性化洞察生成) - 时间分析为洞察提供数据支持

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 时间序列图表准确展示趋势
- [ ] 周期性模式识别功能正常
- [ ] 异常检测准确且有用
- [ ] 趋势预测功能可靠
- [ ] 用户界面直观易用

---

**任务负责人**: [待分配]  
**创建时间**: 2024年  
**最后更新**: 2024年