# E3S1: 相关性算法实现

## 任务概述

**任务ID**: E3S1  
**任务标题**: 相关性算法实现  
**所属Epic**: Epic 3 - 矩阵分析与可视化  
**预估时间**: 4天  
**优先级**: 高  

## 任务目标

作为系统，我需要计算不同维度间的统计相关性，以便为用户提供数据洞察。实现皮尔逊相关系数计算、统计显著性检验和多时间窗口分析，为矩阵可视化提供核心算法支持。

## 详细的验收标准

### 1. 皮尔逊相关系数计算算法实现
- [ ] 皮尔逊相关系数公式正确实现：r = Σ[(xi-x̄)(yi-ȳ)] / √[Σ(xi-x̄)²Σ(yi-ȳ)²]
- [ ] 处理6个维度共15对相关性组合(6×6矩阵的上三角)
- [ ] 数值计算精度保证：使用适当的数值稳定算法
- [ ] 边界情况处理：标准差为0时的处理
- [ ] 算法性能优化：大数据集的高效计算
- [ ] 计算结果验证：与标准统计库结果对比验证

### 2. 统计显著性检验（p值计算）
- [ ] t检验实现：t = r√[(n-2)/(1-r²)]，其中n为样本数
- [ ] p值计算：基于t分布的双尾检验
- [ ] 显著性水平设定：α=0.05, 0.01, 0.001三个水平
- [ ] 显著性标注：*, **, ***分别对应不同显著性水平
- [ ] 自由度计算：df = n-2的正确应用
- [ ] 置信区间计算：95%置信区间的Fisher变换

### 3. 支持时间窗口选择（最近30天、90天、全部数据）
- [ ] 灵活时间窗口：用户可选择分析时间范围
- [ ] 30天窗口：最近一个月的相关性分析
- [ ] 90天窗口：最近三个月的季度分析
- [ ] 全部数据：用户历史所有数据的分析
- [ ] 动态计算：时间窗口变化时重新计算相关性
- [ ] 样本量检查：确保时间窗口内有足够数据进行分析

### 4. 处理缺失数据的策略实现
- [ ] 成对删除（Pairwise deletion）：只删除缺失维度的数据点
- [ ] 列表删除（Listwise deletion）：删除任一维度缺失的完整记录
- [ ] 插值填充：基于趋势的简单插值方法
- [ ] 缺失数据统计：报告每个维度的数据完整性
- [ ] 最小样本量：相关性计算的最小数据要求(n≥10)
- [ ] 缺失模式分析：识别数据缺失的模式

### 5. 相关性计算API端点（POST /api/v1/analysis/correlation）
- [ ] API端点实现：接收时间窗口和用户ID参数
- [ ] 请求参数验证：时间范围、用户权限验证
- [ ] 响应格式标准化：6×6相关性矩阵JSON格式
- [ ] 计算缓存：相同参数的结果缓存1小时
- [ ] 异步处理：大数据集的后台计算支持
- [ ] 错误处理：数据不足、计算失败的友好错误信息

## 技术实现要点

### 相关性计算核心算法
```python
# app/services/correlation_service.py
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

class CorrelationService:
    
    def calculate_pearson_correlation(self, x: List[float], y: List[float]) -> Tuple[float, float]:
        """
        计算皮尔逊相关系数和p值
        Returns: (correlation_coefficient, p_value)
        """
        # 移除缺失值对
        valid_pairs = [(xi, yi) for xi, yi in zip(x, y) if xi is not None and yi is not None]
        
        if len(valid_pairs) < 10:  # 最小样本量要求
            return 0.0, 1.0
            
        x_clean, y_clean = zip(*valid_pairs)
        
        # 计算皮尔逊相关系数
        correlation, p_value = stats.pearsonr(x_clean, y_clean)
        
        return correlation, p_value
    
    def calculate_correlation_matrix(self, 
                                   user_data: List[Dict],
                                   time_window: int = 30) -> Dict:
        """
        计算6×6维度相关性矩阵
        """
        dimensions = [
            'sleep_quality', 'calories', 'total_workout_duration',
            'overall_mood', 'deep_work_hours', 'interpersonal_satisfaction'
        ]
        
        # 构建数据矩阵
        data_matrix = {}
        for dim in dimensions:
            data_matrix[dim] = [record.get(dim) for record in user_data]
        
        # 计算相关性矩阵
        correlation_matrix = {}
        p_value_matrix = {}
        
        for i, dim1 in enumerate(dimensions):
            correlation_matrix[dim1] = {}
            p_value_matrix[dim1] = {}
            
            for j, dim2 in enumerate(dimensions):
                if i <= j:  # 只计算上三角矩阵
                    corr, p_val = self.calculate_pearson_correlation(
                        data_matrix[dim1], 
                        data_matrix[dim2]
                    )
                    correlation_matrix[dim1][dim2] = round(corr, 3)
                    p_value_matrix[dim1][dim2] = round(p_val, 4)
                else:
                    # 对称矩阵
                    correlation_matrix[dim1][dim2] = correlation_matrix[dim2][dim1]
                    p_value_matrix[dim1][dim2] = p_value_matrix[dim2][dim1]
        
        return {
            'correlations': correlation_matrix,
            'p_values': p_value_matrix,
            'sample_size': len(user_data),
            'time_window': time_window,
            'calculated_at': datetime.utcnow().isoformat()
        }
```

