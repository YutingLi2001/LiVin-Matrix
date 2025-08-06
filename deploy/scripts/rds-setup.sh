#!/bin/bash

# RDS PostgreSQL数据库初始化脚本
# 用于创建和配置LiVin Matrix项目的AWS RDS实例

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 颜色输出
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# 配置变量
DB_INSTANCE_IDENTIFIER="livin-matrix-db"
DB_NAME="livin_matrix"
DB_USERNAME="livin_admin"
DB_ENGINE="postgres"
DB_ENGINE_VERSION="15.4"
DB_INSTANCE_CLASS="db.t3.micro"
DB_ALLOCATED_STORAGE="20"
DB_STORAGE_TYPE="gp2"
BACKUP_RETENTION_PERIOD="7"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查AWS CLI和必要工具
check_prerequisites() {
    log_info "检查必需的工具..."

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI未安装"
        exit 1
    fi

    if ! command -v jq &> /dev/null; then
        log_error "jq未安装"
        exit 1
    fi

    if ! command -v psql &> /dev/null; then
        log_warning "PostgreSQL客户端未安装，无法进行连接测试"
    fi

    log_success "工具检查完成"
}

# 验证AWS凭据
verify_aws_credentials() {
    log_info "验证AWS凭据..."

    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS凭据验证失败"
        exit 1
    fi

    local account_id=$(aws sts get-caller-identity --query Account --output text)
    log_success "AWS凭据验证成功 (账户: $account_id)"
}

# 检查VPC和安全组是否存在
check_network_resources() {
    log_info "检查网络资源..."

    # 检查VPC
    local vpc_id=$(cat "$PROJECT_ROOT/.aws-vpc-id" 2>/dev/null || echo "")
    if [ -z "$vpc_id" ] || ! aws ec2 describe-vpcs --vpc-ids "$vpc_id" &>/dev/null; then
        log_error "VPC未找到，请先运行aws-setup.sh创建网络基础设施"
        exit 1
    fi

    # 检查RDS安全组
    local rds_sg_id=$(cat "$PROJECT_ROOT/.aws-sg-rds-id" 2>/dev/null || echo "")
    if [ -z "$rds_sg_id" ] || ! aws ec2 describe-security-groups --group-ids "$rds_sg_id" &>/dev/null; then
        log_error "RDS安全组未找到，请先运行aws-setup.sh创建安全组"
        exit 1
    fi

    log_success "网络资源检查完成"
}

# 创建或验证数据库子网组
create_db_subnet_group() {
    log_info "创建数据库子网组..."

    local subnet_group_name="livin-matrix-db-subnet-group"

    # 检查子网组是否已存在
    if aws rds describe-db-subnet-groups --db-subnet-group-name "$subnet_group_name" &>/dev/null; then
        log_info "数据库子网组已存在: $subnet_group_name"
        return 0
    fi

    # 获取数据库子网ID
    local db_subnet_1a=$(cat "$PROJECT_ROOT/.aws-subnet-db-1a-id" 2>/dev/null || echo "")
    local db_subnet_1b=$(cat "$PROJECT_ROOT/.aws-subnet-db-1b-id" 2>/dev/null || echo "")

    if [ -z "$db_subnet_1a" ] || [ -z "$db_subnet_1b" ]; then
        log_error "数据库子网未找到，请先运行aws-setup.sh创建子网"
        exit 1
    fi

    # 创建数据库子网组
    aws rds create-db-subnet-group \
        --db-subnet-group-name "$subnet_group_name" \
        --db-subnet-group-description "Database subnet group for LiVin Matrix" \
        --subnet-ids "$db_subnet_1a" "$db_subnet_1b" \
        --tags Key=Name,Value="$subnet_group_name" \
               Key=Project,Value=LiVin-Matrix \
               Key=Environment,Value=production

    log_success "数据库子网组创建成功: $subnet_group_name"
}

