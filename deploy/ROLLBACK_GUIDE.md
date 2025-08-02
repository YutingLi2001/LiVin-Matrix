# 回滚操作指南

## 概述

本指南描述了如何在部署失败或出现问题时执行回滚操作。

## 自动回滚

### GitHub Actions 自动回滚

当部署失败时，CI/CD流水线会自动触发回滚：

1. **部署失败检测**: 如果部署脚本返回非零退出码
2. **健康检查失败**: 如果部署后的健康检查失败
3. **自动回滚**: 自动回滚到上一个稳定版本

### 触发条件

- Docker容器启动失败
- 应用健康检查端点返回错误
- Kubernetes部署超时
- 数据库连接失败

## 手动回滚

### 1. 应用回滚

回滚到上一个版本：
```bash
./deploy/scripts/rollback.sh staging
```

回滚到特定版本：
```bash
./deploy/scripts/rollback.sh staging 3
```

### 2. 数据库回滚

**警告**: 数据库回滚可能导致数据丢失，请谨慎操作！

```bash
./deploy/scripts/db-rollback.sh staging abc123def456
```

### 3. 查看回滚历史

```bash
kubectl rollout history deployment/backend -n livin-matrix-staging
kubectl rollout history deployment/frontend -n livin-matrix-staging
```

## 回滚验证

### 1. 健康检查

回滚完成后，脚本会自动执行健康检查：

- 后端API健康检查：`GET /health`
- 前端健康检查：`GET /health`
- 数据库连接验证

### 2. 功能测试

手动验证关键功能：

```bash
# 测试API端点
curl -f https://staging.livin-matrix.com/api/v1/health

# 测试前端
curl -f https://staging.livin-matrix.com/health

# 测试数据库连接
kubectl exec -n livin-matrix-staging deployment/backend -- python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database OK')
"
```

## 故障恢复流程

### 1. 快速恢复 (< 5分钟)

```bash
# 1. 立即回滚到上一版本
./deploy/scripts/rollback.sh staging

# 2. 验证服务状态
kubectl get pods -n livin-matrix-staging

# 3. 测试关键功能
curl -f https://staging.livin-matrix.com/api/v1/health
```

### 2. 深度恢复 (> 5分钟)

如果快速恢复失败：

```bash
# 1. 查看详细错误信息
kubectl describe pods -n livin-matrix-staging
kubectl logs -l app=backend -n livin-matrix-staging --tail=100

# 2. 回滚到更早的稳定版本
kubectl rollout history deployment/backend -n livin-matrix-staging
./deploy/scripts/rollback.sh staging 2

# 3. 如果仍有问题，考虑数据库回滚
./deploy/scripts/db-rollback.sh staging previous_stable_revision
```

## 数据库回滚策略

### 1. 向前兼容的迁移

推荐的迁移策略：
- 添加字段设为可选
- 重命名通过添加新字段实现
- 删除分为多个阶段

### 2. 回滚点管理

```bash
# 创建回滚点
kubectl exec -n livin-matrix-staging deployment/backend -- alembic stamp head

# 查看当前版本
kubectl exec -n livin-matrix-staging deployment/backend -- alembic current

# 查看迁移历史
kubectl exec -n livin-matrix-staging deployment/backend -- alembic history
```

### 3. 数据备份恢复

如果需要从备份恢复：

```bash
# 恢复数据库
kubectl exec -i -n livin-matrix-staging deployment/postgres -- psql -U postgres -d livin_matrix_staging < deploy/backups/db_backup_20240801_120000.sql
```

## 监控和告警

### 1. 回滚监控

回滚操作会记录到以下位置：
- 日志文件：`deploy/rollback.log`
- Kubernetes事件：`kubectl get events -n livin-matrix-staging`

### 2. 告警设置

建议设置以下告警：
- 部署失败告警
- 回滚操作告警
- 健康检查失败告警

## 最佳实践

### 1. 预防措施

- 在staging环境充分测试
- 实施蓝绿部署策略
- 定期备份数据库
- 保持向前兼容的API设计

### 2. 回滚准备

- 保持最近3个版本的镜像
- 定期测试回滚脚本
- 文档化回滚流程
- 建立应急响应团队

### 3. 事后分析

- 记录回滚原因
- 分析根本原因
- 改进部署流程
- 更新回滚文档

## 联系信息

如果遇到无法解决的回滚问题，请联系：

- 技术负责人：[技术负责人联系方式]
- 运维团队：[运维团队联系方式]
- 紧急热线：[紧急联系电话]