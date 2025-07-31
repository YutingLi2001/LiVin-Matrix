# E2S3: 饮食维度数据录入

## 任务概述

**任务ID**: E2S3  
**任务标题**: 饮食维度数据录入  
**所属Epic**: Epic 2 - 数据管理核心  
**预估时间**: 2天  
**优先级**: 高  

## 任务目标

作为用户，我希望记录我的营养摄入，以便分析饮食对健康的影响。实现饮食维度的完整数据录入功能，包括营养素数值输入、快速预设模板、营养建议和智能默认值填充。

## 详细的验收标准

### 1. 营养素数值输入组件（卡路里、蛋白质、脂肪、碳水）
- [ ] 卡路里输入框：数字输入，单位kcal，范围0-5000
- [ ] 蛋白质输入框：数字输入，单位克，范围0-500
- [ ] 脂肪输入框：数字输入，单位克，范围0-500
- [ ] 碳水化合物输入框：数字输入，单位克，范围0-1000
- [ ] 输入验证：实时验证数值范围和格式
- [ ] 单位显示：每个输入框显示对应营养素单位

### 2. 快速预设模板（减脂餐、正常餐、增肌餐）
- [ ] 减脂餐模板：1200-1500kcal，高蛋白低脂
- [ ] 正常餐模板：1800-2200kcal，均衡营养配比
- [ ] 增肌餐模板：2500-3000kcal，高蛋白高碳水
- [ ] 模板选择按钮：一键填充对应数值
- [ ] 自定义模板：用户可保存常用的营养配比
- [ ] 模板预览：显示模板的详细营养信息

### 3. 营养建议提示（基于用户输入的合理性检查）
- [ ] 卡路里建议：基于常见成年人需求(1500-2500kcal)
- [ ] 营养配比检查：蛋白质15-25%，脂肪20-35%，碳水45-65%
- [ ] 异常值警告：超出合理范围时显示建议
- [ ] 营养素密度提示：蛋白质每kg体重1-2g建议
- [ ] 健康建议：基于输入数据提供简单健康提示
- [ ] 动态建议：输入变化时实时更新建议内容

### 4. 数据验证：各营养素在合理范围内（0-5000kcal等）
- [ ] 卡路里验证：0-5000kcal，超出范围显示错误
- [ ] 蛋白质验证：0-500g，异常值提示
- [ ] 脂肪验证：0-500g，过高时健康提醒
- [ ] 碳水验证：0-1000g，极值检查
- [ ] 必填验证：至少填写卡路里字段
- [ ] 逻辑验证：营养素总热量与输入卡路里的合理性检查

### 5. 智能默认值填充（基于历史平均值）
- [ ] 历史数据分析：计算用户过去30天平均值
- [ ] 智能推荐：基于历史数据推荐今日摄入量
- [ ] 趋势识别：识别用户饮食模式（减脂/增肌/维持）
- [ ] 个性化调整：基于用户目标调整默认值
- [ ] 新用户处理：无历史数据时使用通用健康标准
- [ ] 学习能力：系统根据用户习惯不断优化推荐

## 技术实现要点

### 饮食数据模型
```typescript
// types/NutritionData.ts
interface NutritionData {
  calories: number;           // kcal
  protein: number;           // 克
  fat: number;              // 克
  carbohydrates: number;    // 克
  recordDate: string;       // 记录日期
}

interface NutritionTemplate {
  id: string;
  name: string;
  description: string;
  nutrition: NutritionData;
  isCustom: boolean;
}

interface NutritionValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions: string[];
}
```

### 营养输入组件
```typescript
// components/NutritionEntry/NutritionInputs.tsx
const NutritionInputs: React.FC<{
  data: NutritionData;
  onChange: (data: NutritionData) => void;
}> = ({ data, onChange }) => {
  
  const nutritionFields = [
    { key: 'calories', label: '卡路里', unit: 'kcal', max: 5000 },
    { key: 'protein', label: '蛋白质', unit: 'g', max: 500 },
    { key: 'fat', label: '脂肪', unit: 'g', max: 500 },
    { key: 'carbohydrates', label: '碳水化合物', unit: 'g', max: 1000 }
  ];

  return (
    <div className="nutrition-inputs">
      {nutritionFields.map(field => (
        <div key={field.key} className="nutrition-input-group">
          <label>{field.label}</label>
          <div className="input-with-unit">
            <input
              type="number"
              min="0"
              max={field.max}
              value={data[field.key] || ''}
              onChange={(e) => updateField(field.key, parseInt(e.target.value) || 0)}
              placeholder="0"
            />
            <span className="unit">{field.unit}</span>
          </div>
        </div>
      ))}
    </div>
  );
};
```

### 模板选择组件
```typescript
// components/NutritionEntry/TemplateSelector.tsx  
const TemplateSelector: React.FC<{
  onSelectTemplate: (template: NutritionTemplate) => void;
}> = ({ onSelectTemplate }) => {
  
  const defaultTemplates: NutritionTemplate[] = [
    {
      id: 'weight-loss',
      name: '减脂餐',
      description: '低热量高蛋白，适合减脂期',
      nutrition: { calories: 1350, protein: 120, fat: 40, carbohydrates: 140 },
      isCustom: false
    },
    {
      id: 'normal',
      name: '正常餐', 
      description: '均衡营养，日常维持',
      nutrition: { calories: 2000, protein: 100, fat: 70, carbohydrates: 250 },
      isCustom: false
    },
    {
      id: 'muscle-gain',
      name: '增肌餐',
      description: '高蛋白高碳水，适合增肌期', 
      nutrition: { calories: 2750, protein: 150, fat: 80, carbohydrates: 350 },
      isCustom: false
    }
  ];

  return (
    <div className="template-selector">
      <h4>快速模板</h4>
      <div className="template-buttons">
        {defaultTemplates.map(template => (
          <button
            key={template.id}
            className="template-button"
            onClick={() => onSelectTemplate(template)}
          >
            <div className="template-name">{template.name}</div>
            <div className="template-calories">{template.nutrition.calories}kcal</div>
          </button>
        ))}
      </div>
    </div>
  );
};
```

