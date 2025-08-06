#!/bin/bash

# AWS基础设施初始化脚本
# 用于在AWS上部署LiVin Matrix项目的完整基础设施

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
AWS_CONFIG_DIR="$PROJECT_ROOT/deploy/aws"

# 颜色输出
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

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

# 检查必需的工具
check_prerequisites() {
    log_info "检查必需的工具..."

    local missing_tools=()

    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws-cli")
    fi

    if ! command -v eksctl &> /dev/null; then
        missing_tools+=("eksctl")
    fi

    if ! command -v kubectl &> /dev/null; then
        missing_tools+=("kubectl")
    fi

    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必需的工具: ${missing_tools[*]}"
        log_info "请安装缺少的工具后重新运行此脚本"
        exit 1
    fi

    log_success "所有必需工具已安装"
}

# 验证AWS凭据
verify_aws_credentials() {
    log_info "验证AWS凭据..."

    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS凭据验证失败"
        log_info "请运行 'aws configure' 设置您的AWS凭据"
        exit 1
    fi

    local account_id=$(aws sts get-caller-identity --query Account --output text)
    local user_arn=$(aws sts get-caller-identity --query Arn --output text)

    log_success "AWS凭据验证成功"
    log_info "账户ID: $account_id"
    log_info "用户ARN: $user_arn"
}

# 检查免费层资源使用情况
check_free_tier_usage() {
    log_info "检查AWS免费层资源使用情况..."

    # 检查现有EKS集群
    local existing_clusters=$(aws eks list-clusters --query "clusters" --output text 2>/dev/null || echo "")
    if [ -n "$existing_clusters" ]; then
        log_warning "检测到现有EKS集群: $existing_clusters"
        log_warning "免费层每月只允许1个EKS集群"
    fi

    # 检查EC2实例
    local running_instances=$(aws ec2 describe-instances \
        --filters "Name=instance-state-name,Values=running" \
        --query "Reservations[*].Instances[*].InstanceId" \
        --output text 2>/dev/null || echo "")
    if [ -n "$running_instances" ]; then
        log_warning "检测到运行中的EC2实例: $running_instances"
        log_info "请确保总使用时间不超过750小时/月"
    fi

    # 检查RDS实例
    local rds_instances=$(aws rds describe-db-instances \
        --query "DBInstances[*].DBInstanceIdentifier" \
        --output text 2>/dev/null || echo "")
    if [ -n "$rds_instances" ]; then
        log_warning "检测到现有RDS实例: $rds_instances"
        log_info "免费层只允许1个db.t3.micro实例"
    fi

    log_success "免费层资源检查完成"
}

# 创建或更新VPC和网络基础设施
deploy_vpc_infrastructure() {
    log_info "部署VPC和网络基础设施..."

    # 检查VPC是否已存在
    local vpc_id=$(aws ec2 describe-vpcs \
        --filters "Name=tag:Name,Values=livin-matrix-vpc" \
        --query "Vpcs[0].VpcId" \
        --output text 2>/dev/null || echo "None")

    if [ "$vpc_id" != "None" ]; then
        log_info "找到现有VPC: $vpc_id"
        echo "$vpc_id" > "$PROJECT_ROOT/.aws-vpc-id"
    else
        log_info "创建新的VPC..."

        # 创建VPC
        vpc_id=$(aws ec2 create-vpc \
            --cidr-block "10.0.0.0/16" \
            --query "Vpc.VpcId" \
            --output text)

        # 添加标签
        aws ec2 create-tags \
            --resources "$vpc_id" \
            --tags Key=Name,Value=livin-matrix-vpc \
                   Key=Project,Value=LiVin-Matrix \
                   Key=Environment,Value=production \
                   Key=CostCenter,Value=free-tier

        # 启用DNS主机名和DNS解析
        aws ec2 modify-vpc-attribute --vpc-id "$vpc_id" --enable-dns-hostnames
        aws ec2 modify-vpc-attribute --vpc-id "$vpc_id" --enable-dns-support

        echo "$vpc_id" > "$PROJECT_ROOT/.aws-vpc-id"
        log_success "VPC创建成功: $vpc_id"
    fi

    # 创建Internet Gateway
    create_internet_gateway "$vpc_id"

    # 创建子网
    create_subnets "$vpc_id"

    # 创建NAT Gateway
    create_nat_gateway "$vpc_id"

    # 创建路由表
    create_route_tables "$vpc_id"

    # 创建安全组
    create_security_groups "$vpc_id"
}

