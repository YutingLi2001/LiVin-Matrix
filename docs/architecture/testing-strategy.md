# 测试策略 (Testing Strategy)

## 测试框架

### 后端测试
- **测试框架**: pytest + pytest-asyncio
- **测试位置**: `backend/tests/`
- **测试覆盖率目标**: 80%以上
- **测试类型**:
  - 单元测试：模型、服务、API端点
  - 集成测试：数据库操作、认证流程
  - API测试：FastAPI TestClient

### 前端测试
- **测试框架**: Jest + React Testing Library
- **测试位置**: `frontend/src/__tests__/`
- **测试类型**:
  - 组件测试：React组件渲染和交互
  - 集成测试：用户流程和API集成
  - 快照测试：UI组件一致性

## 测试配置

### 数据库测试
- 使用测试数据库进行隔离测试
- 每个测试用例独立的数据库事务
- 测试数据清理策略

### 认证测试
- 模拟GitHub OAuth认证流程
- JWT token验证测试
- 权限和访问控制测试

## 测试标准

### 性能测试基准
- 单条记录插入 < 50ms
- 查询30天数据 < 200ms
- JWT验证时间 < 50ms
- 页面加载时间 < 3秒

### 安全测试
- API端点权限验证
- 数据访问隔离测试
- 输入验证和SQL注入防护测试

## 测试执行

### 本地开发
```bash
# 后端测试
cd backend && python -m pytest

# 前端测试
cd frontend && npm test

# 覆盖率报告
npm run test:coverage
```

### CI/CD集成
- 每次PR自动运行全部测试
- 测试失败时阻止合并
- 测试覆盖率报告生成
