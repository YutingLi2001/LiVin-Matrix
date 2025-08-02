# GitHub OAuth + JWT 认证系统架构文档

## 项目概述

**项目名称**: LiVin Matrix  
**认证方案**: GitHub OAuth + 自制JWT认证系统  
**替代方案**: 从Auth0 ($35/月) 迁移到完全免费的GitHub OAuth解决方案  
**更新日期**: 2025-08-02  

## 高层架构

### 技术概要
- **前端**: React + TypeScript + Vite
- **后端**: FastAPI + Python 3.11 + SQLAlchemy  
- **数据库**: PostgreSQL
- **认证流程**: GitHub OAuth 2.0 → JWT Token → 数据库用户同步
- **部署**: Docker容器化 + 免费云服务

### 认证流程架构图

```mermaid
sequenceDiagram
    participant User as 用户
    participant Frontend as React前端
    participant Backend as FastAPI后端
    participant GitHub as GitHub OAuth
    participant DB as PostgreSQL数据库
    
    User->>Frontend: 点击"GitHub登录"
    Frontend->>GitHub: 重定向到GitHub OAuth
    GitHub->>User: 显示授权页面
    User->>GitHub: 确认授权
    GitHub->>Frontend: 重定向回调 + code
    Frontend->>Backend: POST /api/v1/auth/github/callback {code}
    Backend->>GitHub: 交换code获取access_token
    GitHub->>Backend: 返回access_token
    Backend->>GitHub: 获取用户信息
    GitHub->>Backend: 返回用户资料
    Backend->>DB: 创建/更新用户记录
    Backend->>Backend: 生成JWT token
    Backend->>Frontend: 返回JWT + 用户信息
    Frontend->>Frontend: 存储JWT到localStorage
    Frontend->>Backend: API调用携带JWT Bearer token
    Backend->>Backend: 验证JWT并提取用户信息
    Backend->>Frontend: 返回API响应
```

## 技术栈规范

| 类别 | 技术选择 | 版本 | 成本 | 说明 |
|------|----------|------|------|------|
| **前端框架** | React | 19.1.0 | 免费 | 主UI框架 |
| **前端构建** | Vite | 7.0.4 | 免费 | 开发服务器和构建工具 |
| **前端语言** | TypeScript | 5.8.3 | 免费 | 类型安全 |
| **后端框架** | FastAPI | 0.104.1 | 免费 | Python异步Web框架 |
| **后端语言** | Python | 3.11 | 免费 | 服务端语言 |
| **数据库** | PostgreSQL | 15 | 免费 | 主数据库 |
| **ORM** | SQLAlchemy | 2.0.23 | 免费 | Python ORM |
| **认证服务** | GitHub OAuth | API v4 | 免费 | OAuth提供商 |
| **JWT库** | python-jose | 3.3.0 | 免费 | JWT生成和验证 |
| **密码哈希** | passlib[bcrypt] | 1.7.4 | 免费 | 密码安全存储 |
| **HTTP客户端** | httpx | 0.25.2 | 免费 | 异步HTTP客户端 |
| **缓存** | Redis | 7-alpine | 免费 | Session和缓存存储 |
| **容器化** | Docker | latest | 免费 | 应用容器化 |

## 数据模型设计

### 用户数据模型

```typescript
// 前端TypeScript接口
interface User {
  id: number;
  github_user_id: number;
  github_username: string;
  email: string;
  name?: string;
  avatar_url?: string;
  bio?: string;
  location?: string;
  timezone: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
```

### 数据库Schema

```sql
-- 更新用户表以支持GitHub OAuth
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    github_user_id BIGINT UNIQUE NOT NULL,
    github_username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    bio TEXT,
    location VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引优化
    INDEX idx_users_github_id (github_user_id),
    INDEX idx_users_email (email),
    INDEX idx_users_username (github_username)
);

-- JWT令牌黑名单表（用于登出功能）
CREATE TABLE token_blacklist (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(255) UNIQUE NOT NULL, -- JWT ID
    user_id INTEGER NOT NULL REFERENCES users(id),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_blacklist_jti (jti),
    INDEX idx_blacklist_expires (expires_at)
);
```

## API规范

### 认证端点