create_internet_gateway() {
    local vpc_id="$1"
    log_info "创建Internet Gateway..."

    local igw_id=$(aws ec2 describe-internet-gateways \
        --filters "Name=tag:Name,Values=livin-matrix-igw" \
        --query "InternetGateways[0].InternetGatewayId" \
        --output text 2>/dev/null || echo "None")

    if [ "$igw_id" = "None" ]; then
        igw_id=$(aws ec2 create-internet-gateway \
            --query "InternetGateway.InternetGatewayId" \
            --output text)

        aws ec2 create-tags \
            --resources "$igw_id" \
            --tags Key=Name,Value=livin-matrix-igw \
                   Key=Project,Value=LiVin-Matrix

        aws ec2 attach-internet-gateway \
            --internet-gateway-id "$igw_id" \
            --vpc-id "$vpc_id"

        log_success "Internet Gateway创建成功: $igw_id"
    else
        log_info "使用现有Internet Gateway: $igw_id"
    fi

    echo "$igw_id" > "$PROJECT_ROOT/.aws-igw-id"
}

create_subnets() {
    local vpc_id="$1"
    log_info "创建子网..."

    # 公有子网配置
    declare -A public_subnets=(
        ["public-1a"]="10.0.1.0/24,us-east-1a"
        ["public-1b"]="10.0.2.0/24,us-east-1b"
    )

    # 私有子网配置
    declare -A private_subnets=(
        ["private-1a"]="10.0.10.0/24,us-east-1a"
        ["private-1b"]="10.0.11.0/24,us-east-1b"
    )

    # 数据库子网配置
    declare -A db_subnets=(
        ["db-1a"]="10.0.20.0/24,us-east-1a"
        ["db-1b"]="10.0.21.0/24,us-east-1b"
    )

    # 创建公有子网
    for subnet_name in "${!public_subnets[@]}"; do
        IFS=',' read -r cidr az <<< "${public_subnets[$subnet_name]}"
        create_subnet "$vpc_id" "$subnet_name" "$cidr" "$az" "public"
    done

    # 创建私有子网
    for subnet_name in "${!private_subnets[@]}"; do
        IFS=',' read -r cidr az <<< "${private_subnets[$subnet_name]}"
        create_subnet "$vpc_id" "$subnet_name" "$cidr" "$az" "private"
    done

    # 创建数据库子网
    for subnet_name in "${!db_subnets[@]}"; do
        IFS=',' read -r cidr az <<< "${db_subnets[$subnet_name]}"
        create_subnet "$vpc_id" "$subnet_name" "$cidr" "$az" "database"
    done
}

create_subnet() {
    local vpc_id="$1"
    local subnet_name="$2"
    local cidr="$3"
    local az="$4"
    local subnet_type="$5"

    local full_name="livin-matrix-$subnet_name"

    local subnet_id=$(aws ec2 describe-subnets \
        --filters "Name=tag:Name,Values=$full_name" \
        --query "Subnets[0].SubnetId" \
        --output text 2>/dev/null || echo "None")

    if [ "$subnet_id" = "None" ]; then
        subnet_id=$(aws ec2 create-subnet \
            --vpc-id "$vpc_id" \
            --cidr-block "$cidr" \
            --availability-zone "$az" \
            --query "Subnet.SubnetId" \
            --output text)

        local tags="Key=Name,Value=$full_name Key=Project,Value=LiVin-Matrix Key=Type,Value=$subnet_type"

        # 为公有子网添加额外的标签
        if [ "$subnet_type" = "public" ]; then
            tags="$tags Key=kubernetes.io/role/elb,Value=1"
            # 启用公有IP分配
            aws ec2 modify-subnet-attribute \
                --subnet-id "$subnet_id" \
                --map-public-ip-on-launch
        elif [ "$subnet_type" = "private" ]; then
            tags="$tags Key=kubernetes.io/role/internal-elb,Value=1"
        fi

        aws ec2 create-tags --resources "$subnet_id" --tags $tags

        log_success "子网创建成功: $full_name ($subnet_id)"
    else
        log_info "使用现有子网: $full_name ($subnet_id)"
    fi

    echo "$subnet_id" > "$PROJECT_ROOT/.aws-subnet-$subnet_name-id"
}

