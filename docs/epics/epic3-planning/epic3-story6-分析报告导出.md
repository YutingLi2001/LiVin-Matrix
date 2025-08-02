# E3S6: 分析报告导出

## 任务概述

**任务ID**: E3S6  
**任务标题**: 分析报告导出  
**所属Epic**: Epic 3 - 矩阵分析与可视化  
**预估时间**: 3天  
**优先级**: 高  

## 任务目标

作为用户，我希望能导出我的数据分析报告，以便长期保存或分享。实现多格式的数据导出功能，包括原始数据、分析结果和可视化报告的完整导出。

## 详细的验收标准

### 1. CSV格式的原始数据导出功能
- [ ] 用户日常记录数据CSV导出
- [ ] 包含所有6个维度的完整数据字段
- [ ] 支持日期范围选择导出（最近30天/90天/全部）
- [ ] CSV文件名包含用户ID和导出时间戳
- [ ] 数据编码使用UTF-8确保中文正常显示
- [ ] 导出进度指示器和完成通知

### 2. JSON格式的结构化数据导出
- [ ] 原始数据的JSON格式导出
- [ ] 包含数据元信息（用户信息、导出时间、数据范围）
- [ ] 嵌套结构支持：用户->日期->维度数据
- [ ] 运动训练子记录的完整结构化导出
- [ ] JSON格式化输出，便于程序化处理
- [ ] 数据完整性校验和错误处理

### 3. 包含相关性矩阵的数据导出
- [ ] 6x6相关性矩阵的CSV格式导出
- [ ] 包含相关系数和p值的完整矩阵
- [ ] 矩阵计算参数记录（时间窗口、样本量等）
- [ ] 相关性显著性标注和说明
- [ ] 矩阵数据的JSON格式备选导出
- [ ] 相关性计算方法和统计信息的文档说明

### 4. 导出文件的数据完整性验证
- [ ] 导出前数据完整性检查
- [ ] 文件生成后的校验和计算
- [ ] 空值和异常数据的标识处理
- [ ] 导出数据量与原始数据量的对比验证
- [ ] 文件损坏检测和重新生成机制
- [ ] 导出日志记录和错误追踪

### 5. 下载功能的用户体验优化
- [ ] 一键导出按钮，支持多格式选择
- [ ] 大文件导出的进度条显示
- [ ] 导出完成后的自动下载触发
- [ ] 导出历史记录和管理
- [ ] 移动端友好的下载体验
- [ ] 导出失败时的重试机制

## 技术实现要点