```yaml
openapi: 3.0.0
info:
  title: LiVin Matrix Authentication API
  version: 1.0.0

paths:
  /api/v1/auth/github/login:
    get:
      summary: 获取GitHub OAuth授权URL
      responses:
        200:
          description: 成功返回授权URL
          content:
            application/json:
              schema:
                type: object
                properties:
                  auth_url:
                    type: string
                    example: "https://github.com/login/oauth/authorize?client_id=..."
                  state:
                    type: string
                    description: CSRF保护状态参数

  /api/v1/auth/github/callback:
    post:
      summary: GitHub OAuth回调处理
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                code:
                  type: string
                  description: GitHub授权码
                state:
                  type: string
                  description: CSRF保护状态参数
      responses:
        200:
          description: 登录成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                    description: JWT访问令牌
                  token_type:
                    type: string
                    example: "bearer"
                  expires_in:
                    type: integer
                    example: 86400
                  user:
                    $ref: '#/components/schemas/User'

  /api/v1/auth/refresh:
    post:
      summary: 刷新JWT令牌
      security:
        - BearerAuth: []
      responses:
        200:
          description: 令牌刷新成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  expires_in:
                    type: integer

  /api/v1/auth/logout:
    post:
      summary: 用户登出
      security:
        - BearerAuth: []
      responses:
        200:
          description: 登出成功

  /api/v1/auth/profile:
    get:
      summary: 获取当前用户信息
      security:
        - BearerAuth: []
      responses:
        200:
          description: 用户信息
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        github_user_id:
          type: integer
        github_username:
          type: string
        email:
          type: string
        name:
          type: string
          nullable: true
        avatar_url:
          type: string
          nullable: true
        timezone:
          type: string
        is_active:
          type: boolean
        created_at:
          type: string
          format: date-time
```

## 前端组件架构

### 组件层次结构

```
src/
├── components/
│   ├── auth/
│   │   ├── LoginButton.tsx           # GitHub登录按钮
│   │   ├── LogoutButton.tsx          # 登出按钮
│   │   ├── AuthCallback.tsx          # OAuth回调处理
│   │   └── ProtectedRoute.tsx        # 路由保护组件
│   └── layout/
│       ├── Header.tsx                # 导航栏（含用户菜单）
│       └── UserProfile.tsx           # 用户信息显示
├── contexts/
│   └── AuthContext.tsx               # 认证状态管理
├── hooks/
│   ├── useAuth.ts                    # 认证相关hooks
│   └── useApi.ts                     # API调用hooks
├── services/
│   ├── authService.ts                # 认证服务
│   └── apiClient.ts                  # HTTP客户端配置
├── types/
│   └── auth.ts                       # 认证相关类型定义
└── utils/
    ├── storage.ts                    # 本地存储工具
    └── tokenUtils.ts                 # JWT令牌工具
```

### 核心组件实现

```typescript
// src/contexts/AuthContext.tsx
interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

// src/services/authService.ts  
class AuthService {
  async getGithubAuthUrl(): Promise<{auth_url: string, state: string}>;
  async handleGithubCallback(code: string, state: string): Promise<AuthResponse>;
  async refreshToken(): Promise<AuthResponse>;
  async logout(): Promise<void>;
  async getCurrentUser(): Promise<User>;
}
```

## 后端服务架构

### 服务层组织

```
backend/app/
├── api/
│   └── api_v1/
│       └── endpoints/
│           └── auth.py               # 认证端点
├── core/
│   ├── auth.py                       # JWT认证中间件
│   ├── config.py                     # 配置管理
│   └── security.py                   # 安全工具函数
├── services/
│   ├── github_service.py             # GitHub OAuth服务
│   ├── jwt_service.py                # JWT令牌服务
│   └── user_service.py               # 用户管理服务
├── models/
│   └── user.py                       # 用户数据模型
└── schemas/
    └── auth.py                       # 认证相关Pydantic模型
```

### 核心服务实现

```python
# app/services/github_service.py
class GitHubOAuthService:
    async def get_auth_url(self) -> dict;
    async def exchange_code_for_token(self, code: str) -> str;
    async def get_user_info(self, access_token: str) -> dict;

# app/services/jwt_service.py  
class JWTService:
    def create_access_token(self, data: dict) -> str;
    def verify_token(self, token: str) -> dict;
    async def blacklist_token(self, jti: str, user_id: int) -> None;
    async def is_token_blacklisted(self, jti: str) -> bool;
```

## 环境配置

### 前端环境变量 (.env)

