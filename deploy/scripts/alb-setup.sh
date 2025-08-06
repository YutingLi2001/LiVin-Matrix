#!/bin/bash

# Application Load Balancer设置脚本
# 用于配置AWS ALB和相关资源

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
CLUSTER_NAME="livin-matrix-cluster"
ALB_NAME="livin-matrix-alb"
CERTIFICATE_DOMAIN="api.livin-matrix.example.com"  # 替换为实际域名
LOGS_BUCKET_NAME="livin-matrix-alb-logs-$(date +%s)"

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

    if ! command -v kubectl &> /dev/null; then
        missing_tools+=("kubectl")
    fi

    if ! command -v helm &> /dev/null; then
        missing_tools+=("helm")
    fi

    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必需的工具: ${missing_tools[*]}"
        exit 1
    fi

    log_success "工具检查完成"
}

# 验证EKS集群连接
verify_eks_connection() {
    log_info "验证EKS集群连接..."

    if ! kubectl cluster-info &>/dev/null; then
        log_error "无法连接到EKS集群"
        log_info "请运行: aws eks update-kubeconfig --region us-east-1 --name $CLUSTER_NAME"
        exit 1
    fi

    local cluster_name=$(kubectl config current-context | grep -o 'livin-matrix-cluster' || echo "")
    if [ "$cluster_name" != "$CLUSTER_NAME" ]; then
        log_warning "当前kubectl上下文可能不是正确的集群"
    fi

    log_success "EKS集群连接验证成功"
}

# 安装AWS Load Balancer Controller
install_aws_load_balancer_controller() {
    log_info "安装AWS Load Balancer Controller..."

    # 检查是否已安装
    if kubectl get deployment -n kube-system aws-load-balancer-controller &>/dev/null; then
        log_info "AWS Load Balancer Controller已安装"
        return 0
    fi

    # 获取集群OIDC发行者URL
    local cluster_oidc=$(aws eks describe-cluster \
        --name "$CLUSTER_NAME" \
        --query "cluster.identity.oidc.issuer" \
        --output text | sed 's|https://||')

    # 获取AWS账户ID
    local account_id=$(aws sts get-caller-identity --query Account --output text)

    # 创建IAM策略（如果不存在）
    create_alb_iam_policy "$account_id"

    # 创建IAM角色和服务账户
    create_alb_service_account "$account_id" "$cluster_oidc"

    # 添加EKS Helm仓库
    helm repo add eks https://aws.github.io/eks-charts
    helm repo update

    # 安装AWS Load Balancer Controller
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName="$CLUSTER_NAME" \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller \
        --set region=us-east-1 \
        --set vpcId="$(cat "$PROJECT_ROOT/.aws-vpc-id")" \
        --set image.repository=602401143452.dkr.ecr.us-east-1.amazonaws.com/amazon/aws-load-balancer-controller

    # 等待部署完成
    kubectl wait --for=condition=available \
        --timeout=300s \
        deployment/aws-load-balancer-controller \
        -n kube-system

    log_success "AWS Load Balancer Controller安装完成"
}

# 创建ALB IAM策略
create_alb_iam_policy() {
    local account_id="$1"
    local policy_name="AWSLoadBalancerControllerIAMPolicy"

    log_info "创建ALB IAM策略..."

    # 检查策略是否已存在
    if aws iam get-policy --policy-arn "arn:aws:iam::$account_id:policy/$policy_name" &>/dev/null; then
        log_info "IAM策略已存在: $policy_name"
        return 0
    fi

    # 下载最新的IAM策略文档
    curl -o /tmp/iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.6.0/docs/install/iam_policy.json

    # 创建IAM策略
    aws iam create-policy \
        --policy-name "$policy_name" \
        --policy-document file:///tmp/iam_policy.json \
        --description "IAM policy for AWS Load Balancer Controller"

    # 清理临时文件
    rm -f /tmp/iam_policy.json

    log_success "IAM策略创建完成: $policy_name"
}

# 创建ALB服务账户和IAM角色
create_alb_service_account() {
    local account_id="$1"
    local cluster_oidc="$2"
    local role_name="AmazonEKSLoadBalancerControllerRole"
    local policy_arn="arn:aws:iam::$account_id:policy/AWSLoadBalancerControllerIAMPolicy"

    log_info "创建ALB服务账户和IAM角色..."

    # 检查角色是否已存在
    if aws iam get-role --role-name "$role_name" &>/dev/null; then
        log_info "IAM角色已存在: $role_name"
    else
        # 创建信任策略文档
        cat > /tmp/trust-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": "arn:aws:iam::$account_id:oidc-provider/$cluster_oidc"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "$cluster_oidc:sub": "system:serviceaccount:kube-system:aws-load-balancer-controller",
                    "$cluster_oidc:aud": "sts.amazonaws.com"
                }
            }
        }
    ]
}
EOF

        # 创建IAM角色
        aws iam create-role \
            --role-name "$role_name" \
            --assume-role-policy-document file:///tmp/trust-policy.json \
            --description "IAM role for AWS Load Balancer Controller"

        # 附加策略到角色
        aws iam attach-role-policy \
            --role-name "$role_name" \
            --policy-arn "$policy_arn"

        # 清理临时文件
        rm -f /tmp/trust-policy.json

        log_success "IAM角色创建完成: $role_name"
    fi

    # 创建Kubernetes服务账户
    if ! kubectl get serviceaccount aws-load-balancer-controller -n kube-system &>/dev/null; then
        kubectl create serviceaccount aws-load-balancer-controller -n kube-system

        # 添加角色注解
        kubectl annotate serviceaccount aws-load-balancer-controller \
            -n kube-system \
            eks.amazonaws.com/role-arn="arn:aws:iam::$account_id:role/$role_name"

        log_success "Kubernetes服务账户创建完成"
    else
        log_info "Kubernetes服务账户已存在"
    fi
}

# 创建SSL证书
create_ssl_certificate() {
    log_info "创建SSL证书..."

    # 检查证书是否已存在
    local existing_cert=$(aws acm list-certificates \
        --query "CertificateSummaryList[?DomainName=='$CERTIFICATE_DOMAIN'].CertificateArn" \
        --output text)

    if [ -n "$existing_cert" ]; then
        log_info "SSL证书已存在: $existing_cert"
        echo "$existing_cert" > "$PROJECT_ROOT/.aws-certificate-arn"
        return 0
    fi

    # 请求新的SSL证书
    log_info "请求新的SSL证书: $CERTIFICATE_DOMAIN"
    local cert_arn=$(aws acm request-certificate \
        --domain-name "$CERTIFICATE_DOMAIN" \
        --subject-alternative-names "*.$(echo "$CERTIFICATE_DOMAIN" | sed 's/^[^.]*\.//')" \
        --validation-method DNS \
        --query "CertificateArn" \
        --output text)

    echo "$cert_arn" > "$PROJECT_ROOT/.aws-certificate-arn"

    log_warning "SSL证书已请求，但需要DNS验证"
    log_info "证书ARN: $cert_arn"
    log_info "请在DNS提供商处添加验证记录"

    # 显示DNS验证记录
    show_dns_validation_records "$cert_arn"

    log_info "等待SSL证书验证完成..."
    aws acm wait certificate-validated --certificate-arn "$cert_arn" --timeout 300 || {
        log_warning "SSL证书验证超时，请手动验证DNS记录"
        log_info "可以稍后使用以下命令检查状态:"
        log_info "aws acm describe-certificate --certificate-arn $cert_arn"
    }

    log_success "SSL证书配置完成"
}

# 显示DNS验证记录
show_dns_validation_records() {
    local cert_arn="$1"

    log_info "获取DNS验证记录..."

    # 等待DNS验证记录生成
    sleep 10

    local validation_records=$(aws acm describe-certificate \
        --certificate-arn "$cert_arn" \
        --query "Certificate.DomainValidationOptions" \
        --output json)

    echo
    echo "=== DNS验证记录 ==="
    echo "$validation_records" | jq -r '.[] | "域名: \(.DomainName)\n类型: \(.ResourceRecord.Type)\n名称: \(.ResourceRecord.Name)\n值: \(.ResourceRecord.Value)\n"'
    echo
}

# 创建S3存储桶用于ALB访问日志
create_alb_logs_bucket() {
    log_info "创建ALB访问日志存储桶..."

    # 检查存储桶是否已存在
    if aws s3 ls "s3://$LOGS_BUCKET_NAME" &>/dev/null; then
        log_info "存储桶已存在: $LOGS_BUCKET_NAME"
        return 0
    fi

    # 创建S3存储桶
    aws s3 mb "s3://$LOGS_BUCKET_NAME" --region us-east-1

    # 设置存储桶策略以允许ALB写入日志
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    local elb_account_id="127311923021"  # us-east-1的ELB服务账户ID

    cat > /tmp/bucket-policy.json <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSLogDeliveryWrite",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::$elb_account_id:root"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::$LOGS_BUCKET_NAME/alb-logs/AWSLogs/$account_id/*"
        },
        {
            "Sid": "AWSLogDeliveryAclCheck",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::$elb_account_id:root"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::$LOGS_BUCKET_NAME"
        }
    ]
}
EOF

    # 应用存储桶策略
    aws s3api put-bucket-policy \
        --bucket "$LOGS_BUCKET_NAME" \
        --policy file:///tmp/bucket-policy.json

    # 设置生命周期策略（30天后删除日志）
    cat > /tmp/lifecycle-policy.json <<EOF
{
    "Rules": [
        {
            "ID": "DeleteOldLogs",
            "Status": "Enabled",
            "Expiration": {
                "Days": 30
            },
            "Filter": {
                "Prefix": "alb-logs/"
            }
        }
    ]
}
EOF

    aws s3api put-bucket-lifecycle-configuration \
        --bucket "$LOGS_BUCKET_NAME" \
        --lifecycle-configuration file:///tmp/lifecycle-policy.json

    # 启用公共访问阻止
    aws s3api put-public-access-block \
        --bucket "$LOGS_BUCKET_NAME" \
        --public-access-block-configuration \
            BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

    # 清理临时文件
    rm -f /tmp/bucket-policy.json /tmp/lifecycle-policy.json

    echo "$LOGS_BUCKET_NAME" > "$PROJECT_ROOT/.aws-alb-logs-bucket"

    log_success "ALB访问日志存储桶创建完成: $LOGS_BUCKET_NAME"
}

# 更新Ingress配置文件
update_ingress_config() {
    log_info "更新Ingress配置文件..."

    local cert_arn=$(cat "$PROJECT_ROOT/.aws-certificate-arn" 2>/dev/null || echo "")
    local vpc_id=$(cat "$PROJECT_ROOT/.aws-vpc-id" 2>/dev/null || echo "")
    local public_subnet_1a=$(cat "$PROJECT_ROOT/.aws-subnet-public-1a-id" 2>/dev/null || echo "")
    local public_subnet_1b=$(cat "$PROJECT_ROOT/.aws-subnet-public-1b-id" 2>/dev/null || echo "")
    local alb_sg_id=$(cat "$PROJECT_ROOT/.aws-sg-alb-id" 2>/dev/null || echo "")
    local account_id=$(aws sts get-caller-identity --query Account --output text)

    # 更新Ingress配置文件中的占位符
    sed -i.bak \
        -e "s/ACCOUNT_ID/$account_id/g" \
        -e "s/CERTIFICATE_ID/${cert_arn##*/}/g" \
        -e "s/arn:aws:acm:us-east-1:ACCOUNT_ID:certificate\/CERTIFICATE_ID/$cert_arn/g" \
        -e "s/subnet-12345678,subnet-87654321/$public_subnet_1a,$public_subnet_1b/g" \
        -e "s/sg-12345678/$alb_sg_id/g" \
        -e "s/livin-matrix-alb-logs/$LOGS_BUCKET_NAME/g" \
        "$PROJECT_ROOT/deploy/aws/ingress-aws.yaml"

    log_success "Ingress配置文件更新完成"
}

# 部署应用程序和Ingress
deploy_application() {
    log_info "部署应用程序和Ingress..."

    # 创建命名空间（如果不存在）
    kubectl apply -f "$PROJECT_ROOT/deploy/aws/namespace-aws.yaml"

    # 部署ConfigMaps和Secrets
    kubectl apply -f "$PROJECT_ROOT/deploy/aws/configmap-aws.yaml"

    # 注意：生产环境应使用External Secrets Operator
    # 这里使用本地secrets仅用于演示
    kubectl apply -f "$PROJECT_ROOT/deploy/aws/secrets-aws.yaml"

    # 部署后端应用
    kubectl apply -f "$PROJECT_ROOT/deploy/aws/backend-deployment-aws.yaml"

    # 等待后端应用就绪
    kubectl wait --for=condition=available \
        --timeout=300s \
        deployment/livin-matrix-backend \
        -n livin-matrix-prod

    # 部署Ingress
    kubectl apply -f "$PROJECT_ROOT/deploy/aws/ingress-aws.yaml"

    log_success "应用程序和Ingress部署完成"
}

# 等待ALB创建完成
wait_for_alb() {
    log_info "等待ALB创建完成..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        local alb_dns=$(kubectl get ingress livin-matrix-alb-ingress \
            -n livin-matrix-prod \
            -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")

        if [ -n "$alb_dns" ]; then
            log_success "ALB创建完成"
            log_info "ALB DNS名称: $alb_dns"
            echo "$alb_dns" > "$PROJECT_ROOT/.aws-alb-dns"
            return 0
        fi

        log_info "等待ALB创建... (尝试 $attempt/$max_attempts)"
        sleep 30
        ((attempt++))
    done

    log_error "ALB创建超时"
    exit 1
}

# 配置DNS记录（如果有Route53托管区域）
configure_dns_records() {
    log_info "配置DNS记录..."

    local alb_dns=$(cat "$PROJECT_ROOT/.aws-alb-dns" 2>/dev/null || echo "")
    if [ -z "$alb_dns" ]; then
        log_warning "ALB DNS名称未找到，跳过DNS配置"
        return 0
    fi

    # 尝试查找托管区域
    local domain_name=$(echo "$CERTIFICATE_DOMAIN" | sed 's/^[^.]*\.//')
    local hosted_zone_id=$(aws route53 list-hosted-zones-by-name \
        --dns-name "$domain_name" \
        --query "HostedZones[0].Id" \
        --output text 2>/dev/null || echo "None")

    if [ "$hosted_zone_id" = "None" ]; then
        log_warning "未找到Route53托管区域，请手动配置DNS记录"
        log_info "请将以下域名指向ALB:"
        log_info "  $CERTIFICATE_DOMAIN -> $alb_dns"
        return 0
    fi

    # 创建DNS记录
    log_info "在Route53中创建DNS记录..."

    cat > /tmp/dns-record.json <<EOF
{
    "Changes": [
        {
            "Action": "UPSERT",
            "ResourceRecordSet": {
                "Name": "$CERTIFICATE_DOMAIN",
                "Type": "A",
                "AliasTarget": {
                    "DNSName": "$alb_dns",
                    "EvaluateTargetHealth": true,
                    "HostedZoneId": "Z35SXDOTRQ7X7K"
                }
            }
        }
    ]
}
EOF

    aws route53 change-resource-record-sets \
        --hosted-zone-id "${hosted_zone_id##*/}" \
        --change-batch file:///tmp/dns-record.json

    rm -f /tmp/dns-record.json

    log_success "DNS记录配置完成"
}

# 验证ALB部署
verify_alb_deployment() {
    log_info "验证ALB部署..."

    local issues=()

    # 检查AWS Load Balancer Controller
    if ! kubectl get deployment aws-load-balancer-controller -n kube-system &>/dev/null; then
        issues+=("AWS Load Balancer Controller未安装")
    fi

    # 检查Ingress资源
    if ! kubectl get ingress livin-matrix-alb-ingress -n livin-matrix-prod &>/dev/null; then
        issues+=("Ingress资源未创建")
    fi

    # 检查ALB是否创建
    local alb_dns=$(cat "$PROJECT_ROOT/.aws-alb-dns" 2>/dev/null || echo "")
    if [ -z "$alb_dns" ]; then
        issues+=("ALB未创建或DNS名称未获取")
    fi

    # 检查SSL证书状态
    local cert_arn=$(cat "$PROJECT_ROOT/.aws-certificate-arn" 2>/dev/null || echo "")
    if [ -n "$cert_arn" ]; then
        local cert_status=$(aws acm describe-certificate \
            --certificate-arn "$cert_arn" \
            --query "Certificate.Status" \
            --output text 2>/dev/null || echo "UNKNOWN")

        if [ "$cert_status" != "ISSUED" ]; then
            issues+=("SSL证书状态异常: $cert_status")
        fi
    else
        issues+=("SSL证书ARN未找到")
    fi

    if [ ${#issues[@]} -eq 0 ]; then
        log_success "ALB部署验证通过"
        display_alb_info
    else
        log_error "发现以下问题:"
        for issue in "${issues[@]}"; do
            log_error "  - $issue"
        done
        exit 1
    fi
}

# 显示ALB部署信息
display_alb_info() {
    log_info "Application Load Balancer部署完成！"
    echo
    echo "=== ALB信息 ==="

    local alb_dns=$(cat "$PROJECT_ROOT/.aws-alb-dns" 2>/dev/null || echo "未获取")
    local cert_arn=$(cat "$PROJECT_ROOT/.aws-certificate-arn" 2>/dev/null || echo "未创建")
    local logs_bucket=$(cat "$PROJECT_ROOT/.aws-alb-logs-bucket" 2>/dev/null || echo "未创建")

    echo "ALB DNS名称: $alb_dns"
    echo "SSL证书ARN: $cert_arn"
    echo "访问日志存储桶: $logs_bucket"
    echo "目标域名: $CERTIFICATE_DOMAIN"

    echo
    echo "=== 访问URL ==="
    echo "API端点: https://$CERTIFICATE_DOMAIN/api"
    echo "健康检查: https://$CERTIFICATE_DOMAIN/health"
    echo "API文档: https://$CERTIFICATE_DOMAIN/docs"
    echo "前端重定向: https://$CERTIFICATE_DOMAIN/"

    echo
    echo "=== 后续步骤 ==="
    echo "1. 完成SSL证书的DNS验证（如果尚未完成）"
    echo "2. 配置DNS记录指向ALB"
    echo "3. 测试API端点的连通性"
    echo "4. 监控ALB的健康检查状态"
    echo "5. 配置CloudWatch告警"

    echo
    echo "=== 测试命令 ==="
    echo "curl -f https://$CERTIFICATE_DOMAIN/health"
    echo "curl -f https://$CERTIFICATE_DOMAIN/api/v1/health"
    echo "kubectl get ingress -n livin-matrix-prod"
    echo "kubectl describe ingress livin-matrix-alb-ingress -n livin-matrix-prod"
}

# 清理函数
cleanup_on_error() {
    log_error "ALB设置失败，正在清理临时文件..."
    rm -f /tmp/iam_policy.json /tmp/trust-policy.json
    rm -f /tmp/bucket-policy.json /tmp/lifecycle-policy.json
    rm -f /tmp/dns-record.json
}

# 主函数
main() {
    log_info "开始Application Load Balancer设置..."

    # 设置错误处理
    trap cleanup_on_error ERR

    # 执行设置步骤
    check_prerequisites
    verify_eks_connection
    install_aws_load_balancer_controller
    create_ssl_certificate
    create_alb_logs_bucket
    update_ingress_config
    deploy_application
    wait_for_alb
    configure_dns_records
    verify_alb_deployment

    log_success "Application Load Balancer设置完成！"
}

# 如果直接运行此脚本，则执行主函数
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