create_nat_gateway() {
    local vpc_id="$1"
    log_info "创建NAT Gateway..."

    # 获取公有子网ID
    local public_subnet_id=$(cat "$PROJECT_ROOT/.aws-subnet-public-1a-id")

    local nat_id=$(aws ec2 describe-nat-gateways \
        --filter "Name=tag:Name,Values=livin-matrix-nat-gw" \
               "Name=state,Values=available" \
        --query "NatGateways[0].NatGatewayId" \
        --output text 2>/dev/null || echo "None")

    if [ "$nat_id" = "None" ]; then
        # 分配弹性IP
        local eip_alloc_id=$(aws ec2 allocate-address \
            --domain vpc \
            --query "AllocationId" \
            --output text)

        aws ec2 create-tags \
            --resources "$eip_alloc_id" \
            --tags Key=Name,Value=livin-matrix-nat-eip \
                   Key=Project,Value=LiVin-Matrix

        # 创建NAT Gateway
        nat_id=$(aws ec2 create-nat-gateway \
            --subnet-id "$public_subnet_id" \
            --allocation-id "$eip_alloc_id" \
            --query "NatGateway.NatGatewayId" \
            --output text)

        aws ec2 create-tags \
            --resources "$nat_id" \
            --tags Key=Name,Value=livin-matrix-nat-gw \
                   Key=Project,Value=LiVin-Matrix

        log_info "等待NAT Gateway变为可用状态..."
        aws ec2 wait nat-gateway-available --nat-gateway-ids "$nat_id"

        log_success "NAT Gateway创建成功: $nat_id"
    else
        log_info "使用现有NAT Gateway: $nat_id"
    fi

    echo "$nat_id" > "$PROJECT_ROOT/.aws-nat-gw-id"
}

create_route_tables() {
    local vpc_id="$1"
    log_info "创建路由表..."

    local igw_id=$(cat "$PROJECT_ROOT/.aws-igw-id")
    local nat_id=$(cat "$PROJECT_ROOT/.aws-nat-gw-id")

    # 创建公有路由表
    create_route_table "$vpc_id" "public" "$igw_id" "0.0.0.0/0"

    # 创建私有路由表
    create_route_table "$vpc_id" "private" "$nat_id" "0.0.0.0/0"

    # 关联子网到路由表
    associate_subnets_to_route_tables
}

create_route_table() {
    local vpc_id="$1"
    local rt_type="$2"
    local gateway_id="$3"
    local destination="$4"

    local rt_name="livin-matrix-$rt_type-rt"

    local rt_id=$(aws ec2 describe-route-tables \
        --filters "Name=tag:Name,Values=$rt_name" \
        --query "RouteTables[0].RouteTableId" \
        --output text 2>/dev/null || echo "None")

    if [ "$rt_id" = "None" ]; then
        rt_id=$(aws ec2 create-route-table \
            --vpc-id "$vpc_id" \
            --query "RouteTable.RouteTableId" \
            --output text)

        aws ec2 create-tags \
            --resources "$rt_id" \
            --tags Key=Name,Value="$rt_name" \
                   Key=Project,Value=LiVin-Matrix

        # 添加路由
        if [ "$rt_type" = "public" ]; then
            aws ec2 create-route \
                --route-table-id "$rt_id" \
                --destination-cidr-block "$destination" \
                --gateway-id "$gateway_id"
        else
            aws ec2 create-route \
                --route-table-id "$rt_id" \
                --destination-cidr-block "$destination" \
                --nat-gateway-id "$gateway_id"
        fi

        log_success "路由表创建成功: $rt_name ($rt_id)"
    else
        log_info "使用现有路由表: $rt_name ($rt_id)"
    fi

    echo "$rt_id" > "$PROJECT_ROOT/.aws-rt-$rt_type-id"
}

