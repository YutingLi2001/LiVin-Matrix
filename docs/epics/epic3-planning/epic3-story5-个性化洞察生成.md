# E3S5: 个性化洞察生成

## 任务概述

**任务ID**: E3S5  
**任务标题**: 个性化洞察生成  
**所属Epic**: Epic 3 - 矩阵分析与可视化  
**预估时间**: 3天  
**优先级**: 高  

## 任务目标

作为用户，我希望系统能为我生成个性化的数据洞察，以便获得行动建议。基于相关性分析和时间序列分析结果，自动生成个性化的洞察报告和改进建议。

## 详细的验收标准

### 1. 基于相关性分析的自动洞察生成
- [ ] 相关性强度分析：识别强、中、弱相关关系
- [ ] 因果关系推测：基于相关性的可能因果关系
- [ ] 反向相关识别：负相关关系的特殊标注
- [ ] 相关性稳定性：跨时间窗口的相关性一致性分析
- [ ] 洞察置信度：基于统计显著性的洞察可靠程度
- [ ] 洞察更新频率：基于新数据的洞察动态更新

### 2. 识别用户的前3个最强相关性关系
- [ ] 相关性排序：按绝对相关系数排序所有维度对
- [ ] Top3筛选：选择最强的3个相关性关系
- [ ] 正负区分：分别识别最强正相关和负相关
- [ ] 显著性过滤：只包含统计显著的相关性
- [ ] 实用性评估：优先选择对生活改善有意义的相关性
- [ ] 动态调整：随时间推移动态更新Top3关系

### 3. 生成简单易懂的洞察文本描述
- [ ] 自然语言生成：将统计结果转换为易懂的文字
- [ ] 洞察模板库：预定义的洞察描述模板
- [ ] 个性化定制：基于用户数据的个性化表述
- [ ] 情境化解释：结合具体数值和时间的解释
- [ ] 渐进式披露：从概要到详细的分层描述
- [ ] 多语言支持：支持中英文洞察描述

### 4. 异常模式的识别和提醒
- [ ] 异常相关性：识别突然出现或消失的相关性
- [ ] 异常数值：单维度的异常高低值提醒
- [ ] 模式突变：用户行为模式的显著变化
- [ ] 健康风险识别：基于异常模式的健康风险提醒
- [ ] 异常程度评级：轻微、中等、严重的异常分级
- [ ] 异常处理建议：针对不同异常的应对建议

### 5. 基础的改进建议生成
- [ ] 行为改进建议：基于相关性的行为调整建议
- [ ] 优先级排序：按改进潜力排序建议
- [ ] 可操作性检查：确保建议具有可操作性
- [ ] 渐进式改进：避免激进的改变建议
- [ ] 个性化调整：基于用户历史数据的建议定制
- [ ] 进度跟踪：建议实施后的效果跟踪机制

## 技术实现要点

