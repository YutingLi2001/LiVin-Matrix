# LiVin Matrix 部署架构

## 核心哲学

### 自动化优先

从代码提交到生产部署的全流程自动化。三管道GitHub Actions设计确保每次变更都经过严格的质量门禁，降低人工干预和部署风险。

### 质量内建

80-20测试策略将98个测试精简到20个核心测试，在保障关键功能的前提下减少94%的维护负担。质量保障内建于CI/CD流水线，而非部署后的外部检查。

### 零成本可靠性

在AWS免费Tier约束下实现企业级部署可靠性。Docker Secrets、健康检查、自动回滚等企业级实践证明成本约束不等于质量妥协。

---

## CI/CD流水线设计

### 三管道架构

**Backend CI/CD Pipeline**
- **触发机制** — 后端代码变更时的独立验证和部署
- **质量门禁** — Black格式检查、Flake8代码质量、pytest并行测试
- **部署策略** — Docker镜像构建、烟雾测试、分阶段部署
- **执行时间** — 1分48秒高效完成

**Frontend CI/CD Pipeline**
- **触发机制** — 前端代码变更时的独立构建和部署
- **质量检查** — ESLint代码规范、Prettier格式统一、Jest测试覆盖
- **GitHub Pages** — 自动部署到生产环境
- **执行时间** — 2分12秒完成构建和部署

**Main CI/CD Pipeline**
- **智能触发** — 路径检测和集成验证，支持手动触发
- **并行执行** — 前后端测试并行运行，提升效率
- **集成验证** — 端到端健康检查和完整性验证
- **状态汇总** — 部署状态和性能指标的全面报告

### 自动化测试集成

**80-20测试策略实施成果**
- **测试用例精简** — 从98个减少到20个核心测试（后端12个 + 前端8个）
- **执行效率** — 总测试时间2.06秒，相比原来提升95%+
- **维护负担** — 代码量从1903行减少到110行，减少94%

**测试分级保障**
- **P0级别** — 系统生死线：健康检查、OAuth登录、应用启动
- **P1级别** — 主要业务：路由保护、用户档案、API结构
- **P2级别** — 边界保护：错误处理、CORS配置、环境管理

---

## 多环境部署策略

### Docker容器化部署

**服务架构组成**
- **数据层** — PostgreSQL 15 + Redis缓存
- **应用层** — FastAPI后端服务
- **前端层** — React SPA + Nginx代理
- **网络层** — 专用bridge网络隔离

**环境一致性保障**
- **配置分层** — 基础配置 + 环境特定配置的组合模式
- **依赖管理** — 统一的依赖版本和启动顺序
- **健康检查** — 全服务健康监控和自动恢复

### 配置管理策略

**多环境配置分离架构** (ADR-005)
- **基础配置** — docker-compose.yml（共同组件定义）
- **本地开发** — docker-compose.local.yml（开发环境覆盖）
- **生产环境** — docker-compose.production.yml（生产环境覆盖）
- **统一启动** — 环境变量DEPLOYMENT_ENV自动选择配置

**Docker Secrets集成**
- **生产环境** — Docker Secrets挂载到/var/secrets，企业级密钥管理
- **开发环境** — 标准环境变量，零配置启动
- **密钥安全** — 完全移除.env明文存储，权限600保护
- **核心密钥** — GitHub OAuth、JWT、PostgreSQL、Session统一管理

**环境特定配置差异**
| 配置项 | 本地开发 | 生产环境 |
|--------|----------|----------|
| API地址 | localhost:8000 | 34.195.202.97:8000 |
| 前端地址 | localhost:3000 | 34.195.202.97:3000 |
| GitHub回调URL | localhost:3000/auth/callback | 34.195.202.97:3000/auth/callback |
| 密钥管理 | 环境变量 | Docker Secrets |
| 环境标识 | development | production |
| 调试模式 | DEBUG=true | DEBUG=false |

**部署命令标准化**
```bash
# 本地开发环境
./scripts/services/start-all.command
# 或
docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d

# 生产环境
DEPLOYMENT_ENV=production ./scripts/services/start-all.command
# 或
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
```

---

**部署架构实现了零成本约束下的企业级DevOps实践，通过自动化、质量内建和安全配置管理，确保LiVin Matrix的可靠部署和持续交付。**