# 创建数据库参数组
create_db_parameter_group() {
    log_info "创建数据库参数组..."

    local param_group_name="livin-matrix-postgres-params"

    # 检查参数组是否已存在
    if aws rds describe-db-parameter-groups --db-parameter-group-name "$param_group_name" &>/dev/null; then
        log_info "数据库参数组已存在: $param_group_name"
        return 0
    fi

    # 创建参数组
    aws rds create-db-parameter-group \
        --db-parameter-group-name "$param_group_name" \
        --db-parameter-group-family "postgres15" \
        --description "Custom PostgreSQL parameters for LiVin Matrix" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Environment,Value=production

    # 等待参数组创建完成
    sleep 5

    # 修改参数
    log_info "配置数据库参数..."
    aws rds modify-db-parameter-group \
        --db-parameter-group-name "$param_group_name" \
        --parameters \
            "ParameterName=max_connections,ParameterValue=100,ApplyMethod=pending-reboot" \
            "ParameterName=shared_buffers,ParameterValue=128MB,ApplyMethod=pending-reboot" \
            "ParameterName=effective_cache_size,ParameterValue=512MB,ApplyMethod=pending-reboot" \
            "ParameterName=maintenance_work_mem,ParameterValue=64MB,ApplyMethod=pending-reboot" \
            "ParameterName=checkpoint_completion_target,ParameterValue=0.9,ApplyMethod=pending-reboot" \
            "ParameterName=wal_buffers,ParameterValue=16MB,ApplyMethod=pending-reboot" \
            "ParameterName=random_page_cost,ParameterValue=1.1,ApplyMethod=pending-reboot" \
            "ParameterName=effective_io_concurrency,ParameterValue=200,ApplyMethod=pending-reboot" \
            "ParameterName=log_statement,ParameterValue=mod,ApplyMethod=immediate" \
            "ParameterName=log_min_duration_statement,ParameterValue=1000,ApplyMethod=immediate" \
            "ParameterName=log_connections,ParameterValue=1,ApplyMethod=immediate" \
            "ParameterName=log_disconnections,ParameterValue=1,ApplyMethod=immediate" \
            "ParameterName=log_lock_waits,ParameterValue=1,ApplyMethod=immediate"

    log_success "数据库参数组创建并配置完成: $param_group_name"
}

# 创建AWS Secrets Manager密钥
create_db_secret() {
    log_info "创建数据库密钥..."

    local secret_name="livin-matrix/database/credentials"

    # 检查密钥是否已存在
    if aws secretsmanager describe-secret --secret-id "$secret_name" &>/dev/null; then
        log_info "数据库密钥已存在: $secret_name"
        return 0
    fi

    # 生成随机密码
    local password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

    # 创建密钥
    local secret_arn=$(aws secretsmanager create-secret \
        --name "$secret_name" \
        --description "Database credentials for LiVin Matrix application" \
        --secret-string "{\"username\":\"$DB_USERNAME\",\"password\":\"$password\"}" \
        --kms-key-id "alias/aws/secretsmanager" \
        --query "ARN" \
        --output text)

    # 添加标签
    aws secretsmanager tag-resource \
        --secret-id "$secret_arn" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Environment,Value=production \
               Key=Component,Value=database

    log_success "数据库密钥创建成功: $secret_name"
    echo "$secret_arn" > "$PROJECT_ROOT/.aws-db-secret-arn"
}

# 创建RDS实例
create_rds_instance() {
    log_info "创建RDS PostgreSQL实例..."

    # 检查实例是否已存在
    if aws rds describe-db-instances --db-instance-identifier "$DB_INSTANCE_IDENTIFIER" &>/dev/null; then
        log_info "RDS实例已存在: $DB_INSTANCE_IDENTIFIER"
        return 0
    fi

    # 获取必要的资源ID
    local rds_sg_id=$(cat "$PROJECT_ROOT/.aws-sg-rds-id")
    local secret_arn=$(cat "$PROJECT_ROOT/.aws-db-secret-arn" 2>/dev/null || echo "")

    log_info "创建RDS实例，这可能需要10-15分钟..."

    # 创建RDS实例
    local db_args=(
        --db-instance-identifier "$DB_INSTANCE_IDENTIFIER"
        --db-name "$DB_NAME"
        --engine "$DB_ENGINE"
        --engine-version "$DB_ENGINE_VERSION"
        --db-instance-class "$DB_INSTANCE_CLASS"
        --allocated-storage "$DB_ALLOCATED_STORAGE"
        --storage-type "$DB_STORAGE_TYPE"
        --storage-encrypted
        --vpc-security-group-ids "$rds_sg_id"
        --db-subnet-group-name "livin-matrix-db-subnet-group"
        --db-parameter-group-name "livin-matrix-postgres-params"
        --backup-retention-period "$BACKUP_RETENTION_PERIOD"
        --preferred-backup-window "03:00-04:00"
        --preferred-maintenance-window "Sun:04:00-Sun:05:00"
        --no-multi-az
        --no-publicly-accessible
        --no-deletion-protection
        --tags Key=Name,Value=livin-matrix-postgres \
               Key=Project,Value=LiVin-Matrix \
               Key=Environment,Value=production \
               Key=CostCenter,Value=free-tier
    )

    # 如果有密钥，使用托管密码
    if [ -n "$secret_arn" ]; then
        db_args+=(--master-username "$DB_USERNAME" --manage-master-user-password)
    else
        # 生成临时密码
        local temp_password=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        db_args+=(--master-username "$DB_USERNAME" --master-user-password "$temp_password")
    fi

    aws rds create-db-instance "${db_args[@]}"

    log_info "等待RDS实例变为可用状态..."
    aws rds wait db-instance-available \
        --db-instance-identifier "$DB_INSTANCE_IDENTIFIER" \
        --cli-read-timeout 1800  # 30分钟超时

    # 获取数据库端点
    local db_endpoint=$(aws rds describe-db-instances \
        --db-instance-identifier "$DB_INSTANCE_IDENTIFIER" \
        --query "DBInstances[0].Endpoint.Address" \
        --output text)

    echo "$db_endpoint" > "$PROJECT_ROOT/.aws-rds-endpoint"

    log_success "RDS实例创建成功: $DB_INSTANCE_IDENTIFIER"
    log_info "数据库端点: $db_endpoint"

    # 更新Secret中的主机信息
    update_secret_with_endpoint "$db_endpoint"
}

# 更新密钥中的数据库端点信息
update_secret_with_endpoint() {
    local db_endpoint="$1"
    local secret_name="livin-matrix/database/credentials"

    log_info "更新数据库密钥中的端点信息..."

    # 获取当前密钥内容
    local current_secret=$(aws secretsmanager get-secret-value \
        --secret-id "$secret_name" \
        --query "SecretString" \
        --output text)

    # 更新密钥内容，添加主机信息
    local updated_secret=$(echo "$current_secret" | jq \
        --arg host "$db_endpoint" \
        '. + {host: $host, port: "5432", dbname: "livin_matrix"}')

    # 更新密钥
    aws secretsmanager update-secret \
        --secret-id "$secret_name" \
        --secret-string "$updated_secret"

    log_success "数据库密钥更新完成"
}

# 创建CloudWatch告警
create_cloudwatch_alarms() {
    log_info "创建CloudWatch告警..."

    # 创建SNS主题（如果不存在）
    local sns_topic_arn=$(cat "$PROJECT_ROOT/.aws-sns-topic-arn" 2>/dev/null || echo "")
    if [ -z "$sns_topic_arn" ]; then
        sns_topic_arn=$(aws sns create-topic \
            --name "livin-matrix-db-alerts" \
            --query "TopicArn" \
            --output text)
        echo "$sns_topic_arn" > "$PROJECT_ROOT/.aws-sns-topic-arn"
    fi

    # CPU使用率告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-RDS-HighCPU" \
        --alarm-description "RDS CPU utilization is high" \
        --metric-name "CPUUtilization" \
        --namespace "AWS/RDS" \
        --statistic "Average" \
        --period 300 \
        --threshold 80 \
        --comparison-operator "GreaterThanThreshold" \
        --dimensions Name=DBInstanceIdentifier,Value="$DB_INSTANCE_IDENTIFIER" \
        --evaluation-periods 3 \
        --alarm-actions "$sns_topic_arn" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=database

    # 连接数告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-RDS-HighConnections" \
        --alarm-description "RDS connection count is high" \
        --metric-name "DatabaseConnections" \
        --namespace "AWS/RDS" \
        --statistic "Average" \
        --period 300 \
        --threshold 80 \
        --comparison-operator "GreaterThanThreshold" \
        --dimensions Name=DBInstanceIdentifier,Value="$DB_INSTANCE_IDENTIFIER" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=database

    # 可用存储空间告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-RDS-LowFreeSpace" \
        --alarm-description "RDS free storage space is low" \
        --metric-name "FreeStorageSpace" \
        --namespace "AWS/RDS" \
        --statistic "Average" \
        --period 300 \
        --threshold 2147483648 \
        --comparison-operator "LessThanThreshold" \
        --dimensions Name=DBInstanceIdentifier,Value="$DB_INSTANCE_IDENTIFIER" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=database

    log_success "CloudWatch告警创建完成"
}

# 初始化数据库结构
initialize_database() {
    log_info "初始化数据库结构..."

    # 检查是否有psql客户端
    if ! command -v psql &> /dev/null; then
        log_warning "PostgreSQL客户端未安装，跳过数据库初始化"
        log_info "请在应用程序首次启动时自动初始化数据库"
        return 0
    fi

    # 获取数据库连接信息
    local db_endpoint=$(cat "$PROJECT_ROOT/.aws-rds-endpoint")
    local secret_name="livin-matrix/database/credentials"

    # 从AWS Secrets Manager获取凭据
    local db_credentials=$(aws secretsmanager get-secret-value \
        --secret-id "$secret_name" \
        --query "SecretString" \
        --output text)

    local db_username=$(echo "$db_credentials" | jq -r '.username')
    local db_password=$(echo "$db_credentials" | jq -r '.password')

    # 测试数据库连接
    log_info "测试数据库连接..."
    if PGPASSWORD="$db_password" psql \
        -h "$db_endpoint" \
        -U "$db_username" \
        -d "$DB_NAME" \
        -c "SELECT version();" &>/dev/null; then
        log_success "数据库连接测试成功"
    else
        log_error "数据库连接测试失败"
        return 1
    fi

    # 运行数据库迁移（如果有alembic配置）
    if [ -f "$PROJECT_ROOT/backend/alembic.ini" ]; then
        log_info "运行数据库迁移..."

        # 设置数据库URL环境变量
        export DATABASE_URL="postgresql://$db_username:$db_password@$db_endpoint:5432/$DB_NAME"

        # 进入后端目录并运行迁移
        cd "$PROJECT_ROOT/backend"
        if command -v alembic &> /dev/null; then
            alembic upgrade head
            log_success "数据库迁移完成"
        else
            log_warning "Alembic未安装，请手动运行数据库迁移"
        fi
        cd "$PROJECT_ROOT"
    else
        log_info "未找到Alembic配置，跳过数据库迁移"
    fi
}

# 验证RDS部署
verify_rds_deployment() {
    log_info "验证RDS部署..."

    local issues=()

    # 检查RDS实例状态
    local db_status=$(aws rds describe-db-instances \
        --db-instance-identifier "$DB_INSTANCE_IDENTIFIER" \
        --query "DBInstances[0].DBInstanceStatus" \
        --output text 2>/dev/null || echo "not-found")

    if [ "$db_status" != "available" ]; then
        issues+=("RDS实例状态异常: $db_status")
    fi

    # 检查密钥
    local secret_name="livin-matrix/database/credentials"
    if ! aws secretsmanager describe-secret --secret-id "$secret_name" &>/dev/null; then
        issues+=("数据库密钥未找到")
    fi

    # 检查CloudWatch告警
    local alarms=$(aws cloudwatch describe-alarms \
        --alarm-name-prefix "LiVin-Matrix-RDS" \
        --query "MetricAlarms[].AlarmName" \
        --output text)

    if [ -z "$alarms" ]; then
        issues+=("CloudWatch告警未配置")
    fi

    if [ ${#issues[@]} -eq 0 ]; then
        log_success "RDS部署验证通过"
        display_rds_info
    else
        log_error "发现以下问题:"
        for issue in "${issues[@]}"; do
            log_error "  - $issue"
        done
        exit 1
    fi
}

# 显示RDS部署信息
display_rds_info() {
    log_info "RDS PostgreSQL部署完成！"
    echo
    echo "=== RDS实例信息 ==="

    local db_endpoint=$(aws rds describe-db-instances \
        --db-instance-identifier "$DB_INSTANCE_IDENTIFIER" \
        --query "DBInstances[0].Endpoint.Address" \
        --output text)

    local db_port=$(aws rds describe-db-instances \
        --db-instance-identifier "$DB_INSTANCE_IDENTIFIER" \
        --query "DBInstances[0].Endpoint.Port" \
        --output text)

    echo "实例标识符: $DB_INSTANCE_IDENTIFIER"
    echo "数据库端点: $db_endpoint"
    echo "端口: $db_port"
    echo "数据库名称: $DB_NAME"
    echo "用户名: $DB_USERNAME"
    echo "密钥位置: AWS Secrets Manager (livin-matrix/database/credentials)"

    echo
    echo "=== 连接字符串 ==="
    echo "DATABASE_URL=postgresql://$DB_USERNAME:<password>@$db_endpoint:$db_port/$DB_NAME"

    echo
    echo "=== 后续步骤 ==="
    echo "1. 在Kubernetes中部署External Secrets Operator"
    echo "2. 配置应用程序以使用AWS Secrets Manager"
    echo "3. 运行数据库迁移初始化表结构"
    echo "4. 配置数据库备份和恢复策略"

    echo
    echo "重要提醒："
    echo "- RDS实例位于私有子网中，只能从EKS集群访问"
    echo "- 定期监控免费层使用情况和数据库性能"
    echo "- 备份会自动保留7天，可在AWS控制台查看"
}

# 清理函数
cleanup_on_error() {
    log_error "RDS设置失败，正在清理临时文件..."
    rm -f "$PROJECT_ROOT"/.aws-db-*
}

# 主函数
main() {
    log_info "开始RDS PostgreSQL设置..."

    # 设置错误处理
    trap cleanup_on_error ERR

    # 执行设置步骤
    check_prerequisites
    verify_aws_credentials
    check_network_resources
    create_db_subnet_group
    create_db_parameter_group
    create_db_secret
    create_rds_instance
    create_cloudwatch_alarms
    initialize_database
    verify_rds_deployment

    log_success "RDS PostgreSQL设置完成！"
}

# 如果直接运行此脚本，则执行主函数
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
