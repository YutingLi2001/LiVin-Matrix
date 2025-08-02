# 6. 详细前端架构设计 (Detailed Frontend Architecture)

## 6.1 React组件架构设计

**组件层次结构：**
```typescript
// 应用组件树结构
src/
├── components/           # 可复用组件库
│   ├── ui/              # 基础UI组件
│   │   ├── Button/      # 按钮组件
│   │   ├── Input/       # 输入框组件
│   │   ├── Modal/       # 模态框组件
│   │   ├── Card/        # 卡片组件
│   │   └── Chart/       # 图表组件封装
│   ├── forms/           # 表单相关组件
│   │   ├── DimensionForm/    # 维度数据录入表单
│   │   ├── ValidationInput/  # 带验证的输入组件
│   │   └── DatePicker/       # 日期选择器
│   ├── matrix/          # 矩阵相关组件
│   │   ├── MatrixGrid/       # 6维度矩阵网格
│   │   ├── CorrelationView/  # 相关性可视化
│   │   └── TrendChart/       # 趋势图表
│   └── layout/          # 布局组件
│       ├── Header/           # 页面头部
│       ├── Sidebar/          # 侧边栏导航
│       └── Footer/           # 页面底部
├── pages/               # 页面级组件
│   ├── Dashboard/       # 仪表板主页
│   ├── DataEntry/       # 数据录入页面
│   ├── Analytics/       # 数据分析页面
│   ├── Matrix/          # 矩阵视图页面
│   └── Settings/        # 设置页面
├── hooks/               # 自定义React Hooks
│   ├── useAuth.ts       # 认证状态管理
│   ├── useAPI.ts        # API调用封装
│   ├── useMatrix.ts     # 矩阵数据管理
│   └── useLocalStorage.ts  # 本地存储管理
├── contexts/            # React Context状态管理
│   ├── AuthContext.tsx  # 用户认证上下文
│   ├── ThemeContext.tsx # 主题切换上下文
│   └── DataContext.tsx  # 数据状态上下文
└── utils/               # 工具函数
    ├── api.ts           # API调用工具
    ├── validation.ts    # 数据验证工具
    └── date.ts          # 日期处理工具
```

**组件设计原则：**
```typescript
// 1. 组件职责单一原则
interface ComponentProps {
  data: SpecificDataType;
  onAction: (action: ActionType) => void;
  className?: string; // 支持样式定制
}

// 2. 组件合成模式
const DimensionCard: React.FC<DimensionCardProps> = ({ 
  dimension, 
  data, 
  onUpdate 
}) => {
  return (
    <Card className="dimension-card">
      <Card.Header>
        <DimensionIcon type={dimension.type} />
        <DimensionTitle>{dimension.displayName}</DimensionTitle>
      </Card.Header>
      <Card.Body>
        <DimensionChart data={data} />
        <DimensionMetrics data={data} />
      </Card.Body>
      <Card.Footer>
        <UpdateButton onClick={onUpdate} />
        <OptionsMenu dimension={dimension} />
      </Card.Footer>
    </Card>
  );
};

// 3. Hooks封装逻辑复用
const useDimensionData = (dimensionId: string, dateRange: DateRange) => {
  const [data, setData] = useState<DimensionData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.getDimensionData(dimensionId, dateRange);
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [dimensionId, dateRange]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};
```

## 6.2 状态管理架构

