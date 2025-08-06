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
if [ $# -lt 2 ]; then
    log_error "Usage: $0 <environment> <target_revision>"
    log_info "Example: $0 staging abc123def456"
    exit 1
fi

ENVIRONMENT=$1
TARGET_REVISION=$2

log_info "Rolling back database migrations in $ENVIRONMENT to revision $TARGET_REVISION"

# 设置命名空间
NAMESPACE="livin-matrix-$ENVIRONMENT"

# 检查kubectl是否可用
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl is not installed or not in PATH"
    exit 1
fi

# 获取后端pod
BACKEND_POD=$(kubectl get pods -n $NAMESPACE -l app=backend -o jsonpath="{.items[0].metadata.name}")

if [ -z "$BACKEND_POD" ]; then
    log_error "No backend pod found in namespace $NAMESPACE"
    exit 1
fi

log_info "Using backend pod: $BACKEND_POD"

# 备份当前数据库
log_info "Creating database backup before rollback..."
BACKUP_FILE="db_backup_$(date +%Y%m%d_%H%M%S).sql"

kubectl exec -n $NAMESPACE $BACKEND_POD -- pg_dump \
    -h postgres-service \
    -U postgres \
    -d livin_matrix_staging \
    > "deploy/backups/$BACKUP_FILE"

log_info "Database backup created: deploy/backups/$BACKUP_FILE"

# 显示当前迁移状态
log_info "Current migration status:"
kubectl exec -n $NAMESPACE $BACKEND_POD -- alembic current

# 显示迁移历史
log_info "Migration history:"
kubectl exec -n $NAMESPACE $BACKEND_POD -- alembic history

# 执行数据库回滚
log_warn "Rolling back database to revision $TARGET_REVISION..."
log_warn "This operation may cause data loss!"

read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Database rollback cancelled"
    exit 0
fi

# 执行回滚
if kubectl exec -n $NAMESPACE $BACKEND_POD -- alembic downgrade $TARGET_REVISION; then
    log_info "Database rollback completed successfully"

    # 验证回滚
    log_info "Current migration status after rollback:"
    kubectl exec -n $NAMESPACE $BACKEND_POD -- alembic current

    # 记录回滚操作
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] Database rollback completed for $ENVIRONMENT environment to revision $TARGET_REVISION" >> deploy/rollback.log

    log_info "Database rollback completed successfully!"
    log_info "Backup available at: deploy/backups/$BACKUP_FILE"
else
    log_error "Database rollback failed!"
    log_error "You may need to restore from backup: deploy/backups/$BACKUP_FILE"
    exit 1
fi
