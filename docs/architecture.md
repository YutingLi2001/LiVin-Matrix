# LiVin Matrix - 全栈架构设计文档

## 1. 系统概览 (System Overview)

### 1.1 项目愿景与定位

**LiVin Matrix** 是一个教育导向的全栈自我追踪web应用，旨在通过"矩阵化"方式组织个人生活的6个核心维度（睡眠、饮食、运动、情绪、工作效率、社交），同时为开发者提供使用现代工具链构建完整产品的实践经验。

**核心价值主张：**
- **数据统一性：** 将分散的个人数据整合到统一的矩阵视图中
- **相关性洞察：** 通过跨维度分析发现生活模式和相关性
- **技术学习价值：** 端到端掌握现代全栈开发技术栈
- **成本控制：** 在零成本约束下构建生产级应用

### 1.2 系统边界与约束

**技术约束：**
- **预算限制：** 月运营成本严格控制在 $0（基于AWS免费tier）
- **时间约束：** 14周完成MVP版本
- **并发限制：** 设计支持最多10个同时在线用户
- **存储限制：** PostgreSQL免费层20GB存储限制

**功能边界：**
- **核心用户：** 主要服务项目创建者个人，次要服务学习导向的开发者
- **数据范围：** 专注6个固定维度，暂不支持用户自定义维度
- **平台支持：** Web应用优先，响应式设计支持桌面和平板

### 1.3 系统质量属性

**性能要求：**
- 页面加载时间：首次 < 3秒，后续导航 < 1秒
- 数据查询响应：单维度 < 500ms，矩阵分析 < 2秒
- 复杂相关性分析：< 5秒

**可靠性要求：**
- 数据完整性：零数据丢失，所有操作有事务保护
- 系统可用性：99%+ (在AWS免费tier限制内)
- 备份恢复：24小时内可完整恢复

**安全性要求：**
- 数据传输：HTTPS加密
- 用户认证：基于Auth0的JWT token验证
- 数据隔离：多用户数据完全隔离
- 隐私保护：支持数据导出和账户删除

## 2. 架构原则 (Architecture Principles)

### 2.1 设计原则

**简单性优先 (Simplicity First)**
- 选择单体架构而非微服务，降低复杂度
- 使用成熟稳定的技术栈，避免实验性技术
- 优先功能实现，后期优化性能

**成本意识驱动 (Cost-Conscious Design)**
- 所有技术选择必须支持零成本运营
- 充分利用免费tier资源限制
- 避免vendor lock-in，保持技术栈可迁移性

**学习价值最大化 (Learning Value Maximization)**
- 技术栈覆盖现代全栈开发核心技能
- 包含容器化和云服务部署实践
- 提供完整的CI/CD流水线体验

**数据主权 (Data Sovereignty)**
- 用户完全控制自己的数据
- 支持完整数据导出
- 透明的数据处理和存储策略

### 2.2 技术选择原则

**现代化技术栈**
- 前端：React 18+ + TypeScript（现代前端标准）
- 后端：FastAPI（现代Python web框架）
- 数据库：PostgreSQL（成熟稳定的关系型数据库）

**AI辅助友好**
- 选择流行技术栈获得更好的AI工具支持
- 使用标准化的项目结构和编码规范
- 优先考虑文档丰富的开源解决方案

**容器化优先**
- Docker容器化确保开发环境一致性
- K3s轻量级编排学习容器技术
- GitHub Actions实现完整CI/CD流程

### 2.3 数据架构原则

**矩阵化数据组织**
- 6个固定维度作为矩阵的行和列
- 支持时间维度的数据切片分析
- 相关性计算作为核心数据洞察

**灵活的数据模型**
- 基础固定字段 + JSON扩展字段
- 支持未来用户自定义维度扩展
- 版本化的数据迁移策略

**数据分离策略**
- 用户数据完全隔离
- 配置数据与业务数据分离
- 静态资源与动态数据分离

## 3. 技术栈决策 (Technology Stack Decisions)

### 3.1 前端技术栈

**核心框架选择：**
```typescript
{
  "framework": "React 18+",           // 现代前端标准，生态成熟
  "language": "TypeScript",           // 类型安全，提升开发效率
  "styling": "Tailwind CSS",          // 快速开发，高度可定制
  "charts": "Recharts",               // React原生图表库，简化配置
  "forms": "React Hook Form",         // 成熟稳定的表单管理
  "state": "React Context + useReducer", // 避免Redux复杂性
  "routing": "React Router",          // 标准路由解决方案
  "icons": "Lucide React",            // 简洁稳定的图标库
  "animation": "Framer Motion (渐进式)" // 高质量动画库，渐进引入
}
```

**选择理由：**
- **React生态成熟**：丰富的组件库和工具支持
- **TypeScript类型安全**：减少运行时错误，提升开发体验
- **Tailwind快速开发**：避免编写大量自定义CSS
- **渐进式动画策略**：Framer Motion按需引入，避免影响核心功能

### 3.2 后端技术栈

**API框架选择：**
```python
{
  "framework": "FastAPI",             # 现代Python web框架，自动API文档
  "orm": "SQLAlchemy",                # 成熟的ORM，支持数据迁移
  "validation": "Pydantic",           # 类型安全，自动验证
  "auth": "Auth0",                    # 避免自建认证系统复杂性
  "database": "PostgreSQL 13+",      # 关系型数据，支持JSON字段
  "migration": "Alembic"              # 版本控制数据库schema变更
}
```

**选择理由：**
- **FastAPI性能优秀**：异步支持，自动API文档生成
- **SQLAlchemy成熟稳定**：丰富的ORM功能，支持复杂查询
- **Auth0专业认证**：避免自建认证的安全风险
- **PostgreSQL功能强大**：支持JSON字段，满足灵活数据模型需求

### 3.3 基础设施技术栈

**零成本部署方案：**
```yaml
frontend_hosting: "GitHub Pages"     # 免费静态网站托管
backend_deployment: "AWS API Gateway + EKS"  # 免费tier
database: "AWS RDS PostgreSQL"       # 免费tier 20GB
file_storage: "AWS S3"               # 免费tier 5GB
containerization: "Docker + Docker Compose"  # 开发环境一致性
orchestration: "K3s"                 # 轻量Kubernetes，学习容器编排
ci_cd: "GitHub Actions"              # 代码到生产的自动化流水线
```

**架构优势：**
- **完全免费运营**：充分利用各平台免费tier
- **学习价值丰富**：涵盖容器化、编排、CI/CD完整流程
- **生产就绪**：基于成熟的云服务，具备生产级可靠性

## 4. 系统集成策略

### 4.1 服务通信模式

**前后端分离架构：**
```
用户浏览器 → GitHub Pages (React SPA) → AWS API Gateway → EKS (FastAPI) → RDS (PostgreSQL)
```

**API设计规范：**
- RESTful API设计，遵循HTTP语义
- OpenAPI 3.0规范，自动生成API文档
- 统一的错误处理和响应格式
- JWT token认证和授权

### 4.2 数据流设计

**数据录入流程：**
```
用户输入 → 前端验证 → API请求 → 后端验证 → 数据库存储 → 实时更新UI
```

**数据分析流程：**
```
查询请求 → 缓存检查 → 数据库查询 → 相关性计算 → 结果缓存 → 可视化展示
```

### 4.3 安全集成策略

**认证授权流程：**
```
用户登录 → Auth0认证 → JWT Token → API请求携带Token → 后端验证 → 授权访问
```

**数据安全措施：**
- HTTPS传输加密
- JWT token有效期管理
- API rate limiting防止滥用
- 用户数据行级隔离

现在，让我为您提供下一步的选择，继续架构文档的创建：

## 请选择继续的方向：

**1. 继续下一个章节** - 深入系统架构设计，包括：
   - 详细的组件架构图
   - 数据库设计详解
   - API接口规范
   - 部署架构图

**2. 转向实现规划** - 开始制定具体的开发计划：
   - 技术栈搭建步骤
   - 开发里程碑规划
   - 风险控制策略

**3. 深入技术细节** - 专注特定技术领域：
   - K3s部署配置详解
   - AWS免费tier使用策略
   - 数据分析算法实现

请告诉我您希望继续哪个方向，我将据此展开下一部分的详细内容。

## 5. 详细后端架构设计 (Detailed Backend Architecture)

### 5.1 API路由结构设计

**核心API模块架构：**
```python
# API路由层次结构
/api/v1/
├── /auth/                    # 认证相关
│   ├── POST /login          # 用户登录
│   ├── POST /logout         # 用户登出
│   ├── POST /refresh        # Token刷新
│   └── GET  /profile        # 用户信息
├── /dimensions/             # 维度数据管理
│   ├── GET    /             # 获取所有维度配置
│   ├── POST   /{dim}/data   # 创建维度数据记录
│   ├── GET    /{dim}/data   # 查询维度数据
│   ├── PUT    /{dim}/data/{id}  # 更新数据记录
│   └── DELETE /{dim}/data/{id}  # 删除数据记录
├── /matrix/                 # 矩阵分析功能
│   ├── GET  /overview       # 6维度总览矩阵
│   ├── GET  /correlations   # 跨维度相关性分析
│   ├── GET  /trends         # 时间趋势分析
│   └── POST /insights       # 生成个性化洞察
├── /analytics/              # 数据分析服务
│   ├── GET  /daily-summary  # 日度数据汇总
│   ├── GET  /weekly-report  # 周度数据报告
│   ├── GET  /monthly-stats  # 月度统计分析
│   └── GET  /custom-query   # 自定义查询分析
└── /system/                 # 系统管理接口
    ├── GET  /health         # 健康检查
    ├── GET  /metrics        # 系统指标
    └── POST /backup         # 数据备份触发
```

**API设计原则：**
- **RESTful规范**：使用标准HTTP方法和状态码
- **版本化管理**：/api/v1/前缀支持未来版本升级
- **统一响应格式**：所有API返回统一的JSON结构
- **错误处理标准化**：标准化错误码和错误信息

### 5.2 数据库Schema设计

**核心数据表结构：**
```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth0_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 维度配置表
CREATE TABLE dimensions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    data_schema JSONB NOT NULL,  -- 定义该维度的数据结构
    validation_rules JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 维度数据记录表
CREATE TABLE dimension_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dimension_id INTEGER NOT NULL REFERENCES dimensions(id),
    record_date DATE NOT NULL,
    record_time TIME DEFAULT NOW(),
    data JSONB NOT NULL,  -- 灵活存储不同维度的数据
    metadata JSONB DEFAULT '{}',  -- 存储额外元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 确保每个用户每个维度每天只有一条记录
    UNIQUE(user_id, dimension_id, record_date)
);

-- 相关性分析结果缓存表
CREATE TABLE correlation_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dimension_a INTEGER NOT NULL REFERENCES dimensions(id),
    dimension_b INTEGER NOT NULL REFERENCES dimensions(id),
    time_period VARCHAR(20) NOT NULL, -- 'week', 'month', 'quarter'
    correlation_value DECIMAL(5,4),
    confidence_level DECIMAL(5,4),
    sample_size INTEGER,
    calculation_params JSONB,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 复合索引优化查询性能
    INDEX idx_correlation_user_dims (user_id, dimension_a, dimension_b, time_period)
);

-- 系统配置表
CREATE TABLE system_config (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**数据模型设计理念：**
- **灵活性优先**：使用JSONB字段支持不同维度的个性化数据结构
- **性能优化**：合理的索引设计和分区策略
- **数据完整性**：外键约束确保数据一致性
- **用户隔离**：所有用户数据通过user_id完全隔离

### 5.3 认证授权流程设计

**Auth0集成架构：**
```python
# 认证流程服务层
class AuthenticationService:
    def __init__(self):
        self.auth0_domain = os.getenv('AUTH0_DOMAIN')
        self.auth0_audience = os.getenv('AUTH0_AUDIENCE')
        self.algorithm = 'RS256'
    
    async def verify_token(self, token: str) -> dict:
        """验证JWT token并返回用户信息"""
        try:
            # 1. 从Auth0获取公钥
            jwks_client = PyJWKClient(f"https://{self.auth0_domain}/.well-known/jwks.json")
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            
            # 2. 验证token签名和有效性
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=[self.algorithm],
                audience=self.auth0_audience,
                issuer=f"https://{self.auth0_domain}/"
            )
            
            # 3. 提取用户信息
            return {
                'user_id': payload.get('sub'),
                'email': payload.get('email'),
                'permissions': payload.get('permissions', [])
            }
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def get_or_create_user(self, auth0_user_id: str, email: str) -> User:
        """获取或创建用户记录"""
        # 数据库操作：根据auth0_user_id查找或创建用户
        pass
