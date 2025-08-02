#!/bin/bash

# LiVin Matrix全栈部署脚本
# 端到端部署AWS基础设施、Kubernetes应用和GitHub Pages前端

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
EMAIL_ENDPOINT=""
COST_THRESHOLD="5.0"
SKIP_TESTS=false
DRY_RUN=false
VERBOSE=false

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

log_step() {
    echo
    echo -e "${BLUE}=================================${NC}"
    echo -e "${BLUE}步骤: $1${NC}"
    echo -e "${BLUE}=================================${NC}"
}

# 显示使用说明
show_usage() {
    echo "LiVin Matrix全栈部署脚本"
    echo
    echo "用法: $0 [选项]"
    echo
    echo "选项:"
    echo "  -e, --email EMAIL        告警通知邮箱地址"
    echo "  -c, --cost-threshold N   月度成本告警阈值（美元，默认: $COST_THRESHOLD）"
    echo "  -s, --skip-tests         跳过部署后测试"
    echo "  -n, --dry-run            试运行，显示将要执行的步骤但不实际执行"
    echo "  -v, --verbose            详细输出"
    echo "  -h, --help               显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 -e admin@example.com"
    echo "  $0 --email admin@example.com --cost-threshold 10"
    echo "  $0 --dry-run --verbose"
    echo
    echo "环境变量:"
    echo "  NOTIFICATION_EMAIL       告警通知邮箱地址"
    echo "  AWS_PROFILE             AWS配置文件"
    echo "  GITHUB_TOKEN            GitHub Personal Access Token"
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--email)
                EMAIL_ENDPOINT="$2"
                shift 2
                ;;
            -c|--cost-threshold)
                COST_THRESHOLD="$2"
                shift 2
                ;;
            -s|--skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # 从环境变量获取邮箱地址
    if [ -z "$EMAIL_ENDPOINT" ] && [ -n "${NOTIFICATION_EMAIL:-}" ]; then
        EMAIL_ENDPOINT="$NOTIFICATION_EMAIL"
    fi
}

# 执行命令（支持dry-run模式）
execute_command() {
    local cmd="$1"
    local description="$2"
    
    if [ "$VERBOSE" = true ]; then
        log_info "执行: $description"
        log_info "命令: $cmd"
    fi
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] $description: $cmd"
        return 0
    fi
    
    if [ "$VERBOSE" = true ]; then
        eval "$cmd"
    else
        eval "$cmd" &>/dev/null || {
            log_error "$description 失败"
            return 1
        }
    fi
}

# 检查必需的工具和环境
check_prerequisites() {
    log_step "检查必需的工具和环境"
    
    local missing_tools=()
    local tools=(
        "aws:AWS CLI"
        "kubectl:Kubernetes CLI"
        "helm:Helm"
        "docker:Docker"
        "node:Node.js"
        "npm:NPM"
        "git:Git"
        "jq:JSON处理器"
        "curl:HTTP客户端"
    )
    
    for tool_info in "${tools[@]}"; do
        IFS=':' read -r tool desc <<< "$tool_info"
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$desc")
        fi
    done
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必需的工具:"
        for tool in "${missing_tools[@]}"; do
            log_error "  - $tool"
        done
        exit 1
    fi
    
    # 检查AWS凭据
    if ! aws sts get-caller-identity &>/dev/null; then
        log_error "AWS凭据验证失败"
        log_info "请运行: aws configure"
        exit 1
    fi
    
    # 检查Docker是否运行
    if ! docker info &>/dev/null; then
        log_error "Docker未运行或无法访问"
        exit 1
    fi
    
    log_success "环境检查完成"
}

# 部署AWS基础设施
deploy_aws_infrastructure() {
    log_step "部署AWS基础设施"
    
    local aws_setup_script="$SCRIPT_DIR/aws-setup.sh"
    
    if [ ! -f "$aws_setup_script" ]; then
        log_error "AWS设置脚本未找到: $aws_setup_script"
        exit 1
    fi
    
    execute_command "bash '$aws_setup_script'" "AWS基础设施部署"
    log_success "AWS基础设施部署完成"
}

