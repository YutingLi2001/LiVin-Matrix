# CI/CD 流水线操作指南

## 概述

本项目使用 GitHub Actions 实现完整的 CI/CD 流水线，支持前后端代码的自动测试、构建、部署和回滚。

## 流水线架构

### 前端流水线 (Frontend CI/CD)

```
代码提交 → 测试 → 构建 → 部署到 GitHub Pages
    ↓        ↓      ↓           ↓
  Checkout  Jest   Docker   GitHub Pages部署
   代码    测试    镜像       静态网站托管
          ESLint  构建
         覆盖率
```

### 后端流水线 (Backend CI/CD)

```
代码提交 → 测试 → 构建 → 部署到 Staging → 验证
    ↓        ↓      ↓        ↓           ↓
  Checkout  pytest Docker  K3s部署    健康检查
   代码     测试   镜像    滚动更新     烟雾测试
          Black   构建
          Flake8
         覆盖率
```

## 触发条件

### 自动触发

1. **Push到main分支**: 触发完整的CI/CD流程
2. **Pull Request**: 只执行测试和构建，不部署
3. **路径过滤**:
   - 前端变更 (`frontend/**`) 只触发前端流水线
   - 后端变更 (`backend/**`) 只触发后端流水线

### 手动触发

在 GitHub Actions 页面可以手动触发工作流。

## 工作流详解

### 1. 前端工作流 (.github/workflows/frontend-ci.yml)

#### Test 阶段
- Node.js 18 环境设置
- npm 依赖缓存和安装
- ESLint 代码质量检查
- Vitest 单元测试和覆盖率
- 覆盖率报告上传到 Codecov

#### Build 阶段
- Docker Buildx 设置
- 多阶段 Docker 镜像构建
- GitHub Actions 缓存优化
- 容器健康检查测试

#### Deploy 阶段
- 构建静态资源
- 部署到 GitHub Pages
- 自动域名配置

### 2. 后端工作流 (.github/workflows/backend-ci.yml)

#### Test 阶段
- Python 3.11 环境设置
- PostgreSQL 服务启动
- pip 依赖缓存和安装
- Black 代码格式检查
- Flake8 代码质量检查
- pytest 测试和覆盖率
- 覆盖率报告上传

#### Build 阶段
- Docker 镜像构建
- 安全优化配置
- 容器烟雾测试

#### Deploy 阶段
- K3s 环境部署
- 滚动更新策略
- 健康检查验证
- 失败自动回滚

## 质量门控

### 代码质量标准

1. **前端**:
   - ESLint 检查通过率: 100%
   - 测试覆盖率: ≥ 80%
   - TypeScript 编译无错误

2. **后端**:
   - Black 格式化检查通过
   - Flake8 代码质量检查通过
   - pytest 测试覆盖率: ≥ 80%
   - 类型检查通过

### 性能要求

- 前端构建时间: < 5分钟
- 后端测试时间: < 3分钟
- 总流水线时间: < 15分钟
- Docker 镜像大小: 前端 < 100MB, 后端 < 500MB

## 部署策略

### Staging 环境

- **目标**: K3s 轻量级 Kubernetes
- **策略**: 滚动更新 (Rolling Update)
- **实例数**: 前端2个，后端2个
- **健康检查**: HTTP 探针

### 数据库迁移

- **自动执行**: Alembic 迁移脚本
- **回滚支持**: 向前兼容设计
- **备份**: 部署前自动备份

## 监控和告警

### 部署状态

- GitHub Actions 状态徽章
- 实时部署日志
- Slack/邮件通知

### 性能监控

- 构建时间趋势
- 测试执行时间
- 部署成功率

## 故障处理

### 自动回滚

触发条件：
- 部署脚本执行失败
- 健康检查超时
- 容器启动失败

回滚策略：
- 应用层回滚到上一版本
- 数据库迁移回滚（如需要）
- 自动通知相关人员

### 手动干预

```bash
# 检查部署状态
kubectl get pods -n livin-matrix-staging

# 查看日志
kubectl logs -l app=backend -n livin-matrix-staging

# 手动回滚
./deploy/scripts/rollback.sh staging

# 数据库回滚（谨慎操作）
./deploy/scripts/db-rollback.sh staging revision_id
```

## 本地测试

### 运行完整测试套件

```bash
# 测试整个CI/CD流程
./deploy/scripts/test-cicd.sh
```

### 单独测试组件

```bash
# 前端测试
cd frontend && npm test

# 后端测试
cd backend && pytest

# Docker构建测试
docker build -f deploy/docker/frontend.Dockerfile -t test-frontend .
docker build -f deploy/docker/backend.Dockerfile -t test-backend .
```

### 模拟GitHub Actions

使用 [act](https://github.com/nektos/act) 本地运行工作流：

```bash
# 安装 act
brew install act

# 运行前端工作流
act -W .github/workflows/frontend-ci.yml

# 运行后端工作流
act -W .github/workflows/backend-ci.yml
```

## 环境配置

### GitHub Secrets

需要在 GitHub 仓库设置以下密钥：

```bash
# Codecov
CODECOV_TOKEN=your_codecov_token

# Kubernetes (如果使用云服务)
KUBE_CONFIG=your_k8s_config_base64

# 容器注册表
DOCKER_USERNAME=your_docker_username
DOCKER_PASSWORD=your_docker_password

# 通知
SLACK_WEBHOOK=your_slack_webhook_url
```

### 环境变量

在 Kubernetes ConfigMap/Secret 中配置：

```yaml
# 生产环境
ENVIRONMENT=production
DATABASE_URL=postgresql://...
SECRET_KEY=your_secret_key

# Auth0配置
AUTH0_DOMAIN=your_domain.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
```

## 最佳实践

### 1. 代码提交

- 使用语义化提交消息
- 小而频繁的提交
- 提交前本地测试

### 2. 分支策略

- `main` 分支保护，只接受 PR
- Feature 分支开发
- 热修复通过 hotfix 分支

### 3. 测试策略

- 单元测试覆盖核心逻辑
- 集成测试验证 API 端点
- E2E 测试覆盖关键用户流程

### 4. 部署实践

- 蓝绿部署减少停机时间
- 金丝雀部署降低风险
- 定期备份和恢复演练

## 故障排查

### 常见问题

1. **测试失败**
   - 检查依赖版本兼容性
   - 验证环境变量配置
   - 查看详细错误日志

2. **构建失败**
   - 清理 npm/pip 缓存
   - 检查 Dockerfile 语法
   - 验证镜像基础版本

3. **部署失败**
   - 检查 Kubernetes 资源限制
   - 验证配置文件语法
   - 查看 Pod 事件和日志

### 调试命令

```bash
# 查看工作流运行状态
gh run list

# 查看特定运行的日志
gh run view <run_id> --log

# 本地调试部署脚本
bash -x deploy/scripts/deploy.sh staging

# 检查Kubernetes状态
kubectl describe pod <pod_name> -n livin-matrix-staging
```

## 联系信息

如需技术支持，请联系：

- **DevOps 团队**: devops@livin-matrix.com
- **技术负责人**: tech-lead@livin-matrix.com
- **紧急支持**: +1-xxx-xxx-xxxx