```

**权限控制策略：**
```python
# 基于装饰器的权限控制
class PermissionChecker:
    @staticmethod
    def require_auth(func):
        """要求用户认证的装饰器"""
        async def wrapper(*args, **kwargs):
            # 从请求头提取token并验证
            token = extract_token_from_header(request.headers)
            user_info = await auth_service.verify_token(token)
            request.current_user = user_info
            return await func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def require_own_data(func):
        """要求访问自己数据的装饰器"""
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or request.path_params.get('user_id')
            if user_id != request.current_user['user_id']:
                raise HTTPException(status_code=403, detail="Access denied")
            return await func(*args, **kwargs)
        return wrapper
```

### 5.4 数据处理服务架构

**核心业务服务层：**
```python
# 维度数据服务
class DimensionDataService:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def create_record(self, user_id: str, dimension: str, data: dict) -> DimensionRecord:
        """创建维度数据记录"""
        # 1. 验证数据格式
        dimension_config = await self.get_dimension_config(dimension)
        validated_data = self.validate_data_schema(data, dimension_config.data_schema)
        
        # 2. 检查重复记录
        existing = await self.get_record_by_date(user_id, dimension, data['date'])
        if existing:
            raise ValueError("Record already exists for this date")
        
        # 3. 创建记录
        record = DimensionRecord(
            user_id=user_id,
            dimension_id=dimension_config.id,
            record_date=data['date'],
            data=validated_data
        )
        
        # 4. 保存并触发相关性重计算
        self.db.add(record)
        await self.db.commit()
        await self.trigger_correlation_update(user_id, dimension)
        
        return record
    
    async def get_user_data(self, user_id: str, dimension: str, 
                           start_date: date, end_date: date) -> List[DimensionRecord]:
        """获取用户指定时间范围的维度数据"""
        return await self.db.query(DimensionRecord)\
            .filter(DimensionRecord.user_id == user_id)\
            .filter(DimensionRecord.dimension_id == dimension_id)\
            .filter(DimensionRecord.record_date.between(start_date, end_date))\
            .order_by(DimensionRecord.record_date)\
            .all()
```

**相关性分析服务：**
```python
class CorrelationAnalysisService:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def calculate_correlation(self, user_id: str, dim_a: str, dim_b: str, 
                                  time_period: str = 'month') -> CorrelationResult:
        """计算两个维度之间的相关性"""
        # 1. 检查缓存
        cached_result = await self.get_cached_correlation(user_id, dim_a, dim_b, time_period)
        if cached_result and not cached_result.is_expired():
            return cached_result
        
        # 2. 获取数据
        end_date = date.today()
        start_date = self.calculate_start_date(end_date, time_period)
        
        data_a = await self.dimension_service.get_user_data(user_id, dim_a, start_date, end_date)
        data_b = await self.dimension_service.get_user_data(user_id, dim_b, start_date, end_date)
        
        # 3. 数据预处理和对齐
        aligned_data = self.align_data_by_date(data_a, data_b)
        
        # 4. 计算相关性
        if len(aligned_data) < 7:  # 最少需要7个数据点
            return CorrelationResult(correlation=None, confidence=0, message="Insufficient data")
        
        correlation_value = self.calculate_pearson_correlation(aligned_data)
        confidence = self.calculate_confidence_level(aligned_data, correlation_value)
        
        # 5. 缓存结果
        result = CorrelationResult(
            correlation=correlation_value,
            confidence=confidence,
            sample_size=len(aligned_data),
            time_period=time_period,
            calculated_at=datetime.now()
        )
        
        await self.cache_correlation_result(user_id, dim_a, dim_b, result)
        return result
    
    def calculate_pearson_correlation(self, data_pairs: List[Tuple[float, float]]) -> float:
        """计算皮尔逊相关系数"""
        # 使用scipy.stats.pearsonr计算相关性
        x_values = [pair[0] for pair in data_pairs]
        y_values = [pair[1] for pair in data_pairs]
        
        correlation, p_value = pearsonr(x_values, y_values)
        return correlation if not np.isnan(correlation) else 0.0
```

**数据聚合分析服务：**
```python
class AnalyticsService:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    async def generate_daily_summary(self, user_id: str, target_date: date) -> DailySummary:
        """生成用户日度数据摘要"""
        # 1. 获取所有维度的当日数据
        all_dimensions = await self.get_active_dimensions()
        day_data = {}
        
        for dimension in all_dimensions:
            records = await self.dimension_service.get_user_data(
                user_id, dimension.name, target_date, target_date
            )
            if records:
                day_data[dimension.name] = records[0].data
        
        # 2. 计算完成度和健康分数
        completion_rate = len(day_data) / len(all_dimensions)
        health_score = self.calculate_health_score(day_data)
        
        # 3. 生成摘要
        return DailySummary(
            date=target_date,
            completion_rate=completion_rate,
            health_score=health_score,
            dimension_data=day_data,
            insights=await self.generate_daily_insights(day_data)
        )
    
    async def generate_weekly_report(self, user_id: str, week_start: date) -> WeeklyReport:
        """生成用户周度数据报告"""
        week_end = week_start + timedelta(days=6)
        
        # 1. 获取周度数据
        weekly_data = await self.get_weekly_aggregated_data(user_id, week_start, week_end)
        
        # 2. 计算趋势分析
        trends = await self.calculate_weekly_trends(user_id, weekly_data)
        
        # 3. 识别关键洞察
        insights = await self.identify_weekly_insights(weekly_data, trends)
        
        return WeeklyReport(
            week_start=week_start,
            week_end=week_end,
            daily_summaries=weekly_data,
            trends=trends,
            insights=insights,
            recommendations=await self.generate_recommendations(insights)
        )
```

### 5.5 性能优化策略

**数据库优化：**
```sql
-- 性能优化索引设计
CREATE INDEX CONCURRENTLY idx_dimension_records_user_date 
ON dimension_records(user_id, record_date DESC);

CREATE INDEX CONCURRENTLY idx_dimension_records_user_dim_date 
ON dimension_records(user_id, dimension_id, record_date DESC);

-- 分区表策略（针对大量历史数据）
CREATE TABLE dimension_records_y2024 PARTITION OF dimension_records
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

**缓存策略：**
```python
class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(os.getenv('REDIS_URL'))
    
    async def cache_correlation_result(self, key: str, result: dict, ttl: int = 3600):
        """缓存相关性分析结果"""
        await self.redis_client.setex(key, ttl, json.dumps(result))
    
    async def cache_analytics_summary(self, user_id: str, date_key: str, 
                                    summary: dict, ttl: int = 1800):
        """缓存用户分析摘要"""
        cache_key = f"analytics:{user_id}:{date_key}"
        await self.redis_client.setex(cache_key, ttl, json.dumps(summary))
```

---

继续下一部分，我将为您提供以下选择：

## 请选择继续的方向：

**1. 继续系统设计深入** - 完善架构设计文档：
   - 前端组件架构设计
   - 部署架构和监控设计
   - 安全性和数据保护策略
   - API文档自动生成规范

**2. 开始技术实现规划** - 转向具体开发计划：
   - 开发环境搭建步骤
   - 技术栈初始化配置
   - 数据库迁移和初始化
   - CI/CD流水线设置

**3. 深入特定技术领域** - 专注核心技术实现：
   - 数据相关性算法详细实现
   - K3s集群配置和部署
   - AWS免费tier资源配置优化

请选择您希望继续的方向，我将据此继续完善项目架构文档。

## 6. 详细前端架构设计 (Detailed Frontend Architecture)

### 6.1 React组件架构设计

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

### 6.2 状态管理架构

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

### 6.3 Cyberpunk UI设计实现

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

### 6.4 前后端数据流集成

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

### 6.5 性能优化策略

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

## 请选择继续的方向：

**1. 完善系统架构设计** - 继续架构文档的最后部分：
   - 部署架构和监控系统设计
   - 安全性和数据保护详细策略
   - API文档规范和错误处理
   - 系统可观测性和日志收集

**2. 开始技术实现准备** - 转向具体开发准备：
   - 前端项目初始化和脚手架搭建
   - 组件库和设计系统建立
   - 开发环境配置和工具链设置
   - 前后端集成测试环境

**3. 深入特定前端技术** - 专注前端核心实现：
   - Cyberpunk主题系统完整实现
   - 复杂数据可视化组件开发
   - 性能监控和优化工具集成
   - 响应式设计和移动端适配

请选择您希望继续的方向，我将据此完善项目的前端架构设计。

## 7. 详细数据架构和API接口设计 (Detailed Data Architecture & API Design)

### 7.1 完整数据流架构图

**数据生命周期完整流程：**

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[React前端界面]
        FORM[数据录入表单]
        MATRIX[矩阵可视化]
        DASHBOARD[仪表板]
    end
    
    subgraph "API Gateway Layer"
        GATEWAY[AWS API Gateway]
        AUTH[JWT认证中间件]
        RATE[限流控制]
        CORS[跨域处理]
    end
    
    subgraph "Application Layer"
        API[FastAPI应用]
        VALIDATE[数据验证服务]
        BUSINESS[业务逻辑层]
        ANALYTICS[分析计算服务]
        CACHE[Redis缓存]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL主库)]
        S3[(AWS S3存储)]
        BACKUP[(备份存储)]
    end
    
    subgraph "External Services"
        AUTH0[Auth0认证服务]
        MONITOR[CloudWatch监控]
    end
    
    UI --> GATEWAY
    FORM --> GATEWAY
    MATRIX --> GATEWAY
    DASHBOARD --> GATEWAY
    
    GATEWAY --> AUTH
    AUTH --> RATE
    RATE --> CORS
    CORS --> API
    
    API --> VALIDATE
    VALIDATE --> BUSINESS
    BUSINESS --> ANALYTICS
    ANALYTICS --> CACHE
    
    BUSINESS --> PG
    ANALYTICS --> PG
    API --> S3
    PG --> BACKUP
    
    AUTH --> AUTH0
    API --> MONITOR
```

**数据流处理层次：**

```typescript
// 数据处理管道设计
interface DataProcessingPipeline {
  input: RawUserInput;
  validation: ValidationResult;
  transformation: ProcessedData;
  storage: DatabaseRecord;
  analysis: AnalyticsResult;
  output: UserFacingData;
}

// 具体数据流实现
class DataPipeline {
  async processUserInput(input: RawUserInput): Promise<ProcessedDataResult> {
    // 1. 输入验证阶段
    const validationResult = await this.validateInput(input);
    if (!validationResult.isValid) {
      throw new ValidationError(validationResult.errors);
    }
    
    // 2. 数据转换阶段
    const transformedData = await this.transformData(input, validationResult);
    
    // 3. 数据存储阶段
    const storedRecord = await this.storeData(transformedData);
    
    // 4. 触发分析更新
    await this.triggerAnalyticsUpdate(storedRecord);
    
    // 5. 返回处理结果
    return {
      record: storedRecord,
      analytics: await this.getUpdatedAnalytics(storedRecord.user_id),
      correlations: await this.getAffectedCorrelations(storedRecord)
    };
  }
}
```

### 7.2 RESTful API完整规范设计

**API版本化和统一响应格式：**

```typescript
// API版本化策略
const API_BASE_URL = "/api/v1";

// 统一响应格式接口
interface APIResponse<T> {
  success: boolean;
  data: T | null;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  metadata?: {
    timestamp: string;
    version: string;
    request_id: string;
  };
}

// 分页响应格式
interface PaginatedResponse<T> extends APIResponse<T[]> {
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
}
```

**核心API端点详细设计：**

```python
# FastAPI路由完整实现
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import date, datetime

# 用户认证相关API
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/login")
async def login(credentials: LoginCredentials) -> APIResponse[AuthTokens]:
    """用户登录认证
    
    Args:
        credentials: 包含Auth0 token的登录凭据
        
    Returns:
        APIResponse[AuthTokens]: 包含access_token和refresh_token
        
    Raises:
        HTTPException: 401 if credentials invalid
    """
    pass

@auth_router.post("/refresh")
async def refresh_token(
    refresh_token: str,
    current_user: User = Depends(get_current_user)
) -> APIResponse[AuthTokens]:
    """刷新访问令牌"""
    pass

@auth_router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
) -> APIResponse[UserProfile]:
    """获取用户基本信息"""
    pass

