# ADR-005: 环境配置分离架构

## 状态
已接受 (2025-08-13)

## 背景
在实施Epic 1.5.10最小化端到端部署时，发现现有的配置管理存在以下问题：

1. **环境混淆**：本地开发和生产环境使用相同的配置文件，导致GitHub OAuth回调URL等配置冲突
2. **部署复杂性**：需要手动修改配置文件来适配不同环境
3. **维护困难**：单一配置文件难以管理多环境差异
4. **错误风险**：容易在错误环境使用错误配置

### 具体问题案例
- 前端API配置指向 `localhost:8000`，在AWS环境无法访问
- GitHub OAuth回调URL固定为 `localhost:3000/auth/callback`，AWS环境无法回调
- 生产环境使用开发环境的CORS配置

## 决策
采用**Docker Compose多文件分层配置**架构，实现环境配置分离：

### 文件结构
```
├── docker-compose.yml           # 基础配置（共同部分）
├── docker-compose.local.yml     # 本地开发环境覆盖
├── docker-compose.production.yml # 生产环境覆盖
└── secrets/                     # 密钥文件（支持环境特定版本）
    ├── GITHUB_REDIRECT_URI              # 本地开发回调URL
    └── GITHUB_REDIRECT_URI_PRODUCTION   # 生产环境回调URL
```

### 使用方式
**本地开发：**
```bash
# 直接命令
docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d

# 统一脚本
./scripts/services/start-all.command
```

**生产环境：**
```bash
# 直接命令
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

# 统一脚本
DEPLOYMENT_ENV=production ./scripts/services/start-all.command
```

### 配置差异管理
| 配置项 | 本地开发 | 生产环境 |
|--------|----------|----------|
| API地址 | localhost:8000 | 34.195.202.97:8000 |
| 前端地址 | localhost:3000 | 34.195.202.97:3000 |
| GitHub回调URL | localhost:3000/auth/callback | 34.195.202.97:3000/auth/callback |
| 密钥管理方式 | 环境变量 | Docker Secrets (/var/secrets) |
| 环境标识 | development | production |
| 调试模式 | DEBUG=true | DEBUG=false |
| CORS配置 | 本地地址 | AWS实例地址 |

## 后果

### 积极影响
✅ **环境隔离**：完全分离开发和生产配置，避免混淆
✅ **部署简化**：通过环境变量自动选择正确配置
✅ **维护性**：清晰的配置分层，易于理解和修改
✅ **安全性**：生产环境使用Docker Secrets，开发环境使用环境变量
✅ **一致性**：标准化的启动流程，减少人为错误

### 消极影响
⚠️ **文件增加**：需要维护额外的配置文件
⚠️ **学习成本**：团队需要了解新的部署方式
⚠️ **同步复杂性**：配置变更需要考虑多个文件

### 风险缓解
- 通过统一脚本隐藏复杂性
- 在文档中明确说明使用方式
- 配置文件模板化，减少重复

## 替代方案

### 方案A：环境变量注入
通过部署时注入不同环境变量来区分环境。
- ❌ 缺点：需要外部工具管理，配置分散

### 方案B：单配置文件+条件逻辑
在配置文件中使用条件判断来处理环境差异。
- ❌ 缺点：配置文件复杂，难以维护

### 方案C：完全独立的项目副本
为每个环境维护独立的代码副本。
- ❌ 缺点：代码重复，维护负担重

## 实施细节

### 代码变更
1. **backend/app/core/config.py**：添加环境感知的GitHub OAuth配置
2. **scripts/services/start-all.command**：支持DEPLOYMENT_ENV环境变量
3. **新增配置文件**：docker-compose.local.yml, docker-compose.production.yml

### 部署流程更新
1. **本地开发**：无需更改，默认使用本地配置
2. **AWS生产**：设置 `DEPLOYMENT_ENV=production` 后使用统一脚本

### 向后兼容性
- 保留原有 docker-compose.secrets.yml 作为生产配置模板
- 统一脚本默认使用本地配置，保持现有工作流

## 相关文档
- [Epic 1.5.10: 最小化端到端应用部署](../stories/epic1.5/1.5.10.minimal-end-to-end-deployment.md)
- [部署架构文档](../planning/deployment-architecture.md)
- [Docker Secrets管理](../stories/epic1.5/1.5.4.1.docker-secrets-management.md)

## 验证标准
- ✅ 本地开发环境正常启动和运行
- ✅ 生产环境正常启动和运行
- ✅ GitHub OAuth在两个环境都能正常工作
- ✅ API端点在两个环境都能正常访问
- ✅ 前后端通信在两个环境都正常

---
**决策者**: Dev Agent (James)
**日期**: 2025-08-13
**上下文**: Epic 1.5.10 端到端部署实施
