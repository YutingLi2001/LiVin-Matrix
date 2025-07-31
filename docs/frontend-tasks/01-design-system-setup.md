# 任务01：设计系统建立

## 任务概述
建立LiVin Matrix的赛博朋克风格设计系统，包括Obsidian风格的紫色主题、霓虹发光效果和完整的CSS变量系统。

## 任务目标
创建统一的视觉设计系统，为整个应用提供一致的赛博朋克美学基础。

## 验收标准

### 1. CSS变量系统建立
- [ ] 创建完整的颜色变量系统（主紫色#8b5cf6、霓虹色彩、背景色）
- [ ] 定义字体系统（JetBrains Mono、Inter、Orbitron）
- [ ] 建立间距和尺寸规范
- [ ] 设置圆角和阴影系统

### 2. Tailwind CSS主题配置
- [ ] 配置tailwind.config.js自定义主题
- [ ] 扩展默认调色板添加赛博朋克色彩
- [ ] 配置自定义字体和字重
- [ ] 添加自定义动画和过渡效果

### 3. 赛博朋克效果系统
- [ ] 实现霓虹发光CSS类（.neon-glow, .neon-border）
- [ ] 创建脉冲动画效果（@keyframes pulse-glow）
- [ ] 建立玻璃质感效果（backdrop-filter）
- [ ] 实现矩阵代码风格效果

### 4. 基础主题切换
- [ ] 建立CSS自定义属性结构
- [ ] 实现暗色主题（默认）
- [ ] 预留主题切换接口
- [ ] 确保所有效果在不同主题下正常显示

### 5. 设计系统文档
- [ ] 创建色彩使用指南
- [ ] 编写组件样式规范
- [ ] 提供使用示例和最佳实践
- [ ] 建立设计token文档

## 技术实现要点

### CSS变量系统示例
```css
:root {
  /* 主色调 - 紫色系 (参考Obsidian) */
  --primary-50: #f3f0ff;
  --primary-500: #8b5cf6;    /* 主品牌色 - Obsidian紫 */
  --primary-900: #4c1d95;
  
  /* 赛博朋克背景系统 */
  --bg-primary: #000000;       /* 纯黑主背景 */
  --bg-secondary: #0a0a0a;     /* 微黑卡片背景 */
  
  /* 霓虹发光色彩 */
  --neon-purple: #8b5cf6;
  --neon-cyan: #22d3ee;
  --neon-pink: #ec4899;
  
  /* 文本颜色系统 */
  --text-primary: #ffffff;
  --text-secondary: #b4b4b4;
}
```

### Tailwind配置示例
```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'neon': {
          purple: '#8b5cf6',
          cyan: '#22d3ee',
          pink: '#ec4899'
        }
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        'display': ['Orbitron', 'Inter', 'sans-serif']
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite alternate',
        'neon-flicker': 'flicker 1.5s infinite alternate'
      }
    }
  }
}
```

### 霓虹发光效果
```css
.neon-glow {
  transition: box-shadow 0.3s ease, border-color 0.3s ease;
}

.neon-glow:hover {
  box-shadow: 
    0 0 20px rgba(139, 92, 246, 0.6),
    0 0 40px rgba(139, 92, 246, 0.3),
    inset 0 0 20px rgba(139, 92, 246, 0.1);
  border-color: var(--neon-purple);
}
```

## 创建的文件列表
- `src/styles/globals.css` - 全局CSS变量和基础样式
- `src/styles/cyberpunk-theme.css` - 赛博朋克主题专用样式
- `tailwind.config.js` - Tailwind自定义配置
- `src/styles/design-tokens.css` - 设计token定义
- `docs/design-system.md` - 设计系统文档

## 依赖关系
- **前置条件**: React项目初始化完成
- **后续任务**: 基础UI组件开发需要此设计系统

## 预估时间
**6-8小时**

## 优先级
**高优先级** - 所有其他UI任务的基础

## 风险点和缓解策略
- **风险**: 色彩对比度不符合无障碍标准
- **缓解**: 使用对比度检查工具验证所有颜色组合达到WCAG AA标准

- **风险**: 动画效果影响性能
- **缓解**: 优先使用CSS动画，谨慎使用transform和opacity属性

## 验证方法
1. **视觉验证**: 所有颜色和效果符合赛博朋克美学
2. **无障碍验证**: 色彩对比度达到4.5:1以上
3. **性能验证**: 动画流畅，无明显卡顿
4. **兼容性验证**: 在Chrome、Firefox、Safari中显示一致