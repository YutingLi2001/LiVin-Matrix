# 任务08：状态管理架构

## 任务概述
建立LiVin Matrix应用的全局状态管理系统，使用React Context + useReducer模式，管理用户数据、UI状态和分析结果。

## 验收标准

### 1. 全局状态架构设计
- [ ] 创建AppContext全局状态容器
- [ ] 实现useReducer状态管理逻辑
- [ ] 定义完整的State和Action类型
- [ ] 实现状态持久化机制
- [ ] 添加状态调试工具

### 2. 数据状态管理
- [ ] 用户数据状态管理
- [ ] 矩阵分析结果缓存
- [ ] 表单数据临时存储
- [ ] API请求状态管理
- [ ] 错误状态统一处理

### 3. UI状态管理
- [ ] 主题和布局状态
- [ ] 模态框和弹窗状态
- [ ] 导航和路由状态
- [ ] 加载和错误状态
- [ ] 用户偏好设置

## 技术实现要点

### 全局状态结构
```typescript
interface AppState {
  user: UserState;
  data: DataState;
  ui: UIState;
  analysis: AnalysisState;
}

interface UserState {
  profile: UserProfile | null;
  preferences: UserPreferences;
  isAuthenticated: boolean;
}

interface DataState {
  records: UserRecord[];
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
  cache: Record<string, any>;
}

interface UIState {
  theme: 'dark' | 'light';
  sidebarOpen: boolean;
  currentModal: string | null;
  notifications: Notification[];
}

interface AnalysisState {
  correlationMatrix: CorrelationMatrix | null;
  selectedTimeRange: TimeRange;
  selectedDimensions: string[];
  insights: Insight[];
  loading: boolean;
}
```

### Action定义
```typescript
type AppAction = 
  | { type: 'SET_USER_PROFILE'; payload: UserProfile }
  | { type: 'UPDATE_USER_DATA'; payload: UserRecord[] }
  | { type: 'SET_CORRELATION_MATRIX'; payload: CorrelationMatrix }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_THEME'; payload: 'dark' | 'light' }
  | { type: 'SET_LOADING'; payload: { key: string; loading: boolean } }
  | { type: 'SET_ERROR'; payload: { key: string; error: string | null } };
```

### AppContext Provider
```typescript
const AppContext = createContext<{
  state: AppState;
  dispatch: Dispatch<AppAction>;
} | null>(null);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // 状态持久化
  useEffect(() => {
    const persistedState = localStorage.getItem('livin-matrix-state');
    if (persistedState) {
      const parsed = JSON.parse(persistedState);
      dispatch({ type: 'HYDRATE_STATE', payload: parsed });
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('livin-matrix-state', JSON.stringify({
      user: state.user,
      ui: { theme: state.ui.theme, sidebarOpen: state.ui.sidebarOpen }
    }));
  }, [state.user, state.ui.theme, state.ui.sidebarOpen]);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};
```

## 创建的文件列表
- `src/context/AppContext.tsx` - 全局状态上下文
- `src/context/appReducer.ts` - 状态管理reducer
- `src/types/state.ts` - 状态类型定义
- `src/hooks/useAppContext.ts` - 状态访问Hook
- `src/hooks/useUserData.ts` - 用户数据管理Hook
- `src/hooks/useUIState.ts` - UI状态管理Hook
- `src/utils/stateUtils.ts` - 状态工具函数

## 预估时间
**16-20小时**

## 优先级
**高优先级** - 应用基础架构