@auth_router.put("/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user)
) -> APIResponse[UserProfile]:
    """更新用户基本信息"""
    pass

# 维度数据管理API
dimensions_router = APIRouter(prefix="/dimensions", tags=["Dimensions"])

@dimensions_router.get("/")
async def get_dimensions(
    current_user: User = Depends(get_current_user)
) -> APIResponse[List[DimensionConfig]]:
    """获取所有可用维度配置"""
    pass

@dimensions_router.get("/{dimension_id}/data")
async def get_dimension_data(
    dimension_id: str,
    start_date: date = Query(..., description="查询开始日期"),
    end_date: date = Query(..., description="查询结束日期"),
    current_user: User = Depends(get_current_user)
) -> APIResponse[List[DimensionRecord]]:
    """获取指定维度的用户数据
    
    Args:
        dimension_id: 维度标识符 (sleep, nutrition, exercise, mood, productivity, social)
        start_date: 查询开始日期
        end_date: 查询结束日期
        
    Returns:
        按日期排序的维度数据记录列表
    """
    pass

@dimensions_router.post("/{dimension_id}/data")
async def create_dimension_record(
    dimension_id: str,
    record_data: CreateDimensionRecordRequest,
    current_user: User = Depends(get_current_user)
) -> APIResponse[DimensionRecord]:
    """创建新的维度数据记录
    
    Args:
        dimension_id: 维度标识符
        record_data: 包含日期和维度数据的记录
        
    Returns:
        创建的维度数据记录
        
    Raises:
        HTTPException: 400 if validation fails
        HTTPException: 409 if record already exists for date
    """
    pass

@dimensions_router.put("/{dimension_id}/data/{record_id}")
async def update_dimension_record(
    dimension_id: str,
    record_id: str,
    record_data: UpdateDimensionRecordRequest,
    current_user: User = Depends(get_current_user)
) -> APIResponse[DimensionRecord]:
    """更新已存在的维度数据记录"""
    pass

@dimensions_router.delete("/{dimension_id}/data/{record_id}")
async def delete_dimension_record(
    dimension_id: str,
    record_id: str,
    current_user: User = Depends(get_current_user)
) -> APIResponse[None]:
    """删除维度数据记录"""
    pass

# 矩阵分析API
matrix_router = APIRouter(prefix="/matrix", tags=["Matrix Analysis"])

@matrix_router.get("/overview")
async def get_matrix_overview(
    time_period: str = Query("month", regex="^(week|month|quarter)$"),
    current_user: User = Depends(get_current_user)
) -> APIResponse[MatrixOverview]:
    """获取生活矩阵总览数据
    
    Args:
        time_period: 时间周期 (week/month/quarter)
        
    Returns:
        包含所有维度交叉相关性的矩阵数据
    """
    pass

@matrix_router.get("/correlations")
async def get_correlation_analysis(
    dimension_a: str = Query(..., description="第一个维度ID"),
    dimension_b: str = Query(..., description="第二个维度ID"),
    time_period: str = Query("month", regex="^(week|month|quarter)$"),
    current_user: User = Depends(get_current_user)
) -> APIResponse[CorrelationAnalysis]:
    """获取两个维度间的详细相关性分析
    
    Args:
        dimension_a: 第一个维度标识符
        dimension_b: 第二个维度标识符
        time_period: 分析时间周期
        
    Returns:
        详细的相关性分析结果，包含统计显著性
    """
    pass

@matrix_router.get("/trends")
async def get_trend_analysis(
    dimensions: List[str] = Query(..., description="要分析的维度列表"),
    time_period: str = Query("month", regex="^(week|month|quarter)$"),
    current_user: User = Depends(get_current_user)
) -> APIResponse[TrendAnalysis]:
    """获取多维度趋势分析"""
    pass

@matrix_router.post("/insights")
async def generate_insights(
    insight_request: InsightGenerationRequest,
    current_user: User = Depends(get_current_user)
) -> APIResponse[PersonalizedInsights]:
    """生成个性化数据洞察
    
    Args:
        insight_request: 包含分析参数的洞察生成请求
        
    Returns:
        基于用户数据的个性化洞察和建议
    """
    pass

# 数据分析API
analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])

@analytics_router.get("/daily-summary")
async def get_daily_summary(
    target_date: date = Query(..., description="目标日期"),
    current_user: User = Depends(get_current_user)
) -> APIResponse[DailySummary]:
    """获取指定日期的数据摘要"""
    pass

@analytics_router.get("/weekly-report")
async def get_weekly_report(
    week_start: date = Query(..., description="周开始日期"),
    current_user: User = Depends(get_current_user)
) -> APIResponse[WeeklyReport]:
    """获取指定周的数据报告"""
    pass

@analytics_router.get("/monthly-stats")
async def get_monthly_stats(
    year: int = Query(..., description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    current_user: User = Depends(get_current_user)
) -> APIResponse[MonthlyStatistics]:
    """获取指定月份的统计数据"""
    pass

@analytics_router.get("/custom-query")
async def execute_custom_query(
    query_params: CustomQueryParams = Depends(),
    current_user: User = Depends(get_current_user)
) -> APIResponse[CustomQueryResult]:
    """执行自定义数据查询分析"""
    pass

# 系统管理API
system_router = APIRouter(prefix="/system", tags=["System"])

@system_router.get("/health")
async def health_check() -> APIResponse[HealthStatus]:
    """系统健康检查"""
    return APIResponse(
        success=True,
        data=HealthStatus(
            status="healthy",
            timestamp=datetime.utcnow(),
            database_connected=True,
            cache_connected=True,
            external_services={"auth0": True, "s3": True}
        )
    )

@system_router.get("/metrics")
async def get_system_metrics(
    current_user: User = Depends(get_admin_user)
) -> APIResponse[SystemMetrics]:
    """获取系统运行指标（仅管理员）"""
    pass

@system_router.post("/backup")
async def trigger_backup(
    backup_type: str = "full",
    current_user: User = Depends(get_admin_user)
) -> APIResponse[BackupResult]:
    """触发数据备份（仅管理员）"""
    pass
```

### 7.3 数据模型和关系设计

**完整数据库Schema设计：**

```sql
-- ==========================================
-- 用户和认证相关表
-- ==========================================

-- 用户基础信息表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth0_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100),
    display_name VARCHAR(200),
    avatar_url TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
    theme_preference VARCHAR(20) DEFAULT 'cyberpunk',
    language_preference VARCHAR(10) DEFAULT 'en',
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- 索引优化
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- 用户会话管理表
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    refresh_token VARCHAR(255) UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_agent TEXT,
    ip_address INET,
    is_active BOOLEAN DEFAULT true
);

-- ==========================================
-- 数据维度配置表
-- ==========================================

-- 维度配置主表
CREATE TABLE dimensions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_name VARCHAR(50),
    color_theme VARCHAR(20),
    data_schema JSONB NOT NULL,  -- 该维度的数据结构定义
    validation_rules JSONB DEFAULT '{}',
    calculation_rules JSONB DEFAULT '{}',  -- 计算规则，如BMI等
    display_config JSONB DEFAULT '{}',  -- 显示配置
    is_core_dimension BOOLEAN DEFAULT false,  -- 是否为核心6维度
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户自定义维度表（扩展功能）
CREATE TABLE user_custom_dimensions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    data_schema JSONB NOT NULL,
    validation_rules JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, name)
);

-- ==========================================
-- 用户数据记录表
-- ==========================================

-- 主数据记录表
CREATE TABLE dimension_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dimension_id INTEGER REFERENCES dimensions(id),
    custom_dimension_id UUID REFERENCES user_custom_dimensions(id),
    record_date DATE NOT NULL,
    record_time TIME DEFAULT CURRENT_TIME,
    data JSONB NOT NULL,  -- 实际数据内容
    metadata JSONB DEFAULT '{}',  -- 元数据：数据源、设备信息等
    data_quality_score DECIMAL(3,2) DEFAULT 1.0,  -- 数据质量评分 0-1
    is_estimated BOOLEAN DEFAULT false,  -- 是否为估算数据
    notes TEXT,  -- 用户备注
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 确保每个用户每个维度每天只有一条记录
    CONSTRAINT unique_user_dimension_date UNIQUE(user_id, dimension_id, record_date),
    CONSTRAINT unique_user_custom_dimension_date UNIQUE(user_id, custom_dimension_id, record_date),
    -- 确保只能选择一种维度类型
    CONSTRAINT single_dimension_type CHECK (
        (dimension_id IS NOT NULL AND custom_dimension_id IS NULL) OR
        (dimension_id IS NULL AND custom_dimension_id IS NOT NULL)
    )
);

-- 子数据记录表（用于支持一天多次记录的维度，如运动）
CREATE TABLE dimension_sub_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_record_id UUID NOT NULL REFERENCES dimension_records(id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL,  -- 当天的序号
    start_time TIME,
    end_time TIME,
    data JSONB NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(parent_record_id, sequence_number)
);

-- ==========================================
-- 数据分析和缓存表
-- ==========================================

-- 相关性分析结果缓存表
CREATE TABLE correlation_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dimension_a_id INTEGER REFERENCES dimensions(id),
    dimension_b_id INTEGER REFERENCES dimensions(id),
    custom_dimension_a_id UUID REFERENCES user_custom_dimensions(id),
    custom_dimension_b_id UUID REFERENCES user_custom_dimensions(id),
    time_period VARCHAR(20) NOT NULL, -- 'week', 'month', 'quarter', 'year'
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    correlation_value DECIMAL(6,4),  -- 相关系数 -1 to 1
    confidence_level DECIMAL(5,4),   -- 置信水平 0 to 1
    p_value DECIMAL(10,8),           -- 统计显著性
    sample_size INTEGER,
    calculation_method VARCHAR(50) DEFAULT 'pearson',
    calculation_params JSONB,
    data_points JSONB,  -- 用于计算的数据点
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 复合索引优化查询性能
    CONSTRAINT single_dimension_pair_check CHECK (
        (dimension_a_id IS NOT NULL AND dimension_b_id IS NOT NULL AND 
         custom_dimension_a_id IS NULL AND custom_dimension_b_id IS NULL) OR
        (dimension_a_id IS NULL AND dimension_b_id IS NULL AND 
         custom_dimension_a_id IS NOT NULL AND custom_dimension_b_id IS NOT NULL) OR
        (dimension_a_id IS NOT NULL AND custom_dimension_b_id IS NOT NULL AND
         dimension_b_id IS NULL AND custom_dimension_a_id IS NULL) OR
        (custom_dimension_a_id IS NOT NULL AND dimension_b_id IS NOT NULL AND
         dimension_a_id IS NULL AND custom_dimension_b_id IS NULL)
    )
);

-- 数据统计摘要缓存表
CREATE TABLE analytics_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cache_type VARCHAR(50) NOT NULL,  -- 'daily', 'weekly', 'monthly', 'custom'
    cache_key VARCHAR(255) NOT NULL,  -- 缓存键
    time_period VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    data JSONB NOT NULL,              -- 缓存的分析结果
    metadata JSONB DEFAULT '{}',      -- 计算元数据
    calculation_duration INTEGER,     -- 计算耗时（毫秒）
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, cache_key)
);

-- ==========================================
-- 数据导出和备份表
-- ==========================================

-- 数据导出请求表
CREATE TABLE data_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    export_type VARCHAR(50) NOT NULL,  -- 'full', 'partial', 'dimension'
    export_format VARCHAR(20) NOT NULL, -- 'csv', 'json', 'xlsx'
    date_range JSONB,                  -- {start_date, end_date}
    dimension_filters JSONB,            -- 选择的维度
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    file_path TEXT,                    -- S3文件路径
    file_size BIGINT,                  -- 文件大小（字节）
    download_count INTEGER DEFAULT 0,
    expires_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 系统配置表
