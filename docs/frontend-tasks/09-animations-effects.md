# 任务09：赛博朋克动画效果

## 任务概述
实现LiVin Matrix的赛博朋克风格动画效果系统，包括霓虹发光、页面过渡、矩阵脉冲等视觉增强。

## 验收标准

### 1. 霓虹发光动画系统
- [ ] 悬停霓虹发光效果
- [ ] 脉冲呼吸动画
- [ ] 边框流光效果
- [ ] 文字闪烁动画
- [ ] 按钮点击涟漪效果

### 2. 页面过渡动画
- [ ] 路由切换过渡效果
- [ ] 组件进入/退出动画
- [ ] 模态框弹出动画
- [ ] 卡片展开/收起动画
- [ ] 数据加载动画

### 3. 矩阵相关动画
- [ ] 矩阵单元格脉冲效果
- [ ] 数据更新波纹动画
- [ ] 相关性变化过渡
- [ ] 矩阵加载骨架动画
- [ ] 数据钻取展开效果

## 技术实现要点

### CSS动画定义
```css
@keyframes neon-glow {
  0%, 100% {
    box-shadow: 0 0 5px var(--neon-purple);
  }
  50% {
    box-shadow: 0 0 20px var(--neon-purple), 0 0 30px var(--neon-purple);
  }
}

@keyframes pulse-glow {
  0% {
    box-shadow: 0 0 5px rgba(139, 92, 246, 0.5);
  }
  100% {
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.8);
  }
}

@keyframes matrix-rain {
  0% { transform: translateY(-100vh); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(100vh); opacity: 0; }
}
```

### Framer Motion配置
```typescript
const pageVariants = {
  initial: { opacity: 0, x: -20 },
  in: { opacity: 1, x: 0 },
  out: { opacity: 0, x: 20 }
};

const pageTransition = {
  type: 'tween',
  ease: 'anticipate',
  duration: 0.4
};

const AnimatedPage: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <motion.div
      initial="initial"
      animate="in"
      exit="out"
      variants={pageVariants}
      transition={pageTransition}
    >
      {children}
    </motion.div>
  );
};
```

## 创建的文件列表
- `src/styles/animations.css` - CSS动画定义
- `src/components/animations/AnimatedPage.tsx` - 页面动画包装
- `src/components/animations/NeonButton.tsx` - 霓虹按钮动画
- `src/components/animations/PulseCard.tsx` - 脉冲卡片动画
- `src/hooks/useAnimations.ts` - 动画控制Hook

## 预估时间
**14-18小时**

## 优先级
**中优先级** - 视觉增强功能