### 营养建议系统
```typescript
// utils/nutritionAnalysis.ts
export const analyzeNutrition = (data: NutritionData): NutritionValidation => {
  const errors: string[] = [];
  const warnings: string[] = [];
  const suggestions: string[] = [];
  
  // 基础验证
  if (data.calories < 0 || data.calories > 5000) {
    errors.push('卡路里必须在0-5000之间');
  }
  
  // 营养配比分析
  const totalCaloriesFromMacros = 
    data.protein * 4 + data.fat * 9 + data.carbohydrates * 4;
  
  if (Math.abs(totalCaloriesFromMacros - data.calories) > 200) {
    warnings.push('营养素热量与总热量不匹配，请检查输入');
  }
  
  // 健康建议
  if (data.calories < 1200 && data.calories > 0) {
    warnings.push('热量摄入过低，可能影响基础代谢');
  }
  
  if (data.protein < data.calories * 0.15 / 4) {
    suggestions.push('建议增加蛋白质摄入，有助于肌肉维持');
  }
  
  if (data.fat > data.calories * 0.35 / 9) {
    suggestions.push('脂肪摄入较高，建议适当减少');
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    warnings, 
    suggestions
  };
};

export const generateSmartDefaults = async (userId: string): Promise<NutritionData> => {
  // 获取用户历史数据
  const recentData = await getUserRecentNutrition(userId, 30);
  
  if (recentData.length === 0) {
    // 新用户默认值
    return { calories: 2000, protein: 100, fat: 70, carbohydrates: 250 };
  }
  
  // 计算平均值
  const avgNutrition = recentData.reduce((acc, curr) => ({
    calories: acc.calories + curr.calories,
    protein: acc.protein + curr.protein,
    fat: acc.fat + curr.fat,
    carbohydrates: acc.carbohydrates + curr.carbohydrates
  }));
  
  const count = recentData.length;
  return {
    calories: Math.round(avgNutrition.calories / count),
    protein: Math.round(avgNutrition.protein / count),
    fat: Math.round(avgNutrition.fat / count),
    carbohydrates: Math.round(avgNutrition.carbohydrates / count)
  };
};
```

## 依赖关系

**前置依赖**: E2S1 (数据录入界面架构) - 需要卡片组件框架  
**后续任务**: E2S6 (数据持久化) - 需要饮食数据结构

## 预估时间分解

- **第1天**: 营养输入组件，模板选择功能实现
- **第2天**: 智能默认值系统，营养分析和建议功能

## 风险点和缓解策略

### 风险点
1. **营养计算复杂性**: 营养素热量转换和配比计算可能出错
2. **模板适用性**: 预设模板可能不适合所有用户
3. **数据验证遗漏**: 营养素数值的边界情况处理
4. **用户体验**: 输入过程可能繁琐

### 缓解策略
1. 使用标准营养学公式，充分测试计算逻辑
2. 提供自定义模板功能，支持用户个性化需求
3. 建立完整的验证测试用例
4. 提供快捷输入方式和智能推荐

## 验证方法

### 功能验证
1. **输入验证测试**: 各种数值输入的验证和错误处理
2. **模板应用测试**: 模板选择后数据正确填充
3. **建议系统测试**: 营养分析和建议内容准确性
4. **智能默认值测试**: 基于历史数据的推荐准确性

### 数据准确性验证
- 营养素热量计算准确率 > 95%
- 营养配比分析正确性 100%
- 健康建议符合营养学标准

## 完成标准

- [ ] 所有验收标准项目已完成
- [ ] 营养素输入组件功能完整
- [ ] 快速模板选择正常工作
- [ ] 营养建议系统准确可靠
- [ ] 智能默认值推荐合理
- [ ] 数据验证覆盖全面
- [ ] 用户体验测试通过

## 营养健康参考标准

### 成年人日常营养需求
- **卡路里**: 男性2200-2800kcal，女性1800-2200kcal
- **蛋白质**: 每公斤体重1-1.2g（活跃人群1.5-2g）
- **脂肪**: 总热量的20-35%
- **碳水化合物**: 总热量的45-65%

### 特殊目标营养建议
- **减脂期**: 蛋白质提高至1.6-2.2g/kg，适度降低碳水
- **增肌期**: 蛋白质1.8-2.5g/kg，碳水化合物充足
- **维持期**: 均衡营养配比，关注食物多样性

## 相关文档

- [营养数据模型设计](../营养数据模型设计.md)
- [营养计算公式参考](../营养计算公式参考.md)
- [健康饮食指导](../健康饮食指导.md)
- [模板系统设计](../模板系统设计.md)

---

**任务负责人**: [待分配]  
**创建时间**: 2024年  
**最后更新**: 2024年