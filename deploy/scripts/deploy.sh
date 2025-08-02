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
    log_error "Usage: $0 <environment> [image_tag]"
    log_info "Example: $0 staging latest"
    exit 1
fi

ENVIRONMENT=$1
IMAGE_TAG=${2:-latest}

log_info "Deploying to $ENVIRONMENT environment with image tag: $IMAGE_TAG"

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

# 创建命名空间(如果不存在)
log_info "Creating namespace if not exists..."
kubectl apply -f deploy/kubernetes/namespace.yaml

# 等待命名空间创建
sleep 2

# 部署配置
log_info "Applying configuration..."
kubectl apply -f deploy/kubernetes/configmap.yaml
kubectl apply -f deploy/kubernetes/secret.yaml

# 部署数据库
log_info "Deploying PostgreSQL..."
kubectl apply -f deploy/kubernetes/postgres-deployment.yaml

# 等待数据库就绪
log_info "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s

# 更新镜像标签
log_info "Updating image tags to $IMAGE_TAG..."
kubectl set image deployment/backend backend=backend:$IMAGE_TAG -n $NAMESPACE
kubectl set image deployment/frontend frontend=frontend:$IMAGE_TAG -n $NAMESPACE

# 部署后端
log_info "Deploying backend..."
kubectl apply -f deploy/kubernetes/backend-deployment.yaml

# 部署前端
log_info "Deploying frontend..."
kubectl apply -f deploy/kubernetes/frontend-deployment.yaml

# 部署Ingress
log_info "Deploying ingress..."
kubectl apply -f deploy/kubernetes/ingress.yaml

# 等待部署完成
log_info "Waiting for deployments to be ready..."
kubectl rollout status deployment/backend -n $NAMESPACE --timeout=300s
kubectl rollout status deployment/frontend -n $NAMESPACE --timeout=300s

# 运行健康检查
log_info "Running health checks..."

# 检查后端健康状态
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=backend -o jsonpath="{.items[0].metadata.name}")
if kubectl exec -n $NAMESPACE $BACKEND_POD -- curl -sf http://localhost:8000/health > /dev/null; then
    log_info "Backend health check passed"
else
    log_error "Backend health check failed"
    exit 1
fi

# 检查前端健康状态
FRONTEND_POD=$(kubectl get pods -n $NAMESPACE -l app=frontend -o jsonpath="{.items[0].metadata.name}")
if kubectl exec -n $NAMESPACE $FRONTEND_POD -- curl -sf http://localhost/health > /dev/null; then
    log_info "Frontend health check passed"
else
    log_error "Frontend health check failed"
    exit 1
fi

# 显示部署状态
log_info "Deployment completed successfully!"
log_info "Getting service information..."

kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

log_info "Deployment to $ENVIRONMENT completed successfully with image tag: $IMAGE_TAG"