### 洞察生成服务
```python
# app/services/insights_service.py
from typing import Dict, List, Tuple
import random
from datetime import datetime

class InsightsService:
    
    def __init__(self):
        self.insight_templates = {
            'strong_positive': [
                "你的{dim1}与{dim2}呈现强正相关关系(r={corr:.3f})，这意味着改善{dim1}很可能同时提升{dim2}。",
                "数据显示{dim1}和{dim2}密切相关(r={corr:.3f})，当{dim1}表现好时，{dim2}往往也会有好的表现。"
            ],
            'strong_negative': [
                "你的{dim1}与{dim2}呈现负相关关系(r={corr:.3f})，当{dim1}增加时，{dim2}往往会下降。",
                "注意到{dim1}和{dim2}之间存在负相关(r={corr:.3f})，保持适度的{dim1}可能有助于{dim2}的表现。"
            ],
            'improvement_suggestions': {
                'sleep_quality': [
                    "建议保持规律的作息时间，睡前1小时避免使用电子设备",
                    "尝试创建舒适的睡眠环境，保持室温在18-22度之间"
                ],
                'exercise': [
                    "可以尝试每天增加10-15分钟的轻度运动",
                    "将运动融入日常生活，比如走楼梯代替电梯"
                ],
                'mood': [
                    "考虑每天记录3件感恩的事情，有助于提升整体心情",
                    "适当的社交活动和户外时间可能对情绪有积极影响"
                ]
            }
        }
    
    def generate_comprehensive_insights(self, 
                                      correlation_data: Dict,
                                      time_series_data: Dict,
                                      user_id: str) -> Dict:
        """
        生成综合洞察报告
        """
        insights = {
            'top_correlations': self._analyze_top_correlations(correlation_data),
            'trend_insights': self._analyze_trends(time_series_data),
            'anomaly_alerts': self._identify_anomalies(time_series_data),
            'improvement_suggestions': self._generate_suggestions(correlation_data, time_series_data),
            'generated_at': datetime.utcnow().isoformat(),
            'confidence_score': self._calculate_confidence(correlation_data)
        }
        
        return insights
    
    def _analyze_top_correlations(self, correlation_data: Dict) -> List[Dict]:
        """
        分析前3个最强相关性
        """
        correlations = []
        
        for dim1, dim1_data in correlation_data['correlations'].items():
            for dim2, corr_value in dim1_data.items():
                if dim1 != dim2:  # 排除自相关
                    p_value = correlation_data['p_values'][dim1][dim2]
                    if p_value < 0.05:  # 只包含显著相关
                        correlations.append({
                            'dimension1': dim1,
                            'dimension2': dim2,
                            'correlation': corr_value,
                            'p_value': p_value,
                            'strength': self._get_correlation_strength(abs(corr_value))
                        })
        
        # 按相关性强度排序，取前3个
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        top_3 = correlations[:3]
        
        # 生成洞察文本
        insights = []
        for corr in top_3:
            insight_text = self._generate_correlation_insight(corr)
            insights.append({
                **corr,
                'insight': insight_text,
                'actionable': True
            })
        
        return insights
    
    def _generate_correlation_insight(self, correlation: Dict) -> str:
        """
        生成相关性洞察文本
        """
        dim1_label = self._get_dimension_label(correlation['dimension1'])
        dim2_label = self._get_dimension_label(correlation['dimension2'])
        corr_value = correlation['correlation']
        
        if corr_value > 0.5:
            template = random.choice(self.insight_templates['strong_positive'])
        elif corr_value < -0.5:
            template = random.choice(self.insight_templates['strong_negative'])
        else:
            template = "你的{dim1}与{dim2}存在{strength}相关关系(r={corr:.3f})。"
        
        return template.format(
            dim1=dim1_label,
            dim2=dim2_label,
            corr=corr_value,
            strength=correlation['strength']
        )
    
    def _generate_suggestions(self, 
                            correlation_data: Dict,
                            time_series_data: Dict) -> List[Dict]:
        """
        生成改进建议
        """
        suggestions = []
        
        # 基于相关性的建议
        for insight in self._analyze_top_correlations(correlation_data):
            if insight['correlation'] > 0.5:
                # 正相关：建议同时改进两个维度
                suggestion = {
                    'type': 'correlation_based',
                    'priority': 'high',
                    'title': f"同时改善{self._get_dimension_label(insight['dimension1'])}和{self._get_dimension_label(insight['dimension2'])}",
                    'description': f"由于这两个维度高度正相关，改善其中一个很可能带动另一个的提升。",
                    'specific_actions': self._get_specific_actions(insight['dimension1']) + 
                                     self._get_specific_actions(insight['dimension2'])
                }
                suggestions.append(suggestion)
        
        # 基于趋势的建议
        for dim, trend_data in time_series_data.items():
            if trend_data['trend_analysis']['direction'] == '下降':
                suggestion = {
                    'type': 'trend_based',
                    'priority': 'medium',
                    'title': f"关注{self._get_dimension_label(dim)}的下降趋势",
                    'description': f"最近{self._get_dimension_label(dim)}呈下降趋势，建议采取措施改善。",
                    'specific_actions': self._get_specific_actions(dim)
                }
                suggestions.append(suggestion)
        
        # 按优先级排序
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        suggestions.sort(key=lambda x: priority_order[x['priority']], reverse=True)
        
        return suggestions[:5]  # 返回前5个建议
    
    def _get_specific_actions(self, dimension: str) -> List[str]:
        """
        获取特定维度的改进行动
        """
        return self.insight_templates['improvement_suggestions'].get(
            dimension, 
            ["保持关注该维度的变化，寻找改进机会"]
        )
    
    def _identify_anomalies(self, time_series_data: Dict) -> List[Dict]:
        """
        识别异常模式
        """
        alerts = []
        
        for dimension, data in time_series_data.items():
            anomalies = data.get('anomalies', [])
            if len(anomalies) > 0:
                recent_anomalies = [a for a in anomalies if self._is_recent(a['date'])]
                if recent_anomalies:
                    alert = {
                        'dimension': dimension,
                        'type': 'recent_anomaly',
                        'severity': 'medium',
                        'message': f"最近在{self._get_dimension_label(dimension)}中检测到{len(recent_anomalies)}个异常值",
                        'details': recent_anomalies,
                        'suggestion': f"建议回顾最近影响{self._get_dimension_label(dimension)}的因素"
                    }
                    alerts.append(alert)
        
        return alerts
```