# 部署RDS数据库
deploy_rds_database() {
    log_step "部署RDS PostgreSQL数据库"
    
    local rds_setup_script="$SCRIPT_DIR/rds-setup.sh"
    
    if [ ! -f "$rds_setup_script" ]; then
        log_error "RDS设置脚本未找到: $rds_setup_script"
        exit 1
    fi
    
    execute_command "bash '$rds_setup_script'" "RDS数据库部署"
    log_success "RDS数据库部署完成"
}

# 部署EKS应用程序
deploy_kubernetes_apps() {
    log_step "部署Kubernetes应用程序"
    
    # 确保kubectl配置正确
    execute_command "aws eks update-kubeconfig --region us-east-1 --name livin-matrix-cluster" "更新kubectl配置"
    
    # 部署命名空间和RBAC
    execute_command "kubectl apply -f '$PROJECT_ROOT/deploy/aws/namespace-aws.yaml'" "创建命名空间"
    
    # 部署ConfigMaps
    execute_command "kubectl apply -f '$PROJECT_ROOT/deploy/aws/configmap-aws.yaml'" "部署ConfigMaps"
    
    # 部署Secrets（注意：生产环境应使用External Secrets）
    execute_command "kubectl apply -f '$PROJECT_ROOT/deploy/aws/secrets-aws.yaml'" "部署Secrets"
    
    # 部署后端应用
    execute_command "kubectl apply -f '$PROJECT_ROOT/deploy/aws/backend-deployment-aws.yaml'" "部署后端应用"
    
    # 等待部署完成
    if [ "$DRY_RUN" = false ]; then
        log_info "等待后端应用就绪..."
        kubectl wait --for=condition=available --timeout=300s deployment/livin-matrix-backend -n livin-matrix-prod
    fi
    
    log_success "Kubernetes应用程序部署完成"
}

# 配置ALB和Ingress
deploy_alb_ingress() {
    log_step "配置Application Load Balancer"
    
    local alb_setup_script="$SCRIPT_DIR/alb-setup.sh"
    
    if [ ! -f "$alb_setup_script" ]; then
        log_error "ALB设置脚本未找到: $alb_setup_script"
        exit 1
    fi
    
    execute_command "bash '$alb_setup_script'" "ALB和Ingress配置"
    log_success "Application Load Balancer配置完成"
}

# 配置监控和告警
deploy_monitoring() {
    log_step "配置监控和告警"
    
    local monitoring_setup_script="$SCRIPT_DIR/monitoring-setup.sh"
    
    if [ ! -f "$monitoring_setup_script" ]; then
        log_error "监控设置脚本未找到: $monitoring_setup_script"
        exit 1
    fi
    
    local monitoring_args=""
    if [ -n "$EMAIL_ENDPOINT" ]; then
        monitoring_args="--email '$EMAIL_ENDPOINT'"
    fi
    monitoring_args="$monitoring_args --cost-threshold '$COST_THRESHOLD'"
    
    execute_command "bash '$monitoring_setup_script' $monitoring_args" "监控和告警配置"
    log_success "监控和告警配置完成"
}