associate_subnets_to_route_tables() {
    log_info "关联子网到路由表..."

    local public_rt_id=$(cat "$PROJECT_ROOT/.aws-rt-public-id")
    local private_rt_id=$(cat "$PROJECT_ROOT/.aws-rt-private-id")

    # 关联公有子网
    for subnet in "public-1a" "public-1b"; do
        local subnet_id=$(cat "$PROJECT_ROOT/.aws-subnet-$subnet-id")
        aws ec2 associate-route-table \
            --route-table-id "$public_rt_id" \
            --subnet-id "$subnet_id" 2>/dev/null || true
    done

    # 关联私有子网
    for subnet in "private-1a" "private-1b" "db-1a" "db-1b"; do
        local subnet_id=$(cat "$PROJECT_ROOT/.aws-subnet-$subnet-id")
        aws ec2 associate-route-table \
            --route-table-id "$private_rt_id" \
            --subnet-id "$subnet_id" 2>/dev/null || true
    done

    log_success "子网路由表关联完成"
}

create_security_groups() {
    local vpc_id="$1"
    log_info "创建安全组..."

    # ALB安全组
    create_alb_security_group "$vpc_id"

    # EKS安全组
    create_eks_security_group "$vpc_id"

    # RDS安全组
    create_rds_security_group "$vpc_id"
}