**Context + useReducer模式：**
```typescript
// 全局数据状态管理
interface AppState {
  user: UserProfile | null;
  dimensions: DimensionConfig[];
  currentData: Record<string, DimensionData[]>;
  matrix: MatrixData | null;
  ui: UIState;
}

// 状态更新Actions
type AppAction = 
  | { type: 'SET_USER'; payload: UserProfile }
  | { type: 'UPDATE_DIMENSION_DATA'; payload: { dimensionId: string; data: DimensionData[] } }
  | { type: 'SET_MATRIX_DATA'; payload: MatrixData }
  | { type: 'SET_LOADING'; payload: { key: string; loading: boolean } }
  | { type: 'SET_ERROR'; payload: { key: string; error: string | null } };

// 状态Reducer
const appReducer = (state: AppState, action: AppAction): AppState => {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    
    case 'UPDATE_DIMENSION_DATA':
      return {
        ...state,
        currentData: {
          ...state.currentData,
          [action.payload.dimensionId]: action.payload.data
        }
      };
    
    case 'SET_MATRIX_DATA':
      return { ...state, matrix: action.payload };
    
    case 'SET_LOADING':
      return {
        ...state,
        ui: {
          ...state.ui,
          loading: { ...state.ui.loading, [action.payload.key]: action.payload.loading }
        }
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        ui: {
          ...state.ui,
          errors: { ...state.ui.errors, [action.payload.key]: action.payload.error }
        }
      };
    
    default:
      return state;
  }
};

// Context Provider封装
const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);
  
  const actions = useMemo(() => ({
    setUser: (user: UserProfile) => dispatch({ type: 'SET_USER', payload: user }),
    updateDimensionData: (dimensionId: string, data: DimensionData[]) => 
      dispatch({ type: 'UPDATE_DIMENSION_DATA', payload: { dimensionId, data } }),
    setMatrixData: (matrix: MatrixData) => 
      dispatch({ type: 'SET_MATRIX_DATA', payload: matrix }),
    setLoading: (key: string, loading: boolean) => 
      dispatch({ type: 'SET_LOADING', payload: { key, loading } }),
    setError: (key: string, error: string | null) => 
      dispatch({ type: 'SET_ERROR', payload: { key, error } })
  }), []);

  return (
    <AppContext.Provider value={{ state, actions }}>
      {children}
    </AppContext.Provider>
  );
};
```

**本地状态管理策略：**
```typescript
// 本地存储Hook
const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.warn(`Error setting localStorage key "${key}":`, error);
    }
  }, [key, storedValue]);

  return [storedValue, setValue] as const;
};

// 缓存管理Hook
const useDataCache = () => {
  const [cache, setCache] = useLocalStorage<Record<string, CacheEntry>>('dataCache', {});
  
  const getCachedData = useCallback((key: string) => {
    const entry = cache[key];
    if (!entry) return null;
    
    const isExpired = Date.now() > entry.expiresAt;
    if (isExpired) {
      const newCache = { ...cache };
      delete newCache[key];
      setCache(newCache);
      return null;
    }
    
    return entry.data;
  }, [cache, setCache]);

  const setCachedData = useCallback((key: string, data: any, ttl: number = 300000) => {
    const entry: CacheEntry = {
      data,
      expiresAt: Date.now() + ttl,
      createdAt: Date.now()
    };
    setCache(prev => ({ ...prev, [key]: entry }));
  }, [setCache]);

  return { getCachedData, setCachedData };
};
```

## 6.3 Cyberpunk UI设计实现

**主题系统设计：**
```typescript
// Cyberpunk主题配置
const cyberpunkTheme = {
  colors: {
    primary: {
      neon: '#00ff9f',      // 霓虹绿
      cyan: '#00d4ff',      // 电光蓝
      purple: '#b347d9',    // 紫色
      pink: '#ff1744'       // 粉色
    },
    background: {
      dark: '#0a0a0a',      // 深黑背景
      surface: '#1a1a2e',   // 表面色
      elevated: '#16213e'    // 高层级背景
    },
    text: {
      primary: '#ffffff',    // 主要文字
      secondary: '#b0b0b0',  // 次要文字
      accent: '#00ff9f',     // 强调文字
      muted: '#666666'       // 弱化文字
    },
    border: {
      default: '#333333',    // 默认边框
      neon: '#00ff9f',       // 霓虹边框
      glow: 'rgba(0, 255, 159, 0.3)' // 发光效果
    }
  },
  effects: {
    neonGlow: {
      boxShadow: '0 0 10px #00ff9f, 0 0 20px #00ff9f, 0 0 30px #00ff9f',
      textShadow: '0 0 10px #00ff9f'
    },
    dataStream: {
      background: 'linear-gradient(90deg, transparent 0%, #00ff9f 50%, transparent 100%)',
      animation: 'dataFlow 2s linear infinite'
    },
    glitch: {
      animation: 'glitch 0.3s ease-in-out infinite alternate'
    }
  },
  typography: {
    fonts: {
      mono: "'JetBrains Mono', 'Consolas', monospace",
      sans: "'Inter', 'Helvetica', sans-serif"
    },
    sizes: {
      xs: '0.75rem',
      sm: '0.875rem', 
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem'
    }
  }
};

// CSS-in-JS样式组件
const CyberpunkCard = styled.div<{ glowColor?: string }>`
  background: ${props => props.theme.colors.background.surface};
  border: 1px solid ${props => props.theme.colors.border.default};
  border-radius: 8px;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: ${props => props.theme.effects.dataStream.background};
    animation: ${props => props.theme.effects.dataStream.animation};
  }
  
  &:hover {
    border-color: ${props => props.glowColor || props.theme.colors.primary.neon};
    box-shadow: ${props => `0 0 20px ${props.glowColor || props.theme.colors.primary.neon}33`};
    transform: translateY(-2px);
    transition: all 0.3s ease;
  }