### 数据导出服务
```python
# app/services/export_service.py
import csv
import json
import zipfile
from datetime import datetime, date
from typing import Dict, List, Optional
from io import StringIO, BytesIO
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

class ExportService:
    
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'xlsx']
    
    async def export_user_data(self, 
                             user_id: str,
                             export_format: str,
                             date_range: Optional[tuple] = None,
                             include_analysis: bool = True) -> StreamingResponse:
        """
        导出用户数据
        """
        if export_format not in self.supported_formats:
            raise HTTPException(status_code=400, detail="不支持的导出格式")
        
        # 获取用户数据
        user_data = await self._get_user_export_data(user_id, date_range)
        
        if export_format == 'csv':
            return await self._export_csv(user_data, user_id)
        elif export_format == 'json':
            return await self._export_json(user_data, user_id, include_analysis)
        else:
            raise HTTPException(status_code=400, detail="格式暂不支持")
    
    async def _get_user_export_data(self, 
                                  user_id: str, 
                                  date_range: Optional[tuple]) -> Dict:
        """
        获取导出数据
        """
        # 获取基础用户数据
        daily_records = await self.daily_record_service.get_user_records(
            user_id=user_id,
            start_date=date_range[0] if date_range else None,
            end_date=date_range[1] if date_range else None
        )
        
        # 获取分析数据
        correlation_data = await self.correlation_service.calculate_correlation_matrix(
            daily_records, time_window=30
        )
        
        # 获取洞察数据
        insights = await self.insights_service.generate_comprehensive_insights(
            correlation_data, {}, user_id
        )
        
        return {
            'user_info': await self._get_user_info(user_id),
            'daily_records': daily_records,
            'correlation_analysis': correlation_data,
            'insights': insights,
            'export_metadata': {
                'exported_at': datetime.utcnow().isoformat(),
                'date_range': date_range,
                'total_records': len(daily_records)
            }
        }
    
    async def _export_csv(self, data: Dict, user_id: str) -> StreamingResponse:
        """
        CSV格式导出
        """
        output = StringIO()
        
        # 准备CSV数据
        fieldnames = [
            'record_date', 'sleep_start_time', 'sleep_end_time', 'sleep_quality', 'wake_clarity',
            'calories', 'protein', 'fat', 'carbohydrates',
            'total_workout_duration', 'daily_steps',
            'overall_mood', 'stress_level', 'anxiety_level', 'energy_level',
            'deep_work_hours', 'active_breaks', 'focus_quality', 'task_completion', 
            'work_satisfaction', 'work_environment',
            'initiated_social', 'responded_social', 'interpersonal_satisfaction', 'solitude_satisfaction'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        # 写入数据行
        for record in data['daily_records']:
            # 数据清洗和格式化
            row_data = {}
            for field in fieldnames:
                value = record.get(field)
                if value is not None:
                    if isinstance(value, (date, datetime)):
                        row_data[field] = value.isoformat()
                    else:
                        row_data[field] = value
                else:
                    row_data[field] = ''
            writer.writerow(row_data)
        
        output.seek(0)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"livin_matrix_data_{user_id}_{timestamp}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    async def _export_json(self, 
                         data: Dict, 
                         user_id: str, 
                         include_analysis: bool = True) -> StreamingResponse:
        """
        JSON格式导出
        """
        # 准备JSON数据结构
        export_data = {
            'format_version': '1.0',
            'export_info': {
                'user_id': user_id,
                'exported_at': data['export_metadata']['exported_at'],
                'data_range': data['export_metadata']['date_range'],
                'total_records': data['export_metadata']['total_records']
            },
            'user_profile': data['user_info'],
            'daily_records': []
        }
        
        # 处理日常记录数据
        for record in data['daily_records']:
            record_data = {}
            for key, value in record.items():
                if isinstance(value, (date, datetime)):
                    record_data[key] = value.isoformat()
                else:
                    record_data[key] = value
            export_data['daily_records'].append(record_data)
        
        # 包含分析数据
        if include_analysis:
            export_data['analysis'] = {
                'correlation_matrix': data['correlation_analysis'],
                'insights': data['insights']
            }
        
        # 序列化JSON
        json_output = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"livin_matrix_complete_{user_id}_{timestamp}.json"
        
        return StreamingResponse(
            iter([json_output]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    async def export_correlation_matrix(self, 
                                      correlation_data: Dict,
                                      user_id: str) -> StreamingResponse:
        """
        导出相关性矩阵
        """
        output = StringIO()
        
        # 获取维度列表
        dimensions = list(correlation_data['correlations'].keys())
        
        # 写入相关系数矩阵
        writer = csv.writer(output)
        
        # 写入标题行
        header = ['Dimension'] + dimensions
        writer.writerow(header)
        
        # 写入数据行
        for dim1 in dimensions:
            row = [dim1]
            for dim2 in dimensions:
                corr_value = correlation_data['correlations'][dim1][dim2]
                p_value = correlation_data['p_values'][dim1][dim2]
                
                # 格式：相关系数(p值)
                cell_value = f"{corr_value:.3f}"
                if p_value < 0.05:
                    if p_value < 0.001:
                        cell_value += "***"
                    elif p_value < 0.01:
                        cell_value += "**"
                    else:
                        cell_value += "*"
                
                row.append(cell_value)
            writer.writerow(row)
        
        # 添加说明信息
        writer.writerow([])
        writer.writerow(['说明: *p<0.05, **p<0.01, ***p<0.001'])
        writer.writerow([f'样本量: {correlation_data["sample_size"]}'])
        writer.writerow([f'时间窗口: {correlation_data["time_window"]}天'])
        writer.writerow([f'计算时间: {correlation_data["calculated_at"]}'])
        
        output.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"correlation_matrix_{user_id}_{timestamp}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
```