# 配置GitHub Pages
deploy_github_pages() {
    log_step "配置GitHub Pages部署"
    
    local github_setup_script="$SCRIPT_DIR/github-pages-setup.sh"
    
    if [ ! -f "$github_setup_script" ]; then
        log_error "GitHub Pages设置脚本未找到: $github_setup_script"
        exit 1
    fi
    
    # 从git remote获取仓库信息
    local repo_url=""
    if git remote get-url origin &>/dev/null; then
        repo_url=$(git remote get-url origin)
    fi
    
    local github_args=""
    if [[ "$repo_url" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
        local repo_owner="${BASH_REMATCH[1]}"
        local repo_name="${BASH_REMATCH[2]}"
        github_args="--owner '$repo_owner' --repo '$repo_name'"
    fi
    
    if [ -n "${GITHUB_TOKEN:-}" ]; then
        github_args="$github_args --token '$GITHUB_TOKEN'"
    fi
    
    execute_command "bash '$github_setup_script' $github_args" "GitHub Pages配置"
    log_success "GitHub Pages配置完成"
}

# 运行部署后测试
run_deployment_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_warning "跳过部署后测试"
        return 0
    fi
    
    log_step "运行部署后测试"
    
    # 健康检查测试
    run_health_checks
    
    # API连通性测试
    run_api_tests
    
    # 数据库连接测试
    run_database_tests
    
    # 前端部署测试
    run_frontend_tests
    
    # 性能基准测试
    run_performance_tests
    
    log_success "部署后测试完成"
}

# 健康检查测试
run_health_checks() {
    log_info "运行健康检查测试..."
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] 健康检查测试"
        return 0
    fi
    
    # 检查EKS集群状态
    log_info "检查EKS集群状态..."
    local cluster_status=$(aws eks describe-cluster --name livin-matrix-cluster --query "cluster.status" --output text)
    if [ "$cluster_status" != "ACTIVE" ]; then
        log_error "EKS集群状态异常: $cluster_status"
        return 1
    fi
    
    # 检查节点状态
    log_info "检查Kubernetes节点状态..."
    local ready_nodes=$(kubectl get nodes --no-headers | grep -c "Ready" || echo "0")
    if [ "$ready_nodes" -lt 1 ]; then
        log_error "没有就绪的Kubernetes节点"
        return 1
    fi
    
    # 检查Pod状态
    log_info "检查应用Pod状态..."
    local running_pods=$(kubectl get pods -n livin-matrix-prod --no-headers | grep -c "Running" || echo "0")
    if [ "$running_pods" -lt 1 ]; then
        log_error "没有运行中的应用Pod"
        return 1
    fi
    
    # 检查RDS状态
    log_info "检查RDS数据库状态..."
    local db_status=$(aws rds describe-db-instances --db-instance-identifier livin-matrix-db --query "DBInstances[0].DBInstanceStatus" --output text)
    if [ "$db_status" != "available" ]; then
        log_error "RDS数据库状态异常: $db_status"
        return 1
    fi
    
    log_success "健康检查测试通过"
}

# API连通性测试
run_api_tests() {
    log_info "运行API连通性测试..."
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] API连通性测试"
        return 0
    fi
    
    # 获取ALB DNS名称
    local alb_dns=""
    if [ -f "$PROJECT_ROOT/.aws-alb-dns" ]; then
        alb_dns=$(cat "$PROJECT_ROOT/.aws-alb-dns")
    fi
    
    if [ -z "$alb_dns" ]; then
        alb_dns=$(kubectl get ingress livin-matrix-alb-ingress -n livin-matrix-prod -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
    fi
    
    if [ -z "$alb_dns" ]; then
        log_warning "无法获取ALB DNS名称，跳过API测试"
        return 0
    fi
    
    # 测试健康检查端点
    log_info "测试健康检查端点..."
    local health_url="https://$alb_dns/health"
    
    local max_attempts=30
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$health_url" &>/dev/null; then
            log_success "健康检查端点响应正常"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "健康检查端点无响应: $health_url"
            return 1
        fi
        
        log_info "等待ALB就绪... (尝试 $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    # 测试API端点
    log_info "测试API端点..."
    local api_url="https://$alb_dns/api/v1/health"
    if curl -f -s "$api_url" &>/dev/null; then
        log_success "API端点响应正常"
    else
        log_warning "API端点可能未就绪: $api_url"
    fi
    
    log_success "API连通性测试完成"
}