create_alb_security_group() {
    local vpc_id="$1"

    local sg_id=$(aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=livin-matrix-alb-sg" \
        --query "SecurityGroups[0].GroupId" \
        --output text 2>/dev/null || echo "None")

    if [ "$sg_id" = "None" ]; then
        sg_id=$(aws ec2 create-security-group \
            --group-name "livin-matrix-alb-sg" \
            --description "Security group for Application Load Balancer" \
            --vpc-id "$vpc_id" \
            --query "GroupId" \
            --output text)

        aws ec2 create-tags \
            --resources "$sg_id" \
            --tags Key=Name,Value=livin-matrix-alb-sg \
                   Key=Project,Value=LiVin-Matrix

        # 添加入站规则
        aws ec2 authorize-security-group-ingress \
            --group-id "$sg_id" \
            --protocol tcp \
            --port 80 \
            --cidr 0.0.0.0/0

        aws ec2 authorize-security-group-ingress \
            --group-id "$sg_id" \
            --protocol tcp \
            --port 443 \
            --cidr 0.0.0.0/0

        log_success "ALB安全组创建成功: $sg_id"
    else
        log_info "使用现有ALB安全组: $sg_id"
    fi

    echo "$sg_id" > "$PROJECT_ROOT/.aws-sg-alb-id"
}

create_eks_security_group() {
    local vpc_id="$1"

    local sg_id=$(aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=livin-matrix-eks-sg" \
        --query "SecurityGroups[0].GroupId" \
        --output text 2>/dev/null || echo "None")

    if [ "$sg_id" = "None" ]; then
        sg_id=$(aws ec2 create-security-group \
            --group-name "livin-matrix-eks-sg" \
            --description "Security group for EKS cluster nodes" \
            --vpc-id "$vpc_id" \
            --query "GroupId" \
            --output text)

        aws ec2 create-tags \
            --resources "$sg_id" \
            --tags Key=Name,Value=livin-matrix-eks-sg \
                   Key=Project,Value=LiVin-Matrix

        local alb_sg_id=$(cat "$PROJECT_ROOT/.aws-sg-alb-id")

        # 来自ALB的HTTP流量
        aws ec2 authorize-security-group-ingress \
            --group-id "$sg_id" \
            --protocol tcp \
            --port 80 \
            --source-group "$alb_sg_id"

        # 来自ALB的后端API流量
        aws ec2 authorize-security-group-ingress \
            --group-id "$sg_id" \
            --protocol tcp \
            --port 8000 \
            --source-group "$alb_sg_id"

        # 节点间通信
        aws ec2 authorize-security-group-ingress \
            --group-id "$sg_id" \
            --protocol tcp \
            --port 0-65535 \
            --source-group "$sg_id"

        log_success "EKS安全组创建成功: $sg_id"
    else
        log_info "使用现有EKS安全组: $sg_id"
    fi

    echo "$sg_id" > "$PROJECT_ROOT/.aws-sg-eks-id"
}

create_rds_security_group() {
    local vpc_id="$1"

    local sg_id=$(aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=livin-matrix-rds-sg" \
        --query "SecurityGroups[0].GroupId" \
        --output text 2>/dev/null || echo "None")

    if [ "$sg_id" = "None" ]; then
        sg_id=$(aws ec2 create-security-group \
            --group-name "livin-matrix-rds-sg" \
            --description "Security group for RDS PostgreSQL database" \
            --vpc-id "$vpc_id" \
            --query "GroupId" \
            --output text)

        aws ec2 create-tags \
            --resources "$sg_id" \
            --tags Key=Name,Value=livin-matrix-rds-sg \
                   Key=Project,Value=LiVin-Matrix

        local eks_sg_id=$(cat "$PROJECT_ROOT/.aws-sg-eks-id")

        # 仅允许EKS节点访问数据库
        aws ec2 authorize-security-group-ingress \
            --group-id "$sg_id" \
            --protocol tcp \
            --port 5432 \
            --source-group "$eks_sg_id"

        log_success "RDS安全组创建成功: $sg_id"
    else
        log_info "使用现有RDS安全组: $sg_id"
    fi

    echo "$sg_id" > "$PROJECT_ROOT/.aws-sg-rds-id"
}

# 部署EKS集群
deploy_eks_cluster() {
    log_info "部署EKS集群..."

    # 检查集群是否已存在
    if aws eks describe-cluster --name "livin-matrix-cluster" &>/dev/null; then
        log_info "EKS集群已存在，跳过创建"
        return 0
    fi

    log_info "创建EKS集群，这可能需要15-20分钟..."

    eksctl create cluster \
        --config-file="$AWS_CONFIG_DIR/eks-cluster.yaml" \
        --verbose 4

    log_success "EKS集群创建完成"

    # 配置kubectl
    aws eks update-kubeconfig \
        --region us-east-1 \
        --name livin-matrix-cluster

    log_success "kubectl配置完成"
}

# 部署RDS数据库
deploy_rds_database() {
    log_info "部署RDS PostgreSQL数据库..."

    # 检查数据库是否已存在
    if aws rds describe-db-instances --db-instance-identifier "livin-matrix-db" &>/dev/null; then
        log_info "RDS实例已存在，跳过创建"
        return 0
    fi

    # 创建数据库子网组
    create_db_subnet_group

    # 创建数据库参数组
    create_db_parameter_group

    # 创建数据库实例
    create_rds_instance

    log_success "RDS数据库部署完成"
}

create_db_subnet_group() {
    log_info "创建数据库子网组..."

    local db_subnet_1a=$(cat "$PROJECT_ROOT/.aws-subnet-db-1a-id")
    local db_subnet_1b=$(cat "$PROJECT_ROOT/.aws-subnet-db-1b-id")

    if ! aws rds describe-db-subnet-groups --db-subnet-group-name "livin-matrix-db-subnet-group" &>/dev/null; then
        aws rds create-db-subnet-group \
            --db-subnet-group-name "livin-matrix-db-subnet-group" \
            --db-subnet-group-description "Database subnet group for LiVin Matrix" \
            --subnet-ids "$db_subnet_1a" "$db_subnet_1b" \
            --tags Key=Name,Value=livin-matrix-db-subnet-group \
                   Key=Project,Value=LiVin-Matrix

        log_success "数据库子网组创建成功"
    else
        log_info "使用现有数据库子网组"
    fi
}

create_db_parameter_group() {
    log_info "创建数据库参数组..."

    if ! aws rds describe-db-parameter-groups --db-parameter-group-name "livin-matrix-postgres-params" &>/dev/null; then
        aws rds create-db-parameter-group \
            --db-parameter-group-name "livin-matrix-postgres-params" \
            --db-parameter-group-family "postgres15" \
            --description "Custom PostgreSQL parameters for LiVin Matrix" \
            --tags Key=Project,Value=LiVin-Matrix

        # 修改参数
        aws rds modify-db-parameter-group \
            --db-parameter-group-name "livin-matrix-postgres-params" \
            --parameters "ParameterName=max_connections,ParameterValue=100,ApplyMethod=pending-reboot" \
                        "ParameterName=shared_buffers,ParameterValue=128MB,ApplyMethod=pending-reboot" \
                        "ParameterName=log_statement,ParameterValue=mod,ApplyMethod=immediate"

        log_success "数据库参数组创建成功"
    else
        log_info "使用现有数据库参数组"
    fi
}

create_rds_instance() {
    log_info "创建RDS实例，这可能需要10-15分钟..."

    local rds_sg_id=$(cat "$PROJECT_ROOT/.aws-sg-rds-id")

    aws rds create-db-instance \
        --db-instance-identifier "livin-matrix-db" \
        --db-name "livin_matrix" \
        --engine "postgres" \
        --engine-version "15.4" \
        --db-instance-class "db.t3.micro" \
        --allocated-storage 20 \
        --storage-type "gp2" \
        --storage-encrypted \
        --master-username "livin_admin" \
        --manage-master-user-password \
        --vpc-security-group-ids "$rds_sg_id" \
        --db-subnet-group-name "livin-matrix-db-subnet-group" \
        --db-parameter-group-name "livin-matrix-postgres-params" \
        --backup-retention-period 7 \
        --preferred-backup-window "03:00-04:00" \
        --preferred-maintenance-window "Sun:04:00-Sun:05:00" \
        --no-multi-az \
        --no-publicly-accessible \
        --tags Key=Name,Value=livin-matrix-postgres \
               Key=Project,Value=LiVin-Matrix \
               Key=Environment,Value=production

    log_info "等待RDS实例变为可用状态..."
    aws rds wait db-instance-available --db-instance-identifier "livin-matrix-db"

    log_success "RDS实例创建成功"
}

# 设置监控和告警
setup_monitoring() {
    log_info "设置CloudWatch监控和告警..."

    # 创建SNS主题用于告警通知
    local sns_topic_arn=$(aws sns create-topic \
        --name "livin-matrix-alerts" \
        --query "TopicArn" \
        --output text 2>/dev/null || echo "")

    if [ -n "$sns_topic_arn" ]; then
        aws sns add-tags \
            --resource-arn "$sns_topic_arn" \
            --tags Key=Project,Value=LiVin-Matrix

        log_success "SNS告警主题创建成功: $sns_topic_arn"
        echo "$sns_topic_arn" > "$PROJECT_ROOT/.aws-sns-topic-arn"
    fi

    # 创建成本告警
    create_cost_alarm

    log_success "监控和告警设置完成"
}

create_cost_alarm() {
    log_info "创建成本告警..."

    # 获取账户ID
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    local sns_topic_arn=$(cat "$PROJECT_ROOT/.aws-sns-topic-arn" 2>/dev/null || echo "")

    if [ -n "$sns_topic_arn" ]; then
        aws cloudwatch put-metric-alarm \
            --alarm-name "LiVin-Matrix-Monthly-Cost-Alarm" \
            --alarm-description "Alert when monthly cost exceeds $5" \
            --metric-name "EstimatedCharges" \
            --namespace "AWS/Billing" \
            --statistic "Maximum" \
            --period 86400 \
            --threshold 5.0 \
            --comparison-operator "GreaterThanThreshold" \
            --dimensions Name=Currency,Value=USD \
            --evaluation-periods 1 \
            --alarm-actions "$sns_topic_arn" \
            --tags Key=Project,Value=LiVin-Matrix

        log_success "成本告警创建成功"
    fi
}

# 验证部署
verify_deployment() {
    log_info "验证AWS基础设施部署..."

    local issues=()

    # 验证VPC
    local vpc_id=$(cat "$PROJECT_ROOT/.aws-vpc-id" 2>/dev/null || echo "")
    if [ -z "$vpc_id" ] || ! aws ec2 describe-vpcs --vpc-ids "$vpc_id" &>/dev/null; then
        issues+=("VPC未正确创建")
    fi

    # 验证EKS集群
    if ! aws eks describe-cluster --name "livin-matrix-cluster" &>/dev/null; then
        issues+=("EKS集群未正确创建")
    fi

    # 验证RDS实例
    if ! aws rds describe-db-instances --db-instance-identifier "livin-matrix-db" &>/dev/null; then
        issues+=("RDS实例未正确创建")
    fi

    # 验证kubectl连接
    if ! kubectl get nodes &>/dev/null; then
        issues+=("kubectl无法连接到EKS集群")
    fi

    if [ ${#issues[@]} -eq 0 ]; then
        log_success "所有基础设施组件验证通过"
        display_deployment_info
    else
        log_error "发现以下问题:"
        for issue in "${issues[@]}"; do
            log_error "  - $issue"
        done
        exit 1
    fi
}

# 显示部署信息
display_deployment_info() {
    log_info "AWS基础设施部署完成！"
    echo
    echo "=== 部署信息 ==="

    local vpc_id=$(cat "$PROJECT_ROOT/.aws-vpc-id" 2>/dev/null || echo "未找到")
    echo "VPC ID: $vpc_id"

    if aws eks describe-cluster --name "livin-matrix-cluster" &>/dev/null; then
        echo "EKS集群: livin-matrix-cluster (已创建)"
        echo "kubectl配置: 已完成"
    fi

    if aws rds describe-db-instances --db-instance-identifier "livin-matrix-db" &>/dev/null; then
        local db_endpoint=$(aws rds describe-db-instances \
            --db-instance-identifier "livin-matrix-db" \
            --query "DBInstances[0].Endpoint.Address" \
            --output text)
        echo "RDS端点: $db_endpoint"
    fi

    echo
    echo "=== 后续步骤 ==="
    echo "1. 运行 'kubectl get nodes' 验证EKS集群"
    echo "2. 部署应用程序到Kubernetes集群"
    echo "3. 配置Application Load Balancer"
    echo "4. 设置GitHub Pages前端部署"
    echo
    echo "重要提醒："
    echo "- 请定期检查AWS免费层使用情况"
    echo "- 监控月度成本，确保不超过预算"
    echo "- 及时删除不需要的资源以避免费用"
}

# 清理函数
cleanup_on_error() {
    log_error "脚本执行失败，正在清理临时文件..."
    rm -f "$PROJECT_ROOT"/.aws-*-id
}

# 主函数
main() {
    log_info "开始AWS基础设施部署..."

    # 设置错误处理
    trap cleanup_on_error ERR

    # 执行部署步骤
    check_prerequisites
    verify_aws_credentials
    check_free_tier_usage
    deploy_vpc_infrastructure
    deploy_eks_cluster
    deploy_rds_database
    setup_monitoring
    verify_deployment

    log_success "AWS基础设施部署完成！"
}

# 如果直接运行此脚本，则执行主函数
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
