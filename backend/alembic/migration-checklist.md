# 生产环境数据库迁移安全检查清单

## 迁移前检查 (Pre-Migration Checklist)

### 1. 数据库备份
- [ ] 创建完整数据库备份
- [ ] 验证备份文件完整性
- [ ] 确认备份恢复流程测试过
- [ ] 记录备份文件位置和大小

```bash
# 创建备份
pg_dump -h your-rds-endpoint -U postgres -d livin_matrix_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 验证备份
ls -la backup_*.sql
```

### 2. 迁移脚本验证
- [ ] 在开发环境完整测试迁移脚本
- [ ] 在staging环境验证迁移脚本
- [ ] 确认迁移脚本支持回滚
- [ ] 检查迁移脚本语法和逻辑

```bash
# 测试迁移升级
alembic upgrade head

# 测试迁移回滚
alembic downgrade -1
alembic upgrade head
```

### 3. 影响评估
- [ ] 评估迁移执行时间
- [ ] 确认是否需要停机维护
- [ ] 评估对现有功能的影响
- [ ] 准备回滚计划

### 4. 环境检查
- [ ] 确认数据库连接正常
- [ ] 检查磁盘空间充足
- [ ] 确认数据库权限正确
- [ ] 检查数据库性能指标

## 迁移执行流程 (Migration Execution)

### 1. 执行前准备
```bash
# 设置生产环境变量
export DATABASE_URL=postgresql://user:pass@prod-endpoint:5432/livin_matrix_prod

# 检查当前数据库版本
alembic current

# 检查待执行的迁移
alembic show head
```

### 2. 执行迁移
```bash
# 执行迁移（建议在屏幕会话中执行）
screen -S db_migration
alembic upgrade head

# 记录执行时间和结果
echo "Migration completed at $(date)" >> migration_log.txt
```

### 3. 迁移验证
- [ ] 检查所有表结构正确创建
- [ ] 验证数据完整性
- [ ] 测试关键功能
- [ ] 检查性能指标

```bash
# 验证表结构
psql -h prod-endpoint -U postgres -d livin_matrix_prod -c "\dt"

# 检查约束
psql -h prod-endpoint -U postgres -d livin_matrix_prod -c "\d+ users"
psql -h prod-endpoint -U postgres -d livin_matrix_prod -c "\d+ user_daily_records"
psql -h prod-endpoint -U postgres -d livin_matrix_prod -c "\d+ workout_sessions"
```

## 迁移后检查 (Post-Migration Checklist)

### 1. 功能验证
- [ ] 用户认证功能正常
- [ ] 数据录入功能正常
- [ ] 数据查询功能正常
- [ ] API端点响应正常

### 2. 性能监控
- [ ] 数据库CPU使用率正常
- [ ] 数据库内存使用率正常
- [ ] 查询响应时间正常
- [ ] 连接数在合理范围

### 3. 日志检查
- [ ] 应用日志无错误
- [ ] 数据库日志无异常
- [ ] 监控告警正常
- [ ] 性能指标正常

## 回滚程序 (Rollback Procedure)

### 触发条件
- 迁移执行失败
- 功能验证失败
- 性能严重下降
- 数据完整性问题

### 回滚步骤
```bash
# 1. 停止应用服务
sudo systemctl stop livin-matrix-backend

# 2. 执行数据库回滚
alembic downgrade -1

# 3. 或者从备份恢复（如果回滚不可行）
psql -h prod-endpoint -U postgres -d livin_matrix_prod < backup_YYYYMMDD_HHMMSS.sql

# 4. 重启应用服务
sudo systemctl start livin-matrix-backend
```

### 回滚验证
- [ ] 数据库结构回到迁移前状态
- [ ] 应用功能正常
- [ ] 数据完整性验证
- [ ] 性能指标正常

## 常见问题处理 (Troubleshooting)

### 迁移执行卡住
```bash
# 检查数据库锁
SELECT * FROM pg_locks WHERE NOT granted;

# 检查活跃查询
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

### 约束冲突
```bash
# 检查约束违反的数据
SELECT * FROM users WHERE email IS NULL OR email = '';
SELECT * FROM user_daily_records WHERE sleep_quality < 1 OR sleep_quality > 10;
```

### 权限问题
```bash
# 检查用户权限
\du
\dp users
\dp user_daily_records
```

## 联系信息

- **DBA联系方式**: [dba@company.com]
- **开发团队联系方式**: [dev-team@company.com]
- **紧急联系电话**: [+86-xxx-xxxx-xxxx]

## 文档版本

| 版本 | 日期 | 修改内容 | 修改人 |
|------|------|----------|--------|
| 1.0 | 2025-07-31 | 初始版本 | James (Dev) |