### 前端导出组件
```typescript
// components/Export/ExportPanel.tsx
interface ExportPanelProps {
  userId: string;
  onExportComplete: (filename: string) => void;
}

const ExportPanel: React.FC<ExportPanelProps> = ({ userId, onExportComplete }) => {
  const [exportFormat, setExportFormat] = useState<'csv' | 'json'>('csv');
  const [dateRange, setDateRange] = useState<[Date, Date]>([
    new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    new Date()
  ]);
  const [includeAnalysis, setIncludeAnalysis] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);

  const handleExport = async () => {
    setIsExporting(true);
    setExportProgress(0);

    try {
      const params = new URLSearchParams({
        format: exportFormat,
        start_date: dateRange[0].toISOString().split('T')[0],
        end_date: dateRange[1].toISOString().split('T')[0],
        include_analysis: includeAnalysis.toString()
      });

      // 使用fetch监控下载进度
      const response = await fetch(`/api/v1/export/user-data?${params}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error('导出请求失败');
      }

      // 创建下载链接
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // 从响应头获取文件名
      const contentDisposition = response.headers.get('Content-Disposition');
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : `export_${Date.now()}.${exportFormat}`;
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      onExportComplete(filename);
      
    } catch (error) {
      console.error('导出失败:', error);
      // 显示错误通知
    } finally {
      setIsExporting(false);
      setExportProgress(0);
    }
  };

  return (
    <div className="export-panel">
      <h3>数据导出</h3>
      
      <div className="export-options">
        <div className="option-group">
          <label>导出格式</label>
          <div className="format-selector">
            <button
              className={`format-btn ${exportFormat === 'csv' ? 'active' : ''}`}
              onClick={() => setExportFormat('csv')}
            >
              CSV (表格数据)
            </button>
            <button
              className={`format-btn ${exportFormat === 'json' ? 'active' : ''}`}
              onClick={() => setExportFormat('json')}
            >
              JSON (结构化数据)
            </button>
          </div>
        </div>

        <div className="option-group">
          <label>日期范围</label>
          <DateRangePicker
            value={dateRange}
            onChange={setDateRange}
            maxDate={new Date()}
          />
        </div>

        {exportFormat === 'json' && (
          <div className="option-group">
            <label>
              <input
                type="checkbox"
                checked={includeAnalysis}
                onChange={(e) => setIncludeAnalysis(e.target.checked)}
              />
              包含分析结果（相关性矩阵、洞察等）
            </label>
          </div>
        )}
      </div>

      <div className="export-actions">
        <button
          className="export-btn"
          onClick={handleExport}
          disabled={isExporting}
        >
          {isExporting ? '导出中...' : '开始导出'}
        </button>

        {isExporting && (
          <div className="export-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${exportProgress}%` }}
              />
            </div>
            <span>导出进度: {exportProgress}%</span>
          </div>
        )}
      </div>

      <div className="export-info">
        <h4>导出说明</h4>
        <ul>
          <li><strong>CSV格式</strong>: 适合Excel等表格软件打开，包含原始数据</li>
          <li><strong>JSON格式</strong>: 适合程序化处理，可选择包含分析结果</li>
          <li>导出数据包含选定日期范围内的所有6个维度数据</li>
          <li>大文件导出可能需要较长时间，请耐心等待</li>
        </ul>
      </div>
    </div>
  );
};
```

## 依赖关系

**前置依赖**: 
- E3S2 (矩阵可视化) - 需要相关性矩阵数据
- E3S5 (个性化洞察) - 可选包含洞察数据

**后续任务**: 无（Epic 3的最后一个任务）

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] CSV和JSON格式导出功能正常
- [ ] 相关性矩阵导出准确
- [ ] 数据完整性验证可靠
- [ ] 用户体验优化良好
- [ ] 大文件导出性能acceptable
- [ ] 导出功能有充分测试覆盖

---

**任务负责人**: [待分配]  
**创建时间**: 2024年  
**最后更新**: 2024年