`;

// 动画关键帧
const animations = css`
  @keyframes dataFlow {
    0% { left: -100%; }
    100% { left: 100%; }
  }
  
  @keyframes glitch {
    0% { transform: translate(0); }
    20% { transform: translate(-2px, 2px); }
    40% { transform: translate(-2px, -2px); }
    60% { transform: translate(2px, 2px); }
    80% { transform: translate(2px, -2px); }
    100% { transform: translate(0); }
  }
  
  @keyframes neonPulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }
`;
```

**矩阵可视化组件：**
```typescript
// 6维度矩阵网格组件
const MatrixGrid: React.FC<MatrixGridProps> = ({ 
  dimensions, 
  correlationData, 
  onCellClick 
}) => {
  return (
    <div className="matrix-grid">
      <div className="matrix-header">
        <h2 className="matrix-title">Life Matrix - 生活矩阵</h2>
        <div className="matrix-subtitle">Cross-dimensional correlation analysis</div>
      </div>
      
      <div className="grid-container">
        {/* 维度标签行 */}
        <div className="dimension-labels-row">
          {dimensions.map(dim => (
            <div key={dim.id} className="dimension-label">
              <DimensionIcon type={dim.type} />
              <span>{dim.displayName}</span>
            </div>
          ))}
        </div>
        
        {/* 矩阵单元格 */}
        <div className="matrix-cells">
          {dimensions.map((rowDim, rowIndex) => (
            <div key={rowDim.id} className="matrix-row">
              <div className="row-label">
                <DimensionIcon type={rowDim.type} />
                <span>{rowDim.displayName}</span>
              </div>
              
              {dimensions.map((colDim, colIndex) => {
                const correlation = getCorrelation(rowDim.id, colDim.id, correlationData);
                const isActive = rowIndex !== colIndex;
                
                return (
                  <MatrixCell
                    key={`${rowDim.id}-${colDim.id}`}
                    correlation={correlation}
                    isActive={isActive}
                    onClick={() => isActive && onCellClick(rowDim, colDim)}
                    className={`matrix-cell ${isActive ? 'interactive' : 'diagonal'}`}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// 相关性单元格组件
const MatrixCell: React.FC<MatrixCellProps> = ({ 
  correlation, 
  isActive, 
  onClick 
}) => {
  const getCorrelationColor = (value: number | null) => {
    if (value === null) return '#333333';
    const intensity = Math.abs(value);
    if (value > 0) {
      return `rgba(0, 255, 159, ${intensity})`;  // 正相关用绿色
    } else {
      return `rgba(255, 23, 68, ${intensity})`;   // 负相关用红色
    }
  };

  const getCellContent = () => {
    if (!isActive) return '•';  // 对角线标记
    if (correlation === null) return '?';  // 数据不足
    return correlation.toFixed(2);  // 相关系数
  };

  return (
    <div
      className={`matrix-cell ${isActive ? 'active' : 'inactive'}`}
      style={{
        backgroundColor: getCorrelationColor(correlation),
        border: `1px solid ${getCorrelationColor(correlation) || '#333333'}`
      }}
      onClick={onClick}
    >
      <span className="correlation-value">{getCellContent()}</span>
      {isActive && correlation !== null && (
        <div className="correlation-strength">
          {Math.abs(correlation) > 0.7 ? 'Strong' : 
           Math.abs(correlation) > 0.4 ? 'Moderate' : 'Weak'}
        </div>
      )}
    </div>
  );
};
```