```bash
# GitHub OAuth配置
VITE_GITHUB_CLIENT_ID=your_github_client_id
VITE_GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback

# API配置  
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_ENVIRONMENT=development
```

### 后端环境变量 (.env)

```bash
# GitHub OAuth配置
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/api/v1/auth/github/callback

# JWT配置
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24小时

# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/livin_matrix_dev

# Redis配置 (用于令牌黑名单)
REDIS_URL=redis://localhost:6379/0
```

## 安全策略

### JWT令牌安全
- **算法**: HS256 (对称加密)
- **过期时间**: 24小时  
- **刷新机制**: 静默刷新
- **存储方式**: localStorage (开发环境) / httpOnly Cookie (生产环境)
- **黑名单机制**: Redis存储已撤销令牌

### OAuth安全
- **CSRF保护**: 使用state参数
- **PKCE**: 公共客户端使用代码交换验证
- **Scope限制**: 仅请求必要的权限 (`user:email`)

### API安全
- **CORS配置**: 限制允许的源
- **速率限制**: 防止暴力攻击
- **输入验证**: Pydantic模型验证
- **SQL注入防护**: SQLAlchemy ORM

## 测试策略

### 前端测试

```typescript
// 认证服务测试
describe('AuthService', () => {
  test('应该正确处理GitHub登录流程', async () => {
    // 模拟GitHub OAuth回调
    const mockCode = 'test_code';
    const mockState = 'test_state';
    
    const result = await authService.handleGithubCallback(mockCode, mockState);
    
    expect(result.access_token).toBeDefined();
    expect(result.user).toBeDefined();
  });
});

// AuthContext测试
describe('AuthContext', () => {
  test('应该正确管理认证状态', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    // 测试登录、登出状态变化
  });
});
```

### 后端测试

```python
# 认证API测试
@pytest.mark.asyncio
async def test_github_oauth_callback(test_client, mock_github_response):
    """测试GitHub OAuth回调处理"""
    response = await test_client.post(
        "/api/v1/auth/github/callback",
        json={"code": "test_code", "state": "test_state"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "user" in data

# JWT令牌测试
def test_jwt_token_verification():
    """测试JWT令牌生成和验证"""
    user_data = {"github_user_id": 123, "email": "test@example.com"}
    
    token = jwt_service.create_access_token(user_data)
    payload = jwt_service.verify_token(token)
    
    assert payload["github_user_id"] == 123
    assert payload["email"] == "test@example.com"
```

## 部署架构

### 开发环境
- **前端**: Vite开发服务器 (localhost:3000)
- **后端**: FastAPI + Uvicorn (localhost:8000)  
- **数据库**: Docker PostgreSQL (localhost:5432)
- **缓存**: Docker Redis (localhost:6379)

### 生产环境部署选项

| 服务 | 平台选择 | 免费额度 | 说明 |
|------|----------|----------|------|
| **前端** | GitHub Pages | 无限制 | 静态网站托管 |
| **后端** | Railway/Render | 500小时/月 | Python应用托管 |
| **数据库** | Neon/Supabase | 0.5GB存储 | PostgreSQL托管 |
| **Redis** | Redis Cloud | 30MB | Redis托管服务 |
| **监控** | Sentry | 5K错误/月 | 错误监控 |

## 迁移计划

### 从Auth0迁移步骤

1. **第一阶段 - 准备工作**
   - [ ] 创建GitHub OAuth应用
   - [ ] 设置新的环境变量
   - [ ] 更新数据库schema

2. **第二阶段 - 后端重构**  
   - [ ] 重写认证中间件 (`app/core/auth.py`)
   - [ ] 实现GitHub OAuth服务
   - [ ] 创建新的认证端点
   - [ ] 更新用户服务

3. **第三阶段 - 前端重构**
   - [ ] 移除Auth0依赖
   - [ ] 重写AuthContext
   - [ ] 更新登录/登出组件
   - [ ] 实现OAuth回调页面

4. **第四阶段 - 测试验证**
   - [ ] 单元测试
   - [ ] 集成测试  
   - [ ] 端到端测试
   - [ ] 性能测试

## 预期收益

- **成本节省**: $35/月 → $0/月
- **控制权**: 完全掌控认证流程
- **性能**: 减少第三方依赖延迟
- **学习价值**: 深入理解OAuth和JWT认证机制
- **扩展性**: 可根据需求自由扩展功能