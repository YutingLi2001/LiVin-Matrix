# AWS RDS PostgreSQL 部署指南

## 创建 RDS 实例

### 1. 使用 AWS CLI 创建 RDS 实例（免费层）

```bash
# 创建数据库子网组
aws rds create-db-subnet-group \
    --db-subnet-group-name livin-matrix-subnet-group \
    --db-subnet-group-description "LiVin Matrix Database Subnet Group" \
    --subnet-ids subnet-xxxxxx subnet-yyyyyy

# 创建安全组
aws ec2 create-security-group \
    --group-name livin-matrix-db-sg \
    --description "LiVin Matrix Database Security Group"

# 添加入站规则允许PostgreSQL连接
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 5432 \
    --source-group sg-xxxxxxxxx

# 创建RDS实例
aws rds create-db-instance \
    --db-instance-identifier livin-matrix-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.4 \
    --master-username postgres \
    --master-user-password your-secure-password \
    --allocated-storage 20 \
    --storage-type gp2 \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --db-subnet-group-name livin-matrix-subnet-group \
    --backup-retention-period 7 \
    --storage-encrypted \
    --multi-az false \
    --auto-minor-version-upgrade true \
    --copy-tags-to-snapshot true \
    --deletion-protection false
```

### 2. 通过 AWS 控制台创建（推荐）

1. 登录 AWS 控制台，进入 RDS 服务
2. 点击 "Create database"
3. 选择 "Standard create"
4. 数据库引擎：PostgreSQL
5. 版本：PostgreSQL 15.4-R2
6. 模板：Free tier
7. 设置：
   - DB instance identifier: `livin-matrix-db`
   - Master username: `postgres`
   - Master password: 设置安全密码
8. 实例配置：
   - DB instance class: `db.t3.micro`
9. 存储：
   - Storage type: General Purpose SSD (gp2)
   - Allocated storage: 20 GiB
   - Storage autoscaling: Enable
10. 连接性：
    - VPC: Default VPC
    - Subnet group: Default
    - Public access: Yes（开发环境）
    - VPC security group: Create new
    - Database port: 5432
11. 数据库认证：Database authentication
12. 监控：Enable Enhanced monitoring
13. 日志导出：PostgreSQL log
14. 备份：
    - Backup retention period: 7 days
    - Backup window: 默认
15. 维护：
    - Enable auto minor version upgrade
    - Maintenance window: 默认

## 安全配置

### 1. 安全组规则

```bash
# 仅允许应用服务器IP访问
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 5432 \
    --cidr your-app-server-ip/32
```

### 2. 参数组配置

创建自定义参数组以优化性能：

```bash
aws rds create-db-parameter-group \
    --db-parameter-group-name livin-matrix-params \
    --db-parameter-group-family postgres15 \
    --description "LiVin Matrix PostgreSQL Parameters"

# 修改参数
aws rds modify-db-parameter-group \
    --db-parameter-group-name livin-matrix-params \
    --parameters "ParameterName=shared_preload_libraries,ParameterValue=pg_stat_statements,ApplyMethod=pending-reboot"
```

## 监控和告警

### 1. CloudWatch 告警设置

```bash
# CPU 使用率告警
aws cloudwatch put-metric-alarm \
    --alarm-name "RDS-CPU-High" \
    --alarm-description "RDS CPU utilization is too high" \
    --metric-name CPUUtilization \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=DBInstanceIdentifier,Value=livin-matrix-db \
    --evaluation-periods 2

# 连接数告警
aws cloudwatch put-metric-alarm \
    --alarm-name "RDS-Connections-High" \
    --alarm-description "RDS connection count is too high" \
    --metric-name DatabaseConnections \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 15 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=DBInstanceIdentifier,Value=livin-matrix-db \
    --evaluation-periods 2
```

### 2. 性能洞察

启用性能洞察以监控查询性能：
- 在创建实例时启用 Performance Insights
- 设置保留期为 7 天（免费层）

## 环境变量配置

生产环境的数据库连接字符串：

```bash
# 获取RDS端点
aws rds describe-db-instances \
    --db-instance-identifier livin-matrix-db \
    --query 'DBInstances[0].Endpoint.Address' \
    --output text

# 设置环境变量
export DATABASE_URL=postgresql://postgres:your-password@your-rds-endpoint:5432/livin_matrix_prod
```

## 备份和恢复

### 1. 自动备份
- 备份保留期：7天
- 备份窗口：避开业务高峰期
- 自动快照：每日

### 2. 手动快照

```bash
# 创建手动快照
aws rds create-db-snapshot \
    --db-instance-identifier livin-matrix-db \
    --db-snapshot-identifier livin-matrix-snapshot-$(date +%Y%m%d)
```

## 成本优化

1. 使用 t3.micro 实例（免费层）
2. 启用存储自动扩展，按需付费
3. 设置合理的备份保留期（7天）
4. 监控连接数，避免过多连接
5. 定期清理不需要的快照

## 安全最佳实践

1. 启用数据加密
2. 使用 IAM 数据库认证（可选）
3. 定期轮换密码
4. 限制安全组访问规则
5. 启用删除保护（生产环境）
6. 监控异常访问模式