## 6.4 前后端数据流集成

**API调用封装：**
```typescript
// API基础类
class APIClient {
  private baseURL: string;
  private authToken: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.authToken && { 'Authorization': `Bearer ${this.authToken}` }),
      ...options.headers
    };

    try {
      const response = await fetch(url, { ...options, headers });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(response.status, errorData.detail || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) throw error;
      throw new APIError(0, 'Network error occurred');
    }
  }

  // 维度数据API
  async getDimensionData(
    dimensionId: string, 
    startDate: string, 
    endDate: string
  ): Promise<DimensionRecord[]> {
    return this.request<DimensionRecord[]>(
      `/api/v1/dimensions/${dimensionId}/data?start_date=${startDate}&end_date=${endDate}`
    );
  }

  async createDimensionRecord(
    dimensionId: string, 
    data: CreateDimensionRecordRequest
  ): Promise<DimensionRecord> {
    return this.request<DimensionRecord>(
      `/api/v1/dimensions/${dimensionId}/data`, {
        method: 'POST',
        body: JSON.stringify(data)
      }
    );
  }

  // 矩阵分析API
  async getMatrixOverview(timePeriod: string = 'month'): Promise<MatrixData> {
    return this.request<MatrixData>(
      `/api/v1/matrix/overview?time_period=${timePeriod}`
    );
  }

  async getCorrelationAnalysis(
    dimensionA: string, 
    dimensionB: string, 
    timePeriod: string = 'month'
  ): Promise<CorrelationResult> {
    return this.request<CorrelationResult>(
      `/api/v1/matrix/correlations?dim_a=${dimensionA}&dim_b=${dimensionB}&time_period=${timePeriod}`
    );
  }
}

// React Hook封装API调用
const useAPI = () => {
  const { state } = useContext(AppContext);
  const api = useMemo(() => {
    const client = new APIClient(process.env.REACT_APP_API_BASE_URL!);
    if (state.user?.token) {
      client.setAuthToken(state.user.token);
    }
    return client;
  }, [state.user?.token]);

  return api;
};
```

**实时数据同步：**
```typescript
// WebSocket连接管理
class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private eventHandlers: Map<string, Function[]> = new Map();

  connect(url: string, token: string) {
    try {
      this.ws = new WebSocket(`${url}?token=${token}`);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.emit('connected');
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit(data.type, data.payload);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.emit('disconnected');
        this.attemptReconnect(url, token);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
    }
  }

  private attemptReconnect(url: string, token: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect(url, token);
      }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
    }
  }

  on(event: string, handler: Function) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  }

  private emit(event: string, data?: any) {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }
}

// React Hook封装WebSocket
const useWebSocket = () => {
  const { state, actions } = useContext(AppContext);
  const wsManager = useRef<WebSocketManager>(new WebSocketManager());

  useEffect(() => {
    if (state.user?.token) {
      const wsUrl = process.env.REACT_APP_WS_URL!;
      wsManager.current.connect(wsUrl, state.user.token);

      // 监听数据更新
      wsManager.current.on('dimension_data_updated', (data: DimensionUpdatePayload) => {
        actions.updateDimensionData(data.dimensionId, data.records);
      });

      // 监听矩阵数据更新
      wsManager.current.on('matrix_updated', (data: MatrixData) => {
        actions.setMatrixData(data);
      });

      return () => {
        wsManager.current.disconnect();
      };
    }
  }, [state.user?.token, actions]);

  return wsManager.current;
};
```

## 6.5 性能优化策略