### API端点实现
```python
# app/routers/analysis.py
from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.correlation_service import CorrelationService
from app.services.daily_record_service import DailyRecordService

router = APIRouter()

@router.post("/analysis/correlation")
async def calculate_correlation(
    time_window: int = Query(30, description="时间窗口(天)", ge=7, le=365),
    current_user: User = Depends(get_current_user),
    correlation_service: CorrelationService = Depends(),
    record_service: DailyRecordService = Depends()
):
    try:
        # 获取用户数据
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=time_window)
        
        user_records = await record_service.get_user_records(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        if len(user_records) < 10:
            raise HTTPException(
                status_code=400, 
                detail=f"数据量不足，需要至少10天的记录，当前只有{len(user_records)}天"
            )
        
        # 计算相关性矩阵
        correlation_result = correlation_service.calculate_correlation_matrix(
            user_records, time_window
        )
        
        return APIResponse(
            success=True,
            data=correlation_result,
            message="相关性分析完成"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析计算失败: {str(e)}")
```

### 数据预处理
```python
# app/utils/data_preprocessing.py
def preprocess_correlation_data(raw_data: List[Dict]) -> Dict[str, List[float]]:
    """
    预处理相关性分析数据
    """
    dimension_mapping = {
        'sleep': ['sleep_quality', 'wake_clarity'],
        'nutrition': ['calories', 'protein'],
        'exercise': ['total_workout_duration', 'daily_steps'],
        'mood': ['overall_mood', 'energy_level'],
        'productivity': ['deep_work_hours', 'focus_quality'],
        'social': ['interpersonal_satisfaction', 'solitude_satisfaction']
    }
    
    processed_data = {}
    
    for category, fields in dimension_mapping.items():
        # 复合维度计算平均值
        category_values = []
        for record in raw_data:
            values = [record.get(field) for field in fields if record.get(field) is not None]
            if values:
                category_values.append(sum(values) / len(values))
            else:
                category_values.append(None)
        
        processed_data[category] = category_values
    
    return processed_data
```

## 依赖关系

**前置依赖**: Epic 2完成 - 需要完整的历史数据API  
**后续任务**: E3S2 (矩阵可视化) - 需要相关性计算结果

## 预估时间分解

- **第1天**: 皮尔逊相关系数算法实现和验证
- **第2天**: 统计显著性检验和p值计算
- **第3天**: 时间窗口支持和缺失数据处理
- **第4天**: API端点实现、缓存优化和测试

## 风险点和缓解策略

### 风险点
1. **算法准确性**: 统计计算可能存在数值误差
2. **性能问题**: 大数据集的相关性计算耗时
3. **数据质量**: 缺失和异常数据影响分析结果
4. **统计理解**: 相关性结果的正确解释

### 缓解策略
1. 使用成熟的统计库(scipy.stats)，充分单元测试
2. 实施计算缓存和异步处理机制
3. 建立完善的数据预处理和质量检查流程
4. 提供统计解释文档和用户指导

## 验证方法

### 算法准确性验证
- 使用标准数据集验证算法结果
- 与R/Python统计库结果对比
- 边界情况测试(完全相关、无相关、缺失数据)

### 性能验证
- 1000条记录的计算时间 < 2秒
- 并发计算支持至少10个用户
- 内存使用优化，避免大数据集内存溢出

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 相关性算法准确性验证通过
- [ ] API端点功能完整且性能达标
- [ ] 缺失数据处理策略完善
- [ ] 统计显著性检验正确实现
- [ ] 多时间窗口分析支持
- [ ] 算法有充分的单元测试覆盖

---

**任务负责人**: [待分配]  
**创建时间**: 2024年  
**最后更新**: 2024年