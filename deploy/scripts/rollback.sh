#!/bin/bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查参数
if [ $# -lt 1 ]; then
    log_error "Usage: $0 <environment> [revision]"
    log_info "Example: $0 staging 2"
    log_info "If revision is not specified, rollback to previous version"
    exit 1
fi

ENVIRONMENT=$1
REVISION=${2:-""}

log_info "Rolling back $ENVIRONMENT environment"

# 设置命名空间
NAMESPACE="livin-matrix-$ENVIRONMENT"

# 检查kubectl是否可用
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl is not installed or not in PATH"
    exit 1
fi

# 检查集群连接
if ! kubectl cluster-info &> /dev/null; then
    log_error "Cannot connect to Kubernetes cluster"
    exit 1
fi

# 检查命名空间是否存在
if ! kubectl get namespace $NAMESPACE > /dev/null 2>&1; then
    log_error "Namespace $NAMESPACE does not exist"
    exit 1
fi

# 显示当前部署状态
log_info "Current deployment status:"
kubectl get deployments -n $NAMESPACE

# 显示rollout历史
log_info "Backend deployment history:"
kubectl rollout history deployment/backend -n $NAMESPACE

log_info "Frontend deployment history:"
kubectl rollout history deployment/frontend -n $NAMESPACE

# 执行回滚
if [ -n "$REVISION" ]; then
    log_info "Rolling back to revision $REVISION..."
    kubectl rollout undo deployment/backend --to-revision=$REVISION -n $NAMESPACE
    kubectl rollout undo deployment/frontend --to-revision=$REVISION -n $NAMESPACE
else
    log_info "Rolling back to previous version..."
    kubectl rollout undo deployment/backend -n $NAMESPACE
    kubectl rollout undo deployment/frontend -n $NAMESPACE
fi

# 等待回滚完成
log_info "Waiting for rollback to complete..."
kubectl rollout status deployment/backend -n $NAMESPACE --timeout=300s
kubectl rollout status deployment/frontend -n $NAMESPACE --timeout=300s

# 运行健康检查
log_info "Running post-rollback health checks..."

# 等待pods就绪
sleep 10

# 检查后端健康状态
log_info "Checking backend health..."
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=backend -o jsonpath="{.items[0].metadata.name}")
BACKEND_HEALTHY=false

for i in {1..30}; do
    if kubectl exec -n $NAMESPACE $BACKEND_POD -- curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        log_info "Backend health check passed"
        BACKEND_HEALTHY=true
        break
    fi
    log_info "Backend health check attempt $i/30 failed, retrying in 10s..."
    sleep 10
done

if [ "$BACKEND_HEALTHY" = false ]; then
    log_error "Backend health check failed after rollback"
    log_error "Rolling back again to a known good state..."
    kubectl rollout undo deployment/backend -n $NAMESPACE
    exit 1
fi

# 检查前端健康状态
log_info "Checking frontend health..."
FRONTEND_POD=$(kubectl get pods -n $NAMESPACE -l app=frontend -o jsonpath="{.items[0].metadata.name}")
FRONTEND_HEALTHY=false

for i in {1..30}; do
    if kubectl exec -n $NAMESPACE $FRONTEND_POD -- curl -sf http://localhost/health > /dev/null 2>&1; then
        log_info "Frontend health check passed"
        FRONTEND_HEALTHY=true
        break
    fi
    log_info "Frontend health check attempt $i/30 failed, retrying in 10s..."
    sleep 10
done

if [ "$FRONTEND_HEALTHY" = false ]; then
    log_error "Frontend health check failed after rollback"
    log_error "Rolling back again to a known good state..."
    kubectl rollout undo deployment/frontend -n $NAMESPACE
    exit 1
fi

# 显示最新部署状态
log_info "Rollback completed successfully!"
log_info "Current deployment status:"
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

# 记录回滚操作
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Rollback completed for $ENVIRONMENT environment" >> deploy/rollback.log

log_info "Rollback to $ENVIRONMENT completed successfully!"
log_warn "Please verify application functionality manually"