CREATE TABLE system_config (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    category VARCHAR(100),
    updated_by VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==========================================
-- 性能优化索引
-- ==========================================

-- 用户数据记录查询优化
CREATE INDEX CONCURRENTLY idx_dimension_records_user_date 
ON dimension_records(user_id, record_date DESC);

CREATE INDEX CONCURRENTLY idx_dimension_records_user_dim_date 
ON dimension_records(user_id, dimension_id, record_date DESC);

CREATE INDEX CONCURRENTLY idx_dimension_records_date_range 
ON dimension_records(user_id, record_date) 
WHERE record_date >= CURRENT_DATE - INTERVAL '1 year';

-- 相关性分析查询优化
CREATE INDEX CONCURRENTLY idx_correlation_cache_user_dims 
ON correlation_cache(user_id, dimension_a_id, dimension_b_id, time_period)
WHERE expires_at > NOW();

-- 分析缓存查询优化
CREATE INDEX CONCURRENTLY idx_analytics_cache_user_key 
ON analytics_cache(user_id, cache_key)
WHERE expires_at > NOW();

-- 数据导出查询优化
CREATE INDEX CONCURRENTLY idx_data_exports_user_status 
ON data_exports(user_id, status, created_at DESC);

-- JSONB数据查询优化（GIN索引）
CREATE INDEX CONCURRENTLY idx_dimension_records_data_gin 
ON dimension_records USING GIN(data);

CREATE INDEX CONCURRENTLY idx_users_preferences_gin 
ON users USING GIN(preferences);

-- ==========================================
-- 分区表策略（针对大量历史数据）
-- ==========================================

-- 按年分区历史数据表
CREATE TABLE dimension_records_y2024 PARTITION OF dimension_records
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE dimension_records_y2025 PARTITION OF dimension_records
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- ==========================================
-- 数据完整性约束和触发器
-- ==========================================

-- 更新时间戳触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表添加更新时间戳触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dimension_records_updated_at BEFORE UPDATE ON dimension_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_custom_dimensions_updated_at BEFORE UPDATE ON user_custom_dimensions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 数据质量检查函数
CREATE OR REPLACE FUNCTION validate_dimension_data(
    dimension_schema JSONB,
    user_data JSONB
) RETURNS BOOLEAN AS $$
DECLARE
    field_name TEXT;
    field_config JSONB;
    user_value JSONB;
BEGIN
    -- 遍历schema中定义的字段
    FOR field_name, field_config IN SELECT * FROM jsonb_each(dimension_schema->'fields')
    LOOP
        user_value := user_data->field_name;
        
        -- 检查必填字段
        IF (field_config->>'required')::BOOLEAN AND user_value IS NULL THEN
            RETURN FALSE;
        END IF;
        
        -- 检查数据类型（基础检查）
        IF user_value IS NOT NULL THEN
            CASE field_config->>'type'
                WHEN 'number' THEN
                    IF NOT jsonb_typeof(user_value) = 'number' THEN
                        RETURN FALSE;
                    END IF;
                WHEN 'string' THEN
                    IF NOT jsonb_typeof(user_value) = 'string' THEN
                        RETURN FALSE;
                    END IF;
                WHEN 'boolean' THEN
                    IF NOT jsonb_typeof(user_value) = 'boolean' THEN
                        RETURN FALSE;
                    END IF;
            END CASE;
        END IF;
    END LOOP;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;
```

### 7.4 核心6维度数据Schema定义

**维度数据结构标准化：**

```json
{
  "sleep": {
    "display_name": "睡眠维度",
    "description": "睡眠质量和作息规律追踪",
    "fields": {
      "bedtime": {
        "type": "time",
        "label": "就寝时间",
        "required": true,
        "default": "23:00"
      },
      "wake_time": {
        "type": "time", 
        "label": "起床时间",
        "required": true,
        "default": "07:30"
      },
      "sleep_quality": {
        "type": "number",
        "label": "睡眠质量",
        "min": 1,
        "max": 10,
        "required": true,
        "unit": "分"
      },
      "morning_alertness": {
        "type": "number",
        "label": "晨起清醒度",
        "min": 1,
        "max": 10,
        "required": true,
        "unit": "分"
      }
    },
    "calculated_fields": {
      "total_sleep_hours": {
        "formula": "wake_time - bedtime",
        "type": "number",
        "unit": "小时"
      },
      "sleep_efficiency": {
        "formula": "sleep_quality * 10",
        "type": "number",
        "unit": "%"
      }
    }
  },
  
  "nutrition": {
    "display_name": "饮食营养",
    "description": "营养摄入和饮食结构追踪",
    "fields": {
      "total_calories": {
        "type": "number",
        "label": "总热量",
        "required": true,
        "min": 800,
        "max": 5000,
        "unit": "kcal"
      },
      "protein": {
        "type": "number",
        "label": "蛋白质",
        "required": true,
        "min": 0,
        "max": 500,
        "unit": "g"
      },
      "fat": {
        "type": "number",
        "label": "脂肪",
        "required": true,
        "min": 0,
        "max": 300,
        "unit": "g"
      },
      "carbohydrates": {
        "type": "number",
        "label": "碳水化合物",
        "required": true,
        "min": 0,
        "max": 800,
        "unit": "g"
      },
      "water_intake": {
        "type": "number",
        "label": "饮水量",
        "required": false,
        "min": 0,
        "max": 5000,
        "unit": "ml"
      }
    },
    "calculated_fields": {
      "protein_percentage": {
        "formula": "(protein * 4) / total_calories * 100",
        "type": "number",
        "unit": "%"
      },
      "carb_percentage": {
        "formula": "(carbohydrates * 4) / total_calories * 100", 
        "type": "number",
        "unit": "%"
      },
      "fat_percentage": {
        "formula": "(fat * 9) / total_calories * 100",
        "type": "number", 
        "unit": "%"
      }
    }
  },
  
  "exercise": {
    "display_name": "运动锻炼",
    "description": "运动量和训练强度追踪",
    "fields": {
      "total_duration": {
        "type": "number",
        "label": "总训练时长",
        "required": true,
        "min": 0,
        "max": 480,
        "unit": "分钟"
      },
      "steps_count": {
        "type": "number",
        "label": "步数",
        "required": false,
        "min": 0,
        "max": 50000,
        "unit": "步"
      },
      "strength_training": {
        "type": "object",
        "label": "力量训练",
        "required": false,
        "properties": {
          "duration": {"type": "number", "min": 0, "max": 180, "unit": "分钟"},
          "intensity": {"type": "number", "min": 1, "max": 10, "unit": "分"},
          "feeling": {"type": "number", "min": 1, "max": 10, "unit": "分"}
        }
      },
      "cardio_training": {
        "type": "object",
        "label": "有氧训练",
        "required": false,
        "properties": {
          "duration": {"type": "number", "min": 0, "max": 180, "unit": "分钟"},
          "type": {"type": "string", "enum": ["running", "cycling", "swimming", "hiit", "machine", "other"]},
          "intensity": {"type": "number", "min": 1, "max": 10, "unit": "分"},
          "feeling": {"type": "number", "min": 1, "max": 10, "unit": "分"}
        }
      }
    },
    "calculated_fields": {
      "activity_score": {
        "formula": "total_duration * 0.1 + steps_count * 0.0001",
        "type": "number",
        "unit": "分"
      }
    }
  },
  
  "mood": {
    "display_name": "情绪状态",
    "description": "情绪健康和心理状态追踪",
    "fields": {
      "overall_mood": {
        "type": "number",
        "label": "整体心情",
        "required": true,
        "min": 1,
        "max": 10,
        "unit": "分"
      },
      "stress_level": {
        "type": "number",
        "label": "压力感",
        "required": true,
        "min": 1,
        "max": 10,
        "unit": "分"
      },
      "anxiety_level": {
        "type": "number",
        "label": "焦虑程度",
        "required": true,
        "min": 1,
        "max": 10,
        "unit": "分"
      },
      "energy_level": {
        "type": "number",
        "label": "精力水平",
        "required": true,
        "min": 1,
        "max": 10,
        "unit": "分"
      },
      "emotional_notes": {
        "type": "string",
        "label": "情绪备注",
        "required": false,
        "max_length": 500
      }
    },
    "calculated_fields": {
      "mental_health_score": {
        "formula": "(overall_mood + (11 - stress_level) + (11 - anxiety_level) + energy_level) / 4",
        "type": "number",
        "unit": "分"
      }
    }
  },
  
  "productivity": {
    "display_name": "工作效率",
    "description": "工作表现和专注度追踪",
    "fields": {
      "deep_work_hours": {
        "type": "number",
        "label": "深度工作时长",
        "required": true,
        "min": 0,
        "max": 16,
        "unit": "小时"
      },
      "break_count": {
        "type": "number",
        "label": "主动休息次数",
        "required": true,
        "min": 0,
        "max": 20,
        "unit": "次"
      },
      "focus_quality": {
        "type": "number",
        "label": "专注质量",
        "required": true,
        "min": 1,
        "max": 10,
        "unit": "分"
      },
      "task_completion": {
        "type": "number",
        "label": "任务完成度",
        "required": true,
        "min": 1,
        "max": 10,
        "unit": "分"
      },
      "work_satisfaction": {
        "type": "number",
        "label": "工作满意度",
        "required": true,
        "min": 1,
        "max": 10,
        "unit": "分"
      },
      "work_environment": {
        "type": "string",
        "label": "工作环境",
        "required": true,
        "enum": ["home", "office", "cafe", "mixed"]
      }
    },
    "calculated_fields": {
      "productivity_score": {
        "formula": "(deep_work_hours * 0.3 + focus_quality * 0.3 + task_completion * 0.4)",
        "type": "number",
        "unit": "分"
      }
    }
  },
  
  "social": {
    "display_name": "社交互动",
    "description": "社交活动和人际关系追踪",
    "fields": {
      "initiated_contacts": {
        "type": "number",
        "label": "发起社交次数",
        "required": true,
        "min": 0,
        "max": 50,
        "unit": "次"
      },
      "responded_contacts": {
        "type": "number",
        "label": "响应社交次数",
        "required": true,
        "min": 0,
        "max": 50,
        "unit": "次"
      },
      "social_satisfaction": {
        "type": "number",
        "label": "人际满意度",
        "required": true,
        "min": 1,
        "max": 10,
        "unit": "分"
      },
      "alone_satisfaction": {
        "type": "number",
        "label": "独处满足度",
        "required": true,
        "min": 1,
        "max": 10,
        "unit": "分"
      },
      "social_energy": {
        "type": "number",
        "label": "社交精力",
        "required": false,
        "min": 1,
        "max": 10,
        "unit": "分"
      }
    },
    "calculated_fields": {
      "social_balance_score": {
        "formula": "(social_satisfaction + alone_satisfaction) / 2",
        "type": "number",
        "unit": "分"  
      },
      "social_activity_level": {
        "formula": "initiated_contacts + responded_contacts",
        "type": "number",
        "unit": "次"
      }
    }
  }
}
```

### 7.5 集成模式和数据同步策略

**服务间集成架构：**

```typescript
// 事件驱动架构设计
interface EventBus {
  publish(event: DomainEvent): Promise<void>;
  subscribe(eventType: string, handler: EventHandler): void;
}

// 领域事件定义
abstract class DomainEvent {
  abstract eventType: string;
  abstract payload: any;
  timestamp: Date = new Date();
  userId: string;
  eventId: string = crypto.randomUUID();
}

class DimensionDataUpdatedEvent extends DomainEvent {
  eventType = 'dimension.data.updated';
  
  constructor(
    public userId: string,
    public payload: {
      dimensionId: string;
      recordId: string;
      previousData: any;
      newData: any;
      recordDate: string;
    }
  ) {
    super();
  }
}

class CorrelationUpdateRequiredEvent extends DomainEvent {
  eventType = 'correlation.update.required';
  
  constructor(
    public userId: string,
    public payload: {
      affectedDimensions: string[];
      priority: 'high' | 'medium' | 'low';
    }
  ) {
    super();
  }
}

// 事件处理器实现
class CorrelationUpdateHandler implements EventHandler {
  async handle(event: DimensionDataUpdatedEvent): Promise<void> {
    // 1. 识别需要重新计算的相关性对
    const affectedPairs = await this.identifyAffectedCorrelationPairs(
      event.userId, 
      event.payload.dimensionId
    );
    
    // 2. 异步触发相关性重计算
    for (const pair of affectedPairs) {
      await this.correlationService.scheduleRecalculation(
        event.userId,
        pair.dimensionA,
        pair.dimensionB,
        { priority: 'medium' }
      );
    }
    
    // 3. 清除相关缓存
    await this.cacheService.invalidateCorrelationCache(
      event.userId,
      event.payload.dimensionId
    );
  }
}

// 实时数据同步服务
class DataSyncService {
  private websocketManager: WebSocketManager;
  private eventBus: EventBus;
  
  constructor() {
    this.setupEventHandlers();
  }
  
  private setupEventHandlers(): void {
    this.eventBus.subscribe('dimension.data.updated', async (event) => {
      // 通过WebSocket推送数据更新
      await this.websocketManager.broadcastToUser(event.userId, {
        type: 'data_updated',
        payload: {
          dimensionId: event.payload.dimensionId,
          recordId: event.payload.recordId,
          newData: event.payload.newData
        }
      });
    });
    
    this.eventBus.subscribe('correlation.calculated', async (event) => {
      // 推送相关性分析结果更新
      await this.websocketManager.broadcastToUser(event.userId, {
        type: 'correlation_updated',
        payload: event.payload
      });
    });
  }
  
  // 数据冲突解决策略
  async resolveDataConflict(
    userId: string,
    recordId: string,
    clientData: any,
    serverData: any
  ): Promise<ConflictResolution> {
    // 基于时间戳的冲突解决（Last Write Wins）
    if (clientData.updated_at > serverData.updated_at) {
      return {
        resolution: 'client_wins',
        mergedData: clientData,
        conflictReason: 'client_data_newer'
      };
    } else {
      return {
        resolution: 'server_wins',
        mergedData: serverData,
        conflictReason: 'server_data_newer'
      };
    }
  }
}
```

**API限流和缓存策略：**

```python
# API限流装饰器
from functools import wraps
import time
from typing import Dict, Any
import redis

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def limit(self, key: str, limit: int, window: int):
        """
        限流装饰器
        
        Args:
            key: 限流键前缀
            limit: 限制次数
            window: 时间窗口（秒）
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                request = kwargs.get('request')
                user_id = kwargs.get('current_user', {}).get('id', 'anonymous')
                
                # 构造限流键
                rate_limit_key = f"rate_limit:{key}:{user_id}"
                
                # 检查当前请求次数
                current_requests = self.redis.get(rate_limit_key)
                if current_requests is None:
                    # 首次请求，设置计数器
                    self.redis.setex(rate_limit_key, window, 1)
                elif int(current_requests) >= limit:
                    # 超出限制
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Max {limit} requests per {window} seconds"
                    )
                else:
                    # 增加计数器
                    self.redis.incr(rate_limit_key)
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator

# 缓存服务实现
class CacheService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = 3600  # 1小时
    
    async def get_or_compute(
        self, 
        cache_key: str, 
        compute_func: callable,
        ttl: int = None
    ) -> Any:
        """获取缓存或计算新值"""
        # 尝试从缓存获取
        cached_value = await self.redis.get(cache_key)
        if cached_value:
            return json.loads(cached_value)
        
        # 缓存未命中，计算新值
        computed_value = await compute_func()
        
        # 存储到缓存
        await self.redis.setex(
            cache_key, 
            ttl or self.default_ttl,
            json.dumps(computed_value, default=str)
        )
        
        return computed_value
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """按模式删除缓存"""
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0
    
    # 分层缓存策略
    async def get_user_analytics(
        self, 
        user_id: str, 
        cache_type: str,
        date_range: DateRange
    ) -> Any:
        # L1缓存：内存缓存（短期，高频访问）
        l1_key = f"l1:analytics:{user_id}:{cache_type}:{date_range.hash()}"
        l1_result = self.memory_cache.get(l1_key)
        if l1_result:
            return l1_result
        
        # L2缓存：Redis缓存（中期，跨请求）
        l2_key = f"l2:analytics:{user_id}:{cache_type}:{date_range.hash()}"
        l2_result = await self.redis.get(l2_key)
        if l2_result:
            result = json.loads(l2_result)
            self.memory_cache.set(l1_key, result, ttl=300)  # 5分钟内存缓存
            return result
        
        # L3缓存：数据库缓存表（长期，持久化）
        l3_result = await self.db_cache.get_analytics_cache(
            user_id, cache_type, date_range
        )
        if l3_result and not l3_result.is_expired():
            result = l3_result.data
            # 回写到上层缓存
            await self.redis.setex(l2_key, 1800, json.dumps(result, default=str))
            self.memory_cache.set(l1_key, result, ttl=300)
            return result
        
        # 缓存全部未命中，重新计算
        return None

# 应用到具体API端点
@matrix_router.get("/correlations")
@rate_limiter.limit("matrix_correlations", limit=30, window=60)  # 每分钟30次 
async def get_correlation_analysis(
    dimension_a: str = Query(...),
    dimension_b: str = Query(...),
    time_period: str = Query("month"),
    current_user: User = Depends(get_current_user)
) -> APIResponse[CorrelationAnalysis]:
    
    cache_key = f"correlation:{current_user.id}:{dimension_a}:{dimension_b}:{time_period}"
    
    result = await cache_service.get_or_compute(
        cache_key,
        lambda: correlation_service.calculate_correlation(
            current_user.id, dimension_a, dimension_b, time_period
        ),
        ttl=1800  # 30分钟缓存
    )
    
    return APIResponse(success=True, data=result)
```

## 7. 部署架构和基础设施 (Deployment & Infrastructure Architecture)

### 7.1 零成本部署策略

**AWS免费Tier资源规划：**
```yaml
计算资源:
  EKS免费集群: "1个集群/月"
  EC2 t2.micro: "750小时/月"
  Lambda函数: "100万次请求/月"

存储资源:
  S3存储: "5GB标准存储"
  EBS通用SSD: "30GB/月"
  RDS PostgreSQL: "20GB存储"

网络资源:
  数据传输: "15GB出站/月"
  CloudFront: "50GB数据传输"
  Route53: "25个托管区域查询"
```

**资源分配策略：**
```yaml
前端部署:
  平台: "GitHub Pages"
  CDN: "CloudFront免费tier"
  域名: "免费Freenom域名"
  证书: "Let's Encrypt免费SSL"

后端部署:
  集群: "AWS EKS免费控制平面"
  节点: "1x t2.micro EC2实例"
  负载均衡: "ALB免费tier"
  
数据库:
  主库: "RDS PostgreSQL t3.micro"
  缓存: "ElastiCache Redis t2.micro"
  备份: "自动备份7天保留"

监控:
  日志: "CloudWatch Logs 5GB/月"
  指标: "CloudWatch免费指标"
  告警: "10个免费告警"
```

### 7.2 K3s轻量级编排配置

**K3s集群架构：**
```yaml
# k3s-cluster.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: livin-matrix
---
# 应用配置映射
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: livin-matrix
data:
  NODE_ENV: "production"
  DATABASE_URL: "postgresql://user:pass@rds-endpoint:5432/livinmatrix"
  REDIS_URL: "redis://elasticache-endpoint:6379"
  AUTH0_DOMAIN: "livin-matrix.auth0.com"
  CORS_ORIGINS: "https://livin-matrix.github.io"
  LOG_LEVEL: "info"

---
# 密钥管理
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: livin-matrix
type: Opaque
stringData:
  DATABASE_PASSWORD: "${DB_PASSWORD}"
  AUTH0_CLIENT_SECRET: "${AUTH0_SECRET}"
  JWT_SECRET: "${JWT_SECRET}"
  REDIS_PASSWORD: "${REDIS_PASSWORD}"
```

**部署清单定义：**
```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: livin-matrix-backend
  namespace: livin-matrix
spec:
  replicas: 1  # 免费tier限制
  selector:
    matchLabels:
      app: livin-matrix-backend
  template:
    metadata:
      labels:
        app: livin-matrix-backend
    spec:
      containers:
      - name: backend
        image: livin-matrix/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: DATABASE_URL
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DATABASE_PASSWORD
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# 服务暴露
apiVersion: v1
kind: Service
metadata:
  name: livin-matrix-backend-service
  namespace: livin-matrix
spec:
  selector:
    app: livin-matrix-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP

---
# Ingress配置
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: livin-matrix-ingress
  namespace: livin-matrix
  annotations:
    kubernetes.io/ingress.class: "alb"
    alb.ingress.kubernetes.io/target-type: "ip"
    alb.ingress.kubernetes.io/certificate-arn: "${SSL_CERT_ARN}"
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/ssl-redirect: '443'
spec:
  rules:
  - host: api.livin-matrix.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: livin-matrix-backend-service
            port:
              number: 80
```

### 7.3 CI/CD流水线设计

**GitHub Actions工作流：**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  AWS_REGION: us-east-1
  EKS_CLUSTER_NAME: livin-matrix-cluster
  REGISTRY: ghcr.io
  IMAGE_NAME: livin-matrix

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run backend tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
          REDIS_URL: redis://localhost:6379
          AUTH0_DOMAIN: test.auth0.com
          AUTH0_CLIENT_ID: test-client-id
          AUTH0_CLIENT_SECRET: test-secret
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-report=term

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci

      - name: Run frontend tests
        run: |
          cd frontend
          npm run test:ci

      - name: Frontend build test
        run: |
          cd frontend
          npm run build

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          flags: backend
          name: backend-coverage

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Build frontend for GitHub Pages
        run: |
          cd frontend
          npm ci
          npm run build
          
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend/dist
          cname: livin-matrix.com

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --region ${{ env.AWS_REGION }} --name ${{ env.EKS_CLUSTER_NAME }}

      - name: Deploy to EKS
        run: |
          # 替换镜像标签
          sed -i "s|livin-matrix/backend:latest|${{ env.REGISTRY }}/${{ github.repository }}/${{ env.IMAGE_NAME }}:${{ github.sha }}|g" k8s/backend-deployment.yaml
          
          # 应用Kubernetes配置
          kubectl apply -f k8s/namespace.yaml
          kubectl apply -f k8s/configmap.yaml
          kubectl apply -f k8s/secrets.yaml
          kubectl apply -f k8s/backend-deployment.yaml
          kubectl apply -f k8s/ingress.yaml
          
          # 等待部署完成
          kubectl rollout status deployment/livin-matrix-backend -n livin-matrix --timeout=600s

      - name: Verify deployment
        run: |
          kubectl get pods -n livin-matrix
          kubectl get services -n livin-matrix
          kubectl get ingress -n livin-matrix
```

### 7.4 基础设施即代码 (Infrastructure as Code)

**Terraform AWS配置：**
```hcl
# infrastructure/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "livin-matrix-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "LiVin-Matrix"
      Environment = var.environment
      ManagedBy   = "Terraform"
      CostCenter  = "Education"
    }
  }
}

# VPC和网络配置
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = data.aws_availability_zones.available.names
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = false  # 节省成本
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# EKS集群配置
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # 免费tier控制平面
  cluster_endpoint_public_access = true
  cluster_endpoint_private_access = false

  # 节点组配置
  eks_managed_node_groups = {
    main = {
      min_size     = 1
      max_size     = 2
      desired_size = 1

      instance_types = ["t3.micro"]  # 免费tier
      capacity_type  = "ON_DEMAND"
      
      k8s_labels = {
        Environment = var.environment
      }
    }
  }

  # OIDC身份提供者
  enable_irsa = true

  tags = {
    Environment = var.environment
  }
}

# RDS PostgreSQL数据库
resource "aws_db_instance" "main" {
  identifier = "${var.project_name}-db"

  engine         = "postgres"
  engine_version = "15.4"
  instance_class = "db.t3.micro"  # 免费tier

  allocated_storage     = 20  # 免费tier最大值
  max_allocated_storage = 20  # 防止自动扩展
  storage_type         = "gp2"
  storage_encrypted    = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name = "${var.project_name}-database"
  }
}

# ElastiCache Redis缓存
resource "aws_elasticache_subnet_group" "main" {
  name       = "${var.project_name}-cache-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_elasticache_cluster" "main" {
  cluster_id           = "${var.project_name}-cache"
  engine               = "redis"
  node_type            = "cache.t2.micro"  # 免费tier
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]

  tags = {
    Name = "${var.project_name}-redis"
  }
}

# S3存储桶
resource "aws_s3_bucket" "uploads" {
  bucket = "${var.project_name}-uploads-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "${var.project_name}-uploads"
  }
}

resource "aws_s3_bucket_versioning" "uploads" {
  bucket = aws_s3_bucket.uploads.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# CloudFront CDN分发
resource "aws_cloudfront_distribution" "main" {
  origin {
    domain_name = aws_s3_bucket.uploads.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.uploads.bucket}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.main.cloudfront_access_identity_path
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods        = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "S3-${aws_s3_bucket.uploads.bucket}"
    compress               = true
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name = "${var.project_name}-cdn"
  }
}
```

**变量定义：**
```hcl
# infrastructure/variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "livin-matrix"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "livin-matrix-cluster"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "livinmatrix"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# infrastructure/outputs.tf
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = module.eks.cluster_security_group_id
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.main.cache_nodes[0].address
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = aws_s3_bucket.uploads.bucket
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.main.domain_name
}
```

**安全组配置：**
```hcl
# infrastructure/security.tf
resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

resource "aws_security_group" "redis" {
  name_prefix = "${var.project_name}-redis-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-redis-sg"
  }
}
```

### 7.5 监控和可观测性

**Prometheus + Grafana监控栈：**
```yaml
# k8s/monitoring/prometheus.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: livin-matrix
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus
        - name: prometheus-storage
          mountPath: /prometheus
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
      - name: prometheus-storage
        emptyDir: {}

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: livin-matrix
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "alert_rules.yml"
    
    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093
    
    scrape_configs:
      - job_name: 'kubernetes-apiservers'
        kubernetes_sd_configs:
        - role: endpoints
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
        - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
          action: keep
          regex: default;kubernetes;https
      
      - job_name: 'livin-matrix-backend'
        static_configs:
          - targets: ['livin-matrix-backend-service:80']
        metrics_path: '/metrics'
        scrape_interval: 30s

  alert_rules.yml: |
    groups:
    - name: livin-matrix.rules
      rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: DatabaseConnectionFailed
        expr: up{job="postgres-exporter"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failed"
          description: "Cannot connect to PostgreSQL database"
```

**Grafana仪表板配置：**
```yaml
# k8s/monitoring/grafana.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: livin-matrix
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-secrets
              key: admin-password
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
        - name: grafana-datasources
          mountPath: /etc/grafana/provisioning/datasources
        - name: grafana-dashboards
          mountPath: /etc/grafana/provisioning/dashboards
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
      volumes:
      - name: grafana-storage
        emptyDir: {}
      - name: grafana-datasources
        configMap:
          name: grafana-datasources
      - name: grafana-dashboards
        configMap:
          name: grafana-dashboards

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: livin-matrix
data:
  datasources.yaml: |
    apiVersion: 1
    datasources:
      - name: Prometheus
        type: prometheus
        access: proxy
        url: http://prometheus:9090
        isDefault: true
        editable: true

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
  namespace: livin-matrix
data:
  dashboards.yaml: |
    apiVersion: 1
    providers:
      - name: 'default'
        orgId: 1
        folder: ''
        type: file
        disableDeletion: false
        editable: true
        options:
          path: /var/lib/grafana/dashboards
  
  livin-matrix-dashboard.json: |
    {
      "dashboard": {
        "id": null,
        "title": "LiVin Matrix Application Metrics",
        "tags": ["livin-matrix"],
        "timezone": "browser",
        "panels": [
          {
            "id": 1,
            "title": "Request Rate",
            "type": "graph",
            "targets": [
              {
                "expr": "rate(http_requests_total[5m])",
                "legendFormat": "{{method}} {{endpoint}}"
              }
            ],
            "yAxes": [
              {
                "label": "Requests/sec"
              }
            ],
            "gridPos": {
              "h": 8,
              "w": 12,
              "x": 0,
              "y": 0
            }
          },
          {
            "id": 2,
            "title": "Response Time",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                "legendFormat": "95th percentile"
              },
              {
                "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
                "legendFormat": "50th percentile"
              }
            ],
            "yAxes": [
              {
                "label": "Seconds"
              }
            ],
            "gridPos": {
              "h": 8,
              "w": 12,
              "x": 12,
              "y": 0
            }
          },
          {
            "id": 3,
            "title": "Error Rate",
            "type": "singlestat",
            "targets": [
              {
                "expr": "rate(http_requests_total{status=~\"5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
                "legendFormat": "Error Rate %"
              }
            ],
            "gridPos": {
              "h": 4,
              "w": 8,
              "x": 0,
              "y": 8
            }
          },
          {
            "id": 4,
            "title": "Active Users",
            "type": "singlestat",
            "targets": [
              {
                "expr": "active_users_total",
                "legendFormat": "Active Users"
              }
            ],
            "gridPos": {
              "h": 4,
              "w": 8,
              "x": 8,
              "y": 8
            }
          },
          {
            "id": 5,
            "title": "Database Connections",
            "type": "singlestat",
            "targets": [
              {
                "expr": "pg_stat_database_numbackends",
                "legendFormat": "DB Connections"
              }
            ],
            "gridPos": {
              "h": 4,
              "w": 8,
              "x": 16,
              "y": 8
            }
          }
        ],
        "time": {
          "from": "now-1h",
          "to": "now"
        },
        "refresh": "30s"
      }
    }
```

### 7.6 日志收集和分析

**Fluentd日志收集配置：**
```yaml
# k8s/logging/fluentd.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: livin-matrix
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-cloudwatch
        env:
        - name: AWS_REGION
          value: "us-east-1"
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: fluentd-secrets
              key: aws-access-key-id
        - name: AWS_SECRET_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: fluentd-secrets
              key: aws-secret-access-key
        - name: LOG_GROUP_NAME
          value: "/aws/eks/livin-matrix"
        resources:
          limits:
            memory: 256Mi
          requests:
            cpu: 100m
            memory: 128Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: fluent-conf
          mountPath: /fluentd/etc/fluent.conf
          subPath: fluent.conf
      terminationGracePeriodSeconds: 30
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: fluent-conf
        configMap:
          name: fluentd-config

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: livin-matrix
data:
  fluent.conf: |
    @include systemd.conf
    @include kubernetes.conf
    
    <match **>
      @type cloudwatch_logs
      log_group_name "#{ENV['LOG_GROUP_NAME']}"
      log_stream_name_key stream_name
      auto_create_stream true
      remove_log_stream_name_key true
      
      <buffer>
        @type file
        path /var/log/fluentd-buffers/cloudwatch.buffer
        flush_interval 5s
        chunk_limit_size 2m
        queue_limit_length 32
        retry_limit 3
      </buffer>
    </match>
```

### 7.7 安全和备份策略

**备份脚本配置：**
```bash
#!/bin/bash
# scripts/backup.sh

set -euo pipefail

# 环境变量
BACKUP_BUCKET="livin-matrix-backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/tmp/backup_${TIMESTAMP}"

# 数据库备份
echo "Starting database backup..."
mkdir -p "${BACKUP_DIR}"

# PostgreSQL数据库备份
PGPASSWORD="${DATABASE_PASSWORD}" pg_dump \
  -h "${DATABASE_HOST}" \
  -p "${DATABASE_PORT}" \
  -U "${DATABASE_USER}" \
  -d "${DATABASE_NAME}" \
  --format=custom \
  --compress=9 \
  --file="${BACKUP_DIR}/database_${TIMESTAMP}.dump"

# 压缩备份文件
echo "Compressing backup..."
tar -czf "${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz" -C "${BACKUP_DIR}" .

# 上传到S3
echo "Uploading to S3..."
aws s3 cp "${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz" \
  "s3://${BACKUP_BUCKET}/database/backup_${TIMESTAMP}.tar.gz" \
  --storage-class STANDARD_IA

# 清理本地文件
rm -rf "${BACKUP_DIR}"

# 清理旧备份（保留30天）
echo "Cleaning old backups..."
aws s3 ls "s3://${BACKUP_BUCKET}/database/" | \
  while read -r line; do
    createDate=$(echo "${line}" | awk '{print $1" "$2}')
    createDate=$(date -d "${createDate}" +%s)
    olderThan=$(date -d "30 days ago" +%s)
    
    if [[ ${createDate} -lt ${olderThan} ]]; then
      fileName=$(echo "${line}" | awk '{print $4}')
      if [[ ${fileName} != "" ]]; then
        aws s3 rm "s3://${BACKUP_BUCKET}/database/${fileName}"
      fi
    fi
  done

echo "Backup completed successfully!"
```

**灾难恢复流程：**
```bash
#!/bin/bash
# scripts/restore.sh

set -euo pipefail

BACKUP_BUCKET="livin-matrix-backups"
RESTORE_DATE=${1:-$(date +"%Y%m%d")}
TEMP_DIR="/tmp/restore_${RESTORE_DATE}"

echo "Starting disaster recovery for date: ${RESTORE_DATE}"

# 创建临时目录
mkdir -p "${TEMP_DIR}"

# 查找最新的备份文件
BACKUP_FILE=$(aws s3 ls "s3://${BACKUP_BUCKET}/database/" | \
  grep "${RESTORE_DATE}" | \
  sort | tail -n 1 | awk '{print $4}')

if [[ -z "${BACKUP_FILE}" ]]; then
  echo "No backup found for date: ${RESTORE_DATE}"
  exit 1
fi

echo "Found backup file: ${BACKUP_FILE}"

# 下载备份文件
aws s3 cp "s3://${BACKUP_BUCKET}/database/${BACKUP_FILE}" "${TEMP_DIR}/"

# 解压备份
cd "${TEMP_DIR}"
tar -xzf "${BACKUP_FILE}"

# 停止应用服务
echo "Stopping application services..."
kubectl scale deployment livin-matrix-backend --replicas=0 -n livin-matrix

# 恢复数据库
echo "Restoring database..."
PGPASSWORD="${DATABASE_PASSWORD}" pg_restore \
  -h "${DATABASE_HOST}" \
  -p "${DATABASE_PORT}" \
  -U "${DATABASE_USER}" \
  -d "${DATABASE_NAME}" \
  --clean --if-exists \
  --verbose \
  "database_${RESTORE_DATE}*.dump"

# 重启应用服务
echo "Restarting application services..."
kubectl scale deployment livin-matrix-backend --replicas=1 -n livin-matrix

# 验证服务健康状态
echo "Verifying service health..."
kubectl wait --for=condition=available --timeout=300s deployment/livin-matrix-backend -n livin-matrix

# 清理临时文件
rm -rf "${TEMP_DIR}"

echo "Disaster recovery completed successfully!"
```

### 7.8 成本优化和资源管理

**资源请求和限制策略：**
```yaml
# k8s/resource-quotas.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: livin-matrix-quota
  namespace: livin-matrix
spec:
  hard:
    requests.cpu: "1000m"      # 1 CPU core
    requests.memory: "2Gi"     # 2GB RAM
    limits.cpu: "2000m"        # 2 CPU cores max
    limits.memory: "4Gi"       # 4GB RAM max
    persistentvolumeclaims: "5"
    services: "10"
    secrets: "10"
    configmaps: "10"

---
apiVersion: v1
kind: LimitRange
metadata:
  name: livin-matrix-limits
  namespace: livin-matrix
spec:
  limits:
  - default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
  - max:
      cpu: "1000m"
      memory: "1Gi"
    min:
      cpu: "50m"
      memory: "64Mi"
    type: Container
```

**成本监控和告警：**
```bash
#!/bin/bash
# scripts/cost-monitor.sh

# AWS成本分析脚本
CURRENT_MONTH=$(date +"%Y-%m")
LAST_MONTH=$(date -d "last month" +"%Y-%m")

echo "=== AWS Free Tier Usage Report ==="
echo "Report Date: $(date)"
echo "Current Month: ${CURRENT_MONTH}"

# EC2使用情况
echo -e "\n--- EC2 Usage ---"
aws ce get-usage-and-costs \
  --time-period Start="${CURRENT_MONTH}-01",End="${CURRENT_MONTH}-31" \
  --granularity MONTHLY \
  --metrics BlendedCost,UsageQuantity \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter file://cost-filter.json

# RDS使用情况
echo -e "\n--- RDS Usage ---"
aws rds describe-db-instances \
  --query 'DBInstances[?DBInstanceStatus==`available`].[DBInstanceIdentifier,DBInstanceClass,AllocatedStorage,DBInstanceStatus]' \
  --output table

# S3使用情况
echo -e "\n--- S3 Usage ---"
aws s3 ls --summarize --human-readable --recursive s3://livin-matrix-uploads-*/

# CloudWatch日志使用情况
echo -e "\n--- CloudWatch Logs Usage ---"
aws logs describe-log-groups \
  --query 'logGroups[?starts_with(logGroupName, `/aws/eks/livin-matrix`)].[logGroupName,storedBytes]' \
  --output table

# 告警检查
CURRENT_COST=$(aws ce get-usage-and-costs \
  --time-period Start="${CURRENT_MONTH}-01",End="$(date +%Y-%m-%d)" \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
  --output text)

if (( $(echo "${CURRENT_COST} > 5.00" | bc -l) )); then
  echo "WARNING: Current month cost (${CURRENT_COST}) exceeds $5.00 threshold!"
  # 发送告警通知
  curl -X POST "${SLACK_WEBHOOK_URL}" \
    -H 'Content-type: application/json' \
    --data '{"text":"🚨 AWS Cost Alert: Monthly spend exceeds $5.00 - Current: $'${CURRENT_COST}'"}'
fi

echo -e "\n=== Report Complete ==="
```

继续下一部分的选择，我将提供以下方向：

## 请选择继续的方向：

**1. 完成架构文档其余部分** - 继续完善系统设计：
   - 安全架构和数据保护策略
   - 性能优化和扩展性设计
   - API文档规范和错误处理
   - 系统可观测性完整方案

**2. 开始技术实现准备** - 转向具体开发阶段：
   - 项目脚手架搭建和初始化
   - 开发环境配置和Docker设置
   - 数据库初始化和种子数据
   - 前后端基础框架搭建

**3. 深入基础设施实施** - 专注部署和运维：
   - Terraform脚本完整实现
   - K3s集群详细配置和测试
   - CI/CD流水线调试和优化
   - 监控告警系统完整部署

**4. 开始前端架构设计** - 转向用户界面：
   - React组件架构设计
   - 状态管理和数据流设计
   - 响应式设计和用户体验
   - 前端性能优化策略

请选择您希望继续的方向，我将据此完善项目的架构设计文档。

## 8. 安全和性能考虑 (Security and Performance Considerations)

### 8.1 数据保护策略 (Data Protection Strategy)

#### 8.1.1 数据加密
```yaml
# 加密层级配置
encryption_layers:
  at_rest:
    database:
      engine: "AES-256-GCM"
      key_management: "AWS KMS / HashiCorp Vault"
      rotation_policy: "90天自动轮转"
    
    file_storage:
      algorithm: "AES-256-CBC"
      block_cipher: "PKCS7填充"
      metadata_encryption: true
    
    backup:
      compression: "启用压缩后加密"
      incremental: "差量加密存储"
      
  in_transit:
    api_communication:
      protocol: "TLS 1.3"
      cipher_suites: ["ECDHE-RSA-AES256-GCM-SHA384"]
      hsts_enabled: true
      
    database_connections:
      ssl_mode: "require"
      cert_verification: "full"
      connection_timeout: "30s"
      
    internal_services:
      mutual_tls: true
      service_mesh: "Istio with auto-mTLS"
```

#### 8.1.2 敏感数据处理
```typescript
// 数据脱敏和分类策略
interface DataClassification {
  pii_fields: {
    email: 'hash_mask';      // test***@example.com
    phone: 'partial_mask';   // 135****8888
    id_card: 'full_mask';    // ************
  };
  
  financial_data: {
    encryption_level: 'high';
    audit_required: true;
    retention_policy: '7年';
  };
  
  behavioral_data: {
    anonymization: 'k_anonymity_5';
    aggregation_only: true;
    real_time_deletion: true;
  };
}

// 数据访问控制矩阵
const dataAccessMatrix = {
  user_profile: {
    self: ['read', 'update'],
    admin: ['read', 'update', 'delete'],
    system: ['read', 'create'],
  },
  
  financial_records: {
    owner: ['read'],
    auditor: ['read', 'export'],
    admin: ['read', 'audit_log'],
  },
  
  system_logs: {
    developer: ['read', 'query'],
    ops: ['read', 'query', 'alert'],
    security: ['full_access'],
  }
};
```

### 8.2 访问控制架构 (Access Control Architecture)

#### 8.2.1 身份认证系统
```yaml
# 多因素认证配置
authentication_system:
  primary_auth:
    methods: ["password", "biometric", "social_oauth"]
    password_policy:
      min_length: 12
      complexity: "大小写+数字+特殊字符"
      history_check: 12  # 不能重复最近12个密码
      
  multi_factor:
    required_for: ["admin", "financial_operations", "data_export"]
    options:
      - totp_authenticator    # Google Authenticator
      - sms_verification     # 短信验证码
      - hardware_token      # YubiKey
      - biometric_scan      # 指纹/面部识别
      
  session_management:
    jwt_config:
      algorithm: "RS256"
      expiry: "15m"        # Access token过期时间
      refresh_expiry: "30d" # Refresh token过期时间
      
    security_features:
      concurrent_sessions: 3   # 最大并发会话数
      ip_binding: true        # 绑定IP地址
      device_fingerprint: true # 设备指纹验证
```

#### 8.2.2 权限管理系统 (RBAC + ABAC)
```typescript
// 基于角色和属性的访问控制
interface AccessControlSystem {
  roles: {
    super_admin: {
      permissions: ['*'];
      constraints: {
        ip_whitelist: boolean;
        time_restrictions: string[];
        approval_required: string[];
      };
    };
    
    business_admin: {
      permissions: [
        'user:read', 'user:update', 'user:suspend',
        'report:read', 'report:export',
        'config:read', 'config:update'
      ];
      resource_scope: 'organization';
    };
    
    analyst: {
      permissions: [
        'dashboard:read', 'report:read',
        'data:query', 'export:limited'
      ];
      data_filters: ['anonymized_only'];
    };
  };
  
  attribute_policies: {
    data_access: {
      conditions: [
        'user.department == resource.department',
        'user.clearance_level >= resource.sensitivity',
        'current_time within business_hours OR user.role == emergency_responder'
      ];
    };
    
    geographic_restrictions: {
      allowed_countries: ['CN', 'US', 'UK'];
      blocked_ips: ['tor_exit_nodes', 'known_malicious'];
    };
  };
}
```

### 8.3 威胁防护机制 (Threat Protection)

#### 8.3.1 API安全防护
```yaml
# API Gateway安全配置
api_security:
  rate_limiting:
    global_limit: "1000 req/min per IP"
    user_limit: "100 req/min per user"
    endpoint_specific:
      "/api/auth/login": "5 req/min"
      "/api/sensitive-data": "10 req/min"
      
  request_validation:
    input_sanitization: true
    sql_injection_detection: true
    xss_prevention: true
    schema_validation: "OpenAPI 3.0 strict mode"
    
  security_headers:
    csp: "default-src 'self'; script-src 'self' 'unsafe-inline'"
    hsts: "max-age=63072000; includeSubDomains; preload"
    x_frame_options: "DENY"
    x_content_type_options: "nosniff"
    
  monitoring:
    suspicious_patterns:
      - "异常高频请求"
      - "SQL注入尝试模式"
      - "暴力破解登录"
      - "数据导出异常"
```

#### 8.3.2 实时安全监控
```typescript
// 安全事件检测系统
interface SecurityMonitoring {
  threat_detection: {
    ml_models: {
      anomaly_detection: {
        baseline_learning: '7天';
        sensitivity: 'medium';
        alert_threshold: 0.85;
      };
      
      behavior_analysis: {
        user_profiling: true;
        access_pattern: true;
        geographical_anomaly: true;
      };
    };
    
    rule_based: {
      failed_login_attempts: {
        threshold: 5;
        time_window: '5分钟';
        action: 'account_lock + alert';
      };
      
      privilege_escalation: {
        detect: 'role_change + permission_increase';
        immediate_alert: true;
        auto_review: true;
      };
    };
  };
  
  incident_response: {
    severity_levels: {
      critical: {
        response_time: '5分钟';
        escalation: ['security_team', 'management'];
        auto_actions: ['isolate_account', 'snapshot_logs'];
      };
      
      high: {
        response_time: '15分钟';
        investigation: 'mandatory';
        notification: ['security_team'];
      };
    };
    
    forensic_data: {
      retention: '2年';
      immutable_logs: true;
      chain_of_custody: true;
    };
  };
}
```

### 8.4 性能监控和优化 (Performance Monitoring & Optimization)

#### 8.4.1 应用性能监控 (APM)
```yaml
# 性能监控配置
performance_monitoring:
  application_metrics:
    response_time:
      targets:
        api_endpoints: "< 200ms (P95)"
        database_queries: "< 100ms (P95)"
        page_load: "< 2s (P95)"
        
    throughput:
      current_capacity: "1000 req/s"
      target_capacity: "5000 req/s"
      scaling_trigger: "70% capacity"
      
    error_rates:
      acceptable: "< 0.1%"
      alert_threshold: "0.5%"
      critical_threshold: "1%"
      
  infrastructure_metrics:
    cpu_utilization:
      normal: "< 60%"
      scaling_threshold: "75%"
      alert_threshold: "85%"
      
    memory_usage:
      application_heap: "< 80%"
      system_memory: "< 85%"
      leak_detection: true
      
    disk_io:
      iops_monitoring: true
      latency_tracking: true
      space_utilization: "< 80%"
      
  custom_metrics:
    business_kpis:
      user_engagement: "日活跃用户数"
      conversion_rate: "关键业务转化率"
      revenue_impact: "性能对收入影响"
```

#### 8.4.2 性能优化策略
```typescript
// 多层缓存架构
interface CachingStrategy {
  client_side: {
    browser_cache: {
      static_assets: '30天';
      api_responses: '5分钟';
      user_preferences: '1天';
    };
    
    service_worker: {
      offline_support: true;
      background_sync: true;
      push_notifications: true;
    };
  };
  
  server_side: {
    redis_layers: {
      l1_cache: {
        type: 'Redis Cluster';
        ttl: '1小时';
        use_cases: ['session', 'frequent_queries'];
      };
      
      l2_cache: {
        type: 'Redis Persistent';
        ttl: '24小时';
        use_cases: ['computed_results', 'aggregations'];
      };
    };
    
    cdn_strategy: {
      global_distribution: 'Cloudflare';
      edge_caching: '全球15个节点';
      dynamic_content: 'ESI边缘包含';
    };
  };
  
  database_optimization: {
    query_optimization: {
      index_strategy: 'B-tree + partial indexes';
      query_plan_analysis: true;
      slow_query_monitoring: '> 100ms';
    };
    
    connection_pooling: {
      pool_size: '20-100 connections';
      idle_timeout: '10分钟';
      health_checks: '每30秒';
    };
  };
}
```

### 8.5 扩展性设计 (Scalability Design)

#### 8.5.1 水平扩展策略
```yaml
# 微服务扩展配置
scaling_architecture:
  service_scaling:
    auto_scaling_rules:
      cpu_threshold: 70%
      memory_threshold: 80%
      request_queue_depth: 100
      custom_metrics: ["business_load", "db_connections"]
      
    scaling_policies:
      scale_out:
        min_instances: 2
        max_instances: 50
        step_scaling: "2个实例递增"
        cooldown: "5分钟"
        
      scale_in:
        min_instances: 2
        step_scaling: "1个实例递减"
        cooldown: "10分钟"
        
  database_scaling:
    read_replicas:
      auto_scaling: true
      max_replicas: 5
      lag_threshold: "100ms"
      
    sharding_strategy:
      shard_key: "user_id"
      shard_count: 16
      rebalancing: "automatic"
      
    caching_layers:
      distributed: "Redis Cluster"
      local: "Application-level cache"
      
  load_balancing:
    algorithms:
      api_gateway: "least_connections"
      database: "weighted_round_robin"
      static_content: "geographical_proximity"
      
    health_checks:
      interval: "10秒"
      timeout: "5秒"
      unhealthy_threshold: 3
```

#### 8.5.2 异步处理架构
```typescript
// 消息队列和异步处理
interface AsyncProcessingArchitecture {
  message_queues: {
    high_priority: {
      type: 'Redis Streams';
      use_cases: ['real_time_notifications', 'payment_processing'];
      reliability: 'at_least_once';
      max_retries: 3;
    };
    
    batch_processing: {
      type: 'Apache Kafka';
      use_cases: ['data_analytics', 'report_generation'];
      partitioning: 'by_user_id';
      retention: '7天';
    };
    
    scheduled_tasks: {
      type: 'Kubernetes CronJobs';
      use_cases: ['backup', 'cleanup', 'reports'];
      monitoring: 'Prometheus + Grafana';
    };
  };
  
  event_driven_architecture: {
    event_bus: {
      technology: 'Apache Kafka';
      topics: [
        'user.events',
        'financial.transactions',
        'system.monitoring'
      ];
    };
    
    event_sourcing: {
      critical_domains: ['user_authentication', 'financial_operations'];
      snapshot_frequency: '每1000个事件';
      replay_capability: true;
    };
  };
  
  circuit_breaker_pattern: {
    failure_threshold: 5;
    timeout: '30秒';
    retry_policy: 'exponential_backoff';
    fallback_strategies: ['cached_response', 'degraded_service'];
  };
}
```

### 8.6 运维和可观测性 (Operations & Observability)

#### 8.6.1 日志管理策略
```yaml
# 统一日志架构
logging_architecture:
  log_levels:
    application:
      production: "INFO"
      staging: "DEBUG"
      development: "TRACE"
      
  structured_logging:
    format: "JSON"
    fields:
      mandatory: ["timestamp", "level", "service", "trace_id"]
      optional: ["user_id", "session_id", "request_id"]
      
  log_aggregation:
    collector: "Fluentd"
    storage: "Elasticsearch"
    retention:
      error_logs: "90天"
      access_logs: "30天"
      debug_logs: "7天"
      
  log_analysis:
    real_time: "Kibana Dashboard"
    alerting: "ElastAlert"
    anomaly_detection: "Machine Learning模块"
    
  compliance:
    sensitive_data: "自动脱敏"
    audit_trail: "不可变存储"
    legal_hold: "法律要求数据保留"
```

#### 8.6.2 监控告警系统
```typescript
// 全栈监控配置
interface MonitoringConfiguration {
  metrics_collection: {
    application_metrics: {
      business_metrics: [
        'user_registration_rate',
        'transaction_success_rate',
        'feature_adoption_rate'
      ];
      
      technical_metrics: [
        'response_time_percentiles',
        'error_rate_by_endpoint',
        'database_connection_pool'
      ];
    };
    
    infrastructure_metrics: {
      system_resources: ['cpu', 'memory', 'disk', 'network'];
      kubernetes_metrics: ['pod_status', 'resource_usage', 'hpa_metrics'];
      database_metrics: ['query_performance', 'replication_lag', 'connections'];
    };
  };
  
  alerting_rules: {
    severity_levels: {
      p1_critical: {
        conditions: [
          'service_unavailable > 5分钟',
          'error_rate > 5%',
          'data_loss_detected'
        ];
        notification: ['pager', 'sms', 'phone_call'];
        response_sla: '15分钟';
      };
      
      p2_high: {
        conditions: [
          'response_time > 2秒 (P95)',
          'disk_usage > 90%',
          'unusual_traffic_pattern'
        ];
        notification: ['slack', 'email'];
        response_sla: '1小时';
      };
    };
    
    escalation_policies: {
      primary_oncall: '立即通知';
      secondary_oncall: '30分钟后升级';
      management: '2小时后升级';
    };
  };
  
  dashboards: {
    executive_summary: {
      metrics: ['system_health', 'business_kpis', 'cost_optimization'];
      update_frequency: '实时';
    };
    
    operations_dashboard: {
      metrics: ['service_status', 'performance_trends', 'capacity_planning'];
      drill_down: true;
    };
    
    developer_dashboard: {
      metrics: ['deployment_status', 'error_tracking', 'performance_profiling'];
      integration: 'IDE插件支持';
    };
  };
}
```

### 8.7 灾难恢复和业务连续性 (Disaster Recovery & Business Continuity)

#### 8.7.1 备份策略
```yaml
# 多层备份架构
backup_strategy:
  database_backups:
    full_backup:
      frequency: "每日凌晨2点"
      retention: "30天本地 + 90天云端"
      verification: "自动恢复测试"
      
    incremental_backup:
      frequency: "每6小时"
      retention: "7天"
      compression: "启用"
      
    transaction_log_backup:
      frequency: "每15分钟"
      retention: "24小时"
      
  application_data:
    file_system:
      frequency: "每日"
      method: "增量备份"
      storage: "AWS S3 多区域复制"
      
    configuration:
      frequency: "配置变更时"
      versioning: "Git版本控制"
      immutable: "不可变基础设施"
      
  cross_region_replication:
    primary_region: "上海"
    backup_regions: ["北京", "深圳"]
    replication_lag: "< 5分钟"
    failover_time: "< 30分钟"
```

#### 8.7.2 故障恢复计划
```typescript
// 灾难恢复流程
interface DisasterRecoveryPlan {
  rto_rpo_targets: {
    critical_services: {
      rto: '15分钟';  // 恢复时间目标
      rpo: '5分钟';   // 恢复点目标
      priority: 1;
    };
    
    important_services: {
      rto: '1小时';
      rpo: '30分钟';
      priority: 2;
    };
    
    standard_services: {
      rto: '4小时';
      rpo: '2小时';
      priority: 3;
    };
  };
  
  failure_scenarios: {
    single_server_failure: {
      detection: '自动健康检查';
      response: '自动故障转移';
      recovery_time: '< 5分钟';
    };
    
    database_failure: {
      detection: '连接监控 + 复制延迟';
      response: '主从切换';
      recovery_time: '< 15分钟';
    };
    
    region_outage: {
      detection: '跨区域监控';
      response: '流量重路由';
      recovery_time: '< 30分钟';
    };
    
    complete_disaster: {
      detection: '人工确认';
      response: '完整环境重建';
      recovery_time: '< 24小时';
    };
  };
  
  testing_schedule: {
    failover_testing: '每季度';
    backup_restoration: '每月';
    full_dr_drill: '每半年';
    documentation_review: '每月';
  };
}
```

### 8.8 合规性和审计 (Compliance & Audit)

#### 8.8.1 数据合规框架
```yaml
# 数据保护合规配置
compliance_framework:
  gdpr_compliance:
    data_subject_rights:
      - "数据访问权 (Right to Access)"
      - "数据更正权 (Right to Rectification)"
      - "数据删除权 (Right to Erasure)"
      - "数据可携权 (Right to Portability)"
      
    privacy_by_design:
      data_minimization: true
      purpose_limitation: true
      storage_limitation: true
      transparency: "隐私政策明确说明"
      
  cybersecurity_law_china:
    data_localization:
      personal_info: "境内存储"
      important_data: "境内处理"
      cross_border_transfer: "评估和申报"
      
    network_security:
      level_protection: "等保2.0三级"
      security_assessment: "年度评估"
      incident_reporting: "24小时内上报"
      
  industry_standards:
    iso27001:
      information_security_management: true
      risk_assessment: "年度更新"
      continuous_improvement: true
      
    soc2_type2:
      security: "访问控制和加密"
      availability: "系统可用性监控"
      processing_integrity: "数据处理完整性"
      confidentiality: "敏感信息保护"
```

#### 8.8.2 审计追踪系统
```typescript
// 审计日志架构
interface AuditTrailSystem {
  audit_events: {
    user_actions: {
      authentication: ['login', 'logout', 'failed_attempts'];
      data_access: ['view', 'download', 'export'];
      data_modification: ['create', 'update', 'delete'];
      privilege_changes: ['role_assignment', 'permission_grant'];
    };
    
    system_events: {
      configuration_changes: ['system_settings', 'security_policies'];
      infrastructure: ['deployments', 'scaling_events'];
      security_incidents: ['breach_attempts', 'anomaly_detection'];
    };
  };
  
  audit_log_format: {
    mandatory_fields: [
      'timestamp',
      'user_id',
      'session_id', 
      'action_type',
      'resource_affected',
      'ip_address',
      'user_agent',
      'result'
    ];
    
    optional_fields: [
      'geolocation',
      'device_fingerprint',
      'business_context',
      'data_classification'
    ];
  };
  
  retention_policies: {
    financial_transactions: '7年';
    user_access_logs: '3年';
    system_operations: '1年';
    security_events: '5年';
  };
  
  audit_reporting: {
    compliance_reports: {
      frequency: '季度';
      automated_generation: true;
      management_review: true;
    };
    
    security_dashboard: {
      real_time_monitoring: true;
      anomaly_alerts: true;
      trend_analysis: true;
    };
  };
}
```

### 8.9 成本优化策略 (Cost Optimization)

#### 8.9.1 云资源优化
```yaml
# 成本管理配置
cost_optimization:
  resource_rightsizing:
    auto_scaling:
      cpu_utilization_target: "70%"
      memory_utilization_target: "80%"
      scale_down_aggressively: true
      
    instance_optimization:
      reserved_instances: "稳定工作负载"
      spot_instances: "批处理任务"
      burstable_instances: "开发测试环境"
      
  storage_optimization:
    data_lifecycle:
      hot_storage: "30天内访问"
      warm_storage: "30-90天"
      cold_storage: "90天以上"
      archive_storage: "法规要求长期保存"
      
    compression_and_deduplication:
      database: "启用压缩"
      backups: "重复数据删除"
      logs: "自动压缩"
      
  network_optimization:
    cdn_usage: "静态资源全部CDN"
    data_transfer_optimization: "区域内传输优先"
    compression: "API响应压缩"
    
  monitoring_and_alerting:
    cost_anomaly_detection: true
    budget_alerts:
      - "月预算50%时警告"
      - "月预算80%时告警"
      - "月预算100%时限制"
    
    cost_attribution:
      by_service: true
      by_environment: true
      by_team: true
```

#### 8.9.2 性能与成本平衡
```typescript
// 性能成本优化策略
interface PerformanceCostBalance {
  tiered_service_levels: {
    premium_tier: {
      sla: '99.99% 可用性';
      performance: 'P95 < 100ms';
      cost_multiplier: 3;
      target_users: 'enterprise_customers';
    };
    
    standard_tier: {
      sla: '99.9% 可用性';
      performance: 'P95 < 500ms';
      cost_multiplier: 1;
      target_users: 'regular_users';
    };
    
    basic_tier: {
      sla: '99.5% 可用性';
      performance: 'P95 < 2s';
      cost_multiplier: 0.3;
      target_users: 'free_tier_users';
    };
  };
  
  intelligent_scaling: {
    predictive_scaling: {
      ml_model: 'based_on_historical_patterns';
      forecast_horizon: '24小时';
      accuracy_target: '85%';
    };
    
    cost_aware_scaling: {
      prefer_horizontal: 'when_cost_effective';
      prefer_vertical: 'for_performance_critical';
      spot_instance_integration: true;
    };
  };
  
  feature_flags_for_cost_control: {
    expensive_features: {
      real_time_analytics: 'premium_users_only';
      advanced_reporting: 'paid_tier_only';
      ai_recommendations: 'usage_based_billing';
    };
    
    graceful_degradation: {
      under_high_load: 'disable_non_critical_features';
      during_peak_hours: 'reduce_refresh_rates';
      cost_threshold_exceeded: 'limit_concurrent_users';
    };
  };
}
```

---

## 总结与后续建议 (Summary & Next Steps)

### 架构文档完成情况
本详细架构文档涵盖了LiVin Matrix项目的以下关键方面：

1. **系统概览和架构原则** - 建立了清晰的技术愿景和设计原则
2. **技术栈决策** - 详细说明了前后端、数据库和基础设施的技术选择
3. **后端架构设计** - 微服务架构、API设计和数据处理流程
4. **前端架构设计** - React组件体系、状态管理和用户体验设计
5. **数据架构和API接口** - 数据模型、接口规范和集成策略
6. **部署架构和基础设施** - K3s集群、CI/CD流水线和运维自动化
7. **安全和性能考虑** - 数据保护、威胁防护、性能优化和合规框架

### 关键技术亮点
- **现代化技术栈**: Node.js + React + PostgreSQL + Redis
- **云原生架构**: Kubernetes + 微服务 + 容器化部署
- **全面安全体系**: 多层加密 + 访问控制 + 威胁检测
- **高性能设计**: 多级缓存 + 异步处理 + 智能扩展
- **运维自动化**: GitOps + 监控告警 + 灾难恢复

### 项目继续方向建议

## 请选择继续的方向：

**1. 开始技术实现阶段** - 转向具体开发：
   - 创建项目脚手架和开发环境配置
   - 实现核心业务逻辑和API接口
   - 构建前端组件库和页面结构
   - 集成第三方服务和中间件

**2. 深入基础设施实施** - 专注部署和运维：
   - 编写完整的Terraform基础设施代码
   - 配置和调试K3s集群环境
   - 实现CI/CD流水线和自动化部署
   - 部署监控、日志和告警系统

**3. 安全合规深化实施** - 强化安全框架：
   - 实现详细的身份认证和授权系统
   - 部署安全监控和威胁检测机制
   - 建立数据保护和合规审计流程
   - 进行安全测试和渗透测试

**4. 性能优化和压力测试** - 验证系统性能：
   - 设计和执行负载测试方案
   - 优化数据库查询和缓存策略
   - 实施前端性能优化和CDN配置
   - 建立性能监控和自动调优机制

选择您希望继续的方向，我将据此开始详细的技术实施工作。