**组件渲染优化：**
```typescript
// React.memo优化重渲染
const DimensionCard = React.memo<DimensionCardProps>(({ 
  dimension, 
  data, 
  onUpdate 
}) => {
  return (
    <Card>
      <DimensionChart data={data} />
      <DimensionMetrics data={data} />
    </Card>
  );
}, (prevProps, nextProps) => {
  // 自定义比较函数
  return (
    prevProps.dimension.id === nextProps.dimension.id &&
    JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data)
  );
});

// useMemo优化计算
const MatrixAnalysis: React.FC<MatrixAnalysisProps> = ({ correlationData }) => {
  const processedData = useMemo(() => {
    return correlationData.map(correlation => ({
      ...correlation,
      strength: Math.abs(correlation.value),
      direction: correlation.value > 0 ? 'positive' : 'negative',
      significance: correlation.confidence > 0.7 ? 'high' : 'low'
    }));
  }, [correlationData]);

  const strongCorrelations = useMemo(() => {
    return processedData.filter(item => item.strength > 0.6);
  }, [processedData]);

  return (
    <div>
      <CorrelationMatrix data={processedData} />
      <StrongCorrelationsList data={strongCorrelations} />
    </div>
  );
};

// useCallback优化事件处理
const DataEntryForm: React.FC<DataEntryFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<FormData>({});

  const handleFieldChange = useCallback((field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  }, [formData, onSubmit]);

  return (
    <form onSubmit={handleSubmit}>
      {/* 表单字段 */}
    </form>
  );
};
```

**代码分割和懒加载：**
```typescript
// 路由级别代码分割
const Dashboard = React.lazy(() => import('../pages/Dashboard'));
const Analytics = React.lazy(() => import('../pages/Analytics'));
const MatrixView = React.lazy(() => import('../pages/MatrixView'));
const Settings = React.lazy(() => import('../pages/Settings'));

// 应用路由配置
const AppRouter: React.FC = () => {
  return (
    <Router>
      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/matrix" element={<MatrixView />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </Router>
  );
};

// 动态导入优化
const ChartComponent = React.lazy(() => 
  import('recharts').then(module => ({
    default: module.LineChart
  }))
);

// 条件加载复杂组件
const AdvancedAnalytics: React.FC<AdvancedAnalyticsProps> = ({ showAdvanced }) => {
  const [AdvancedCharts, setAdvancedCharts] = useState<React.ComponentType | null>(null);

  useEffect(() => {
    if (showAdvanced && !AdvancedCharts) {
      import('../components/AdvancedCharts').then(module => {
        setAdvancedCharts(() => module.default);
      });
    }
  }, [showAdvanced, AdvancedCharts]);

  return (
    <div>
      <BasicCharts />
      {showAdvanced && AdvancedCharts && <AdvancedCharts />}
    </div>
  );
};
```

**数据预取和缓存策略：**
```typescript
// 数据预取Hook
const useDataPreloader = () => {
  const api = useAPI();
  const { getCachedData, setCachedData } = useDataCache();

  const preloadDimensionData = useCallback(async (dimensionIds: string[]) => {
    const today = new Date();
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    const preloadPromises = dimensionIds.map(async (dimensionId) => {
      const cacheKey = `dimension-${dimensionId}-week`;
      const cached = getCachedData(cacheKey);
      
      if (!cached) {
        try {
          const data = await api.getDimensionData(
            dimensionId, 
            lastWeek.toISOString().split('T')[0],
            today.toISOString().split('T')[0]
          );
          setCachedData(cacheKey, data, 300000); // 5分钟缓存
        } catch (error) {
          console.warn(`Failed to preload data for dimension ${dimensionId}:`, error);
        }
      }
    });

    await Promise.allSettled(preloadPromises);
  }, [api, getCachedData, setCachedData]);

  return { preloadDimensionData };
};

// 虚拟滚动优化长列表
const VirtualizedDataList: React.FC<DataListProps> = ({ items }) => {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 10 });
  const containerRef = useRef<HTMLDivElement>(null);
  const itemHeight = 60;

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const scrollTop = e.currentTarget.scrollTop;
    const containerHeight = e.currentTarget.clientHeight;
    
    const start = Math.floor(scrollTop / itemHeight);
    const end = Math.min(start + Math.ceil(containerHeight / itemHeight) + 1, items.length);
    
    setVisibleRange({ start, end });
  }, [items.length]);

  const visibleItems = items.slice(visibleRange.start, visibleRange.end);

  return (
    <div 
      ref={containerRef}
      className="virtual-list-container" 
      style={{ height: '400px', overflow: 'auto' }}
      onScroll={handleScroll}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        {visibleItems.map((item, index) => (
          <div
            key={item.id}
            style={{
              position: 'absolute',
              top: (visibleRange.start + index) * itemHeight,
              height: itemHeight,
              width: '100%'
            }}
          >
            <DataItem data={item} />
          </div>
        ))}
      </div>
    </div>
  );
};
```

---
