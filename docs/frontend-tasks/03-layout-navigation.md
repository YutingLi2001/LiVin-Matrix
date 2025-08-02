# 任务03：布局和导航系统

## 任务概述
创建LiVin Matrix应用的响应式布局系统和导航架构，实现桌面端侧边栏布局、平板端全宽布局和移动端优化。

## 任务目标
建立完整的应用布局框架，提供一致的导航体验和响应式适配。

## 验收标准

### 1. 主布局组件实现
- [ ] 创建AppLayout主布局组件
- [ ] 实现Header顶部导航栏（64px高度）
- [ ] 实现Sidebar侧边栏（240px宽度，可收起）
- [ ] 实现Main内容区域和Footer页脚
- [ ] 支持布局状态管理（侧边栏展开/收起）

### 2. 响应式断点适配
- [ ] 桌面端（≥1024px）：完整侧边栏布局
- [ ] 平板端（768px-1023px）：全宽布局 + 移动菜单
- [ ] 移动端（<768px）：堆叠布局 + 底部导航
- [ ] 实现断点切换时的平滑过渡动画
- [ ] 确保在所有断点下的可用性

### 3. 导航菜单系统
- [ ] 实现主菜单项（Dashboard、Matrix、Data Entry、Trends、Profile）
- [ ] 添加菜单项激活状态和霓虹高亮效果
- [ ] 支持嵌套子菜单（如果需要）
- [ ] 实现面包屑导航组件
- [ ] 添加菜单项图标和Badge通知

### 4. 赛博朋克导航样式
- [ ] 侧边栏背景使用玻璃质感效果
- [ ] 菜单项悬停和激活时的霓虹发光效果
- [ ] Header使用渐变背景和模糊效果
- [ ] 导航分隔线使用霓虹色彩
- [ ] 移动端菜单的滑出动画效果

### 5. 导航状态管理
- [ ] 实现路由状态同步
- [ ] 保存用户的布局偏好（侧边栏状态）
- [ ] 支持键盘导航（Tab、Arrow keys）
- [ ] 实现搜索快捷跳转功能
- [ ] 添加返回顶部功能

## 技术实现要点

### AppLayout组件结构
```typescript
interface LayoutProps {
  children: ReactNode;
}

const AppLayout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);

  return (
    <div className="min-h-screen bg-primary text-primary">
      <Header 
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        isMobile={isMobile}
      />
      
      <div className="flex">
        <Sidebar 
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          isMobile={isMobile}
        />
        
        <Main className={cn(
          'flex-1 transition-all duration-300',
          sidebarOpen && !isMobile ? 'ml-240' : 'ml-0'
        )}>
          {children}
        </Main>
      </div>
    </div>
  );
};
```

### Sidebar组件实现
```typescript
interface SidebarProps {
  open: boolean;
  onClose: () => void;
  isMobile: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose, isMobile }) => {
  const location = useLocation();
  
  const menuItems = [
    { path: '/', label: 'Dashboard', icon: HomeIcon },
    { path: '/matrix', label: 'Matrix Analysis', icon: GridIcon },
    { path: '/entry', label: 'Data Entry', icon: PlusIcon },
    { path: '/trends', label: 'Trends', icon: TrendingUpIcon },
    { path: '/profile', label: 'Profile', icon: UserIcon }
  ];

  return (
    <>
      {/* Mobile Overlay */}
      {isMobile && open && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside className={cn(
        'fixed top-16 left-0 z-50 h-[calc(100vh-4rem)]',
        'w-60 bg-secondary/80 backdrop-blur-lg',
        'border-r border-primary-500/30',
        'transform transition-transform duration-300 ease-in-out',
        open ? 'translate-x-0' : '-translate-x-full',
        !isMobile && 'sticky translate-x-0'
      )}>
        <nav className="p-4 space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center space-x-3 px-4 py-3 rounded-lg',
                'text-secondary hover:text-primary transition-colors',
                'hover:bg-primary-500/10 neon-glow',
                location.pathname === item.path && 
                'bg-primary-500/20 text-neon-purple border border-neon-purple/50'
              )}
              onClick={isMobile ? onClose : undefined}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          ))}
        </nav>
      </aside>
    </>
  );
};
```

### Header组件实现
```typescript
interface HeaderProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  isMobile: boolean;
}

const Header: React.FC<HeaderProps> = ({ 
  sidebarOpen, 
  setSidebarOpen, 
  isMobile 
}) => {
  return (
    <header className="sticky top-0 z-30 h-16 bg-secondary/80 backdrop-blur-lg border-b border-primary-500/30">
      <div className="flex items-center justify-between h-full px-4">
        {/* Logo and Menu Toggle */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-primary-500/10 neon-glow"
          >
            <MenuIcon className="w-5 h-5 text-primary" />
          </button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-neon-purple to-neon-cyan rounded-lg flex items-center justify-center">
              <span className="text-primary font-bold font-display">LM</span>
            </div>
            <h1 className="text-xl font-bold text-primary font-display">
              LiVin Matrix
            </h1>
          </div>
        </div>

        {/* Search and User Menu */}
        <div className="flex items-center space-x-4">
          <SearchBox />
          <NotificationBell />
          <UserMenu />
        </div>
      </div>
    </header>
  );
};
```

### 响应式设计
```css
/* Tailwind配置中的断点 */
@media (min-width: 1024px) {
  .desktop-layout {
    /* 桌面端完整布局 */
  }
}

@media (min-width: 768px) and (max-width: 1023px) {
  .tablet-layout {
    /* 平板端简化布局 */
  }
}

@media (max-width: 767px) {
  .mobile-layout {
    /* 移动端堆叠布局 */
  }
}
```

## 创建的文件列表
- `src/components/layout/AppLayout.tsx` - 主布局组件
- `src/components/layout/Header.tsx` - 顶部导航栏
- `src/components/layout/Sidebar.tsx` - 侧边栏导航
- `src/components/layout/Main.tsx` - 主内容区域
- `src/components/navigation/NavigationMenu.tsx` - 导航菜单
- `src/components/navigation/Breadcrumb.tsx` - 面包屑导航
- `src/hooks/useResponsive.ts` - 响应式状态Hook
- `src/styles/layout.css` - 布局专用样式

## 依赖关系
- **前置条件**: 01-design-system-setup、02-base-ui-components完成
- **后续任务**: 所有页面组件都需要在此布局中使用

## 预估时间
**16-20小时**

## 优先级
**高优先级** - 应用基础架构

## 风险点和缓解策略
- **风险**: 响应式断点切换时布局闪烁
- **缓解**: 使用CSS过渡和transform优化动画性能

- **风险**: 移动端导航体验不佳
- **缓解**: 参考现代Web应用的移动端导航模式

## 验证方法
1. **响应式验证**: 在不同设备尺寸下测试布局适配
2. **导航验证**: 确保所有导航链接正常工作
3. **无障碍验证**: 支持键盘导航和屏幕阅读器
4. **性能验证**: 布局切换动画流畅，无卡顿