### 洞察展示组件
```typescript
// components/Analysis/InsightsPanel.tsx
interface InsightsPanelProps {
  insights: ComprehensiveInsights;
  onSuggestionClick: (suggestion: Suggestion) => void;
}

interface ComprehensiveInsights {
  top_correlations: CorrelationInsight[];
  trend_insights: TrendInsight[];
  anomaly_alerts: AnomalyAlert[];
  improvement_suggestions: Suggestion[];
  confidence_score: number;
  generated_at: string;
}

const InsightsPanel: React.FC<InsightsPanelProps> = ({
  insights,
  onSuggestionClick
}) => {
  return (
    <div className="insights-panel">
      <div className="insights-header">
        <h2>个性化洞察</h2>
        <div className="confidence-indicator">
          置信度: {(insights.confidence_score * 100).toFixed(0)}%
        </div>
      </div>

      <div className="insights-content">
        {/* 关键发现 */}
        <section className="key-findings">
          <h3>关键发现</h3>
          {insights.top_correlations.map((insight, index) => (
            <div key={index} className="insight-card">
              <div className="insight-icon">
                {insight.correlation > 0 ? '📈' : '📉'}
              </div>
              <div className="insight-content">
                <div className="insight-text">{insight.insight}</div>
                <div className="insight-meta">
                  强度: {insight.strength} | 
                  显著性: p = {insight.p_value.toFixed(4)}
                </div>
              </div>
            </div>
          ))}
        </section>

        {/* 异常提醒 */}
        {insights.anomaly_alerts.length > 0 && (
          <section className="anomaly-alerts">
            <h3>异常提醒</h3>
            {insights.anomaly_alerts.map((alert, index) => (
              <div key={index} className={`alert-card severity-${alert.severity}`}>
                <div className="alert-icon">⚠️</div>
                <div className="alert-content">
                  <div className="alert-message">{alert.message}</div>
                  <div className="alert-suggestion">{alert.suggestion}</div>
                </div>
              </div>
            ))}
          </section>
        )}

        {/* 改进建议 */}
        <section className="improvement-suggestions">
          <h3>改进建议</h3>
          {insights.improvement_suggestions.map((suggestion, index) => (
            <div key={index} className="suggestion-card">
              <div className="suggestion-header">
                <span className={`priority-badge priority-${suggestion.priority}`}>
                  {suggestion.priority === 'high' ? '高优先级' : '中优先级'}
                </span>
                <h4>{suggestion.title}</h4>
              </div>
              <div className="suggestion-description">
                {suggestion.description}
              </div>
              <div className="suggestion-actions">
                <ul>
                  {suggestion.specific_actions.map((action, actionIndex) => (
                    <li key={actionIndex}>{action}</li>
                  ))}
                </ul>
              </div>
              <button 
                className="suggestion-action-btn"
                onClick={() => onSuggestionClick(suggestion)}
              >
                查看详细计划
              </button>
            </div>
          ))}
        </section>
      </div>

      <div className="insights-footer">
        <div className="last-updated">
          最后更新: {new Date(insights.generated_at).toLocaleString()}
        </div>
        <button className="refresh-insights-btn">
          刷新洞察
        </button>
      </div>
    </div>
  );
};
```

## 依赖关系

**前置依赖**: 
- E3S1 (相关性算法实现) - 需要相关性数据
- E3S4 (时间维度分析) - 需要趋势分析数据

**后续任务**: E3S6 (分析报告导出) - 洞察内容可包含在导出报告中

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 自动洞察生成准确且有用
- [ ] Top3相关性识别正确
- [ ] 洞察文本简单易懂
- [ ] 异常检测及时准确
- [ ] 改进建议具体可操作
- [ ] 用户界面友好直观

---

**任务负责人**: [待分配]  
**创建时间**: 2024年  
**最后更新**: 2024年