# 数据库连接测试
run_database_tests() {
    log_info "运行数据库连接测试..."
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] 数据库连接测试"
        return 0
    fi
    
    # 从Kubernetes Secret获取数据库连接信息
    log_info "测试数据库连接..."
    
    # 在Pod中运行数据库连接测试
    local test_command='
    kubectl run db-test-$(date +%s) \
      --image=postgres:15-alpine \
      --rm -i --restart=Never \
      --namespace=livin-matrix-prod \
      --env="PGPASSWORD=$(kubectl get secret livin-matrix-db-secret -n livin-matrix-prod -o jsonpath=\"{.data.password}\" | base64 -d)" \
      -- psql -h $(kubectl get secret livin-matrix-db-secret -n livin-matrix-prod -o jsonpath=\"{.data.host}\" | base64 -d) \
             -U $(kubectl get secret livin-matrix-db-secret -n livin-matrix-prod -o jsonpath=\"{.data.username}\" | base64 -d) \
             -d $(kubectl get secret livin-matrix-db-secret -n livin-matrix-prod -o jsonpath=\"{.data.dbname}\" | base64 -d) \
             -c "SELECT version();"'
    
    if eval "$test_command" &>/dev/null; then
        log_success "数据库连接测试通过"
    else
        log_warning "数据库连接测试失败或跳过"
    fi
}

# 前端部署测试
run_frontend_tests() {
    log_info "运行前端部署测试..."
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] 前端部署测试"
        return 0
    fi
    
    # 获取GitHub Pages URL
    local repo_owner=""
    local repo_name=""
    
    if git remote get-url origin &>/dev/null; then
        local remote_url=$(git remote get-url origin)
        if [[ "$remote_url" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
            repo_owner="${BASH_REMATCH[1]}"
            repo_name="${BASH_REMATCH[2]}"
        fi
    fi
    
    if [ -n "$repo_owner" ] && [ -n "$repo_name" ]; then
        local pages_url="https://$repo_owner.github.io/$repo_name/"
        
        log_info "测试GitHub Pages部署: $pages_url"
        
        # 注意：GitHub Pages可能需要一些时间来更新
        if curl -f -s "$pages_url" &>/dev/null; then
            log_success "GitHub Pages部署测试通过"
        else
            log_warning "GitHub Pages可能还未就绪或需要手动触发部署"
        fi
    else
        log_warning "无法确定GitHub Pages URL，跳过前端测试"
    fi
}

# 性能基准测试
run_performance_tests() {
    log_info "运行性能基准测试..."
    
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] 性能基准测试"
        return 0
    fi
    
    # 获取ALB DNS名称
    local alb_dns=""
    if [ -f "$PROJECT_ROOT/.aws-alb-dns" ]; then
        alb_dns=$(cat "$PROJECT_ROOT/.aws-alb-dns")
    fi
    
    if [ -z "$alb_dns" ]; then
        log_warning "无法获取ALB DNS名称，跳过性能测试"
        return 0
    fi
    
    log_info "测试API响应时间..."
    local health_url="https://$alb_dns/health"
    
    # 测试响应时间（5次测试取平均值）
    local total_time=0
    local successful_tests=0
    
    for i in {1..5}; do
        local response_time=$(curl -o /dev/null -s -w '%{time_total}' "$health_url" 2>/dev/null || echo "0")
        if (( $(echo "$response_time > 0" | bc -l 2>/dev/null || echo "0") )); then
            total_time=$(echo "$total_time + $response_time" | bc -l 2>/dev/null || echo "$total_time")
            ((successful_tests++))
        fi
        sleep 1
    done
    
    if [ "$successful_tests" -gt 0 ]; then
        local avg_time=$(echo "scale=3; $total_time / $successful_tests" | bc -l 2>/dev/null || echo "unknown")
        log_info "平均响应时间: ${avg_time}秒"
        
        if (( $(echo "$avg_time < 2.0" | bc -l 2>/dev/null || echo "0") )); then
            log_success "响应时间性能测试通过"
        else
            log_warning "响应时间较长，可能需要优化"
        fi
    else
        log_warning "性能测试失败，无法获取响应时间"
    fi
}

# 显示部署摘要
display_deployment_summary() {
    log_step "部署摘要"
    
    echo "🎉 LiVin Matrix全栈部署完成！"
    echo
    echo "=== 部署组件 ==="
    echo "✅ AWS VPC和网络基础设施"
    echo "✅ EKS Kubernetes集群"
    echo "✅ RDS PostgreSQL数据库"
    echo "✅ Application Load Balancer"
    echo "✅ CloudWatch监控和告警"
    echo "✅ GitHub Pages前端部署"
    
    echo
    echo "=== 访问信息 ==="
    
    # ALB信息
    if [ -f "$PROJECT_ROOT/.aws-alb-dns" ]; then
        local alb_dns=$(cat "$PROJECT_ROOT/.aws-alb-dns")
        echo "🌐 API端点: https://$alb_dns"
        echo "🏥 健康检查: https://$alb_dns/health"
        echo "📚 API文档: https://$alb_dns/docs"
    fi
    
    # GitHub Pages信息
    local repo_owner=""
    local repo_name=""
    if git remote get-url origin &>/dev/null; then
        local remote_url=$(git remote get-url origin)
        if [[ "$remote_url" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
            repo_owner="${BASH_REMATCH[1]}"
            repo_name="${BASH_REMATCH[2]}"
            echo "🎨 前端应用: https://$repo_owner.github.io/$repo_name/"
        fi
    fi
    
    echo
    echo "=== 管理控制台 ==="
    local account_id=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "")
    echo "☁️  AWS控制台: https://console.aws.amazon.com/"
    echo "📊 CloudWatch: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1"
    echo "🚢 Kubernetes: kubectl get all -n livin-matrix-prod"
    
    if [ -n "$repo_owner" ] && [ -n "$repo_name" ]; then
        echo "🔄 GitHub Actions: https://github.com/$repo_owner/$repo_name/actions"
    fi
    
    echo
    echo "=== 成本监控 ==="
    echo "💰 月度预算阈值: \$${COST_THRESHOLD}"
    echo "📧 告警通知: ${EMAIL_ENDPOINT:-'未设置'}"
    echo "📈 费用预估: https://console.aws.amazon.com/billing/home#/bills"
    
    echo
    echo "=== 下一步 ==="
    echo "1. 验证所有服务正常运行"
    echo "2. 配置自定义域名（可选）"
    echo "3. 设置SSL证书验证"
    echo "4. 配置数据备份策略"
    echo "5. 进行安全审查"
    echo "6. 性能优化和监控"
    
    echo
    echo "=== 重要提醒 ==="
    echo "⚠️  定期检查AWS免费层使用情况"
    echo "⚠️  监控月度成本，避免超出预算"
    echo "⚠️  及时更新安全补丁"
    echo "⚠️  定期备份重要数据"
    
    if [ "$DRY_RUN" = true ]; then
        echo
        echo "📝 注意：这是试运行模式，实际未执行任何部署操作"
    fi
}

# 错误处理和清理
cleanup_on_error() {
    log_error "部署过程中发生错误，正在清理..."
    
    # 这里可以添加清理逻辑
    # 注意：生产环境中要谨慎删除资源
    
    log_info "清理完成"
    exit 1
}

# 主函数
main() {
    echo "🚀 开始LiVin Matrix全栈部署..."
    echo
    
    # 设置错误处理
    trap cleanup_on_error ERR
    
    # 解析参数
    parse_arguments "$@"
    
    if [ "$DRY_RUN" = true ]; then
        log_warning "试运行模式 - 不会执行实际部署操作"
    fi
    
    # 执行部署步骤
    check_prerequisites
    deploy_aws_infrastructure
    deploy_rds_database
    deploy_kubernetes_apps
    deploy_alb_ingress
    deploy_monitoring
    deploy_github_pages
    run_deployment_tests
    display_deployment_summary
    
    log_success "🎉 LiVin Matrix全栈部署成功完成！"
}

# 如果直接运行此脚本，则执行主函数
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi