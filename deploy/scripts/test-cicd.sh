#!/bin/bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

# 测试计数器
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"

    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    log_test "Running test: $test_name"

    if eval "$test_command"; then
        log_info "✅ PASSED: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "❌ FAILED: $test_name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# 检查必要工具
check_prerequisites() {
    log_info "Checking prerequisites..."

    run_test "Docker is installed" "command -v docker >/dev/null 2>&1"
    run_test "Docker daemon is running" "docker info >/dev/null 2>&1"
    run_test "Node.js is installed" "command -v node >/dev/null 2>&1"
    run_test "Python is installed" "command -v python3 >/dev/null 2>&1"
    run_test "npm is available" "command -v npm >/dev/null 2>&1"
    run_test "pip is available" "command -v pip >/dev/null 2>&1"
}

# 测试前端构建
test_frontend_build() {
    log_info "Testing frontend build process..."

    cd frontend

    run_test "Frontend dependencies install" "npm ci"
    run_test "Frontend linting" "npm run lint"
    run_test "Frontend type checking" "npm run typecheck"
    run_test "Frontend tests" "npm run test:coverage"
    run_test "Frontend build" "npm run build"

    cd ..
}

# 测试后端构建
test_backend_build() {
    log_info "Testing backend build process..."

    cd backend

    run_test "Backend dependencies install" "pip install -r requirements.txt && pip install -r requirements-test.txt"
    run_test "Backend code formatting check" "black --check . --diff"
    run_test "Backend linting" "flake8 ."
    run_test "Backend tests" "python -m pytest --cov=app --cov-report=term-missing"

    cd ..
}

# 测试Docker镜像构建
test_docker_build() {
    log_info "Testing Docker image builds..."

    run_test "Frontend Docker build" "docker build -f deploy/docker/frontend.Dockerfile -t test-frontend:latest ."
    run_test "Backend Docker build" "docker build -f deploy/docker/backend.Dockerfile -t test-backend:latest ."

    # 测试镜像运行
    log_info "Testing Docker image execution..."

    # 测试前端镜像
    run_test "Frontend container starts" "
        docker run -d --name test-frontend-container -p 3001:80 test-frontend:latest &&
        sleep 5 &&
        curl -sf http://localhost:3001/health >/dev/null &&
        docker stop test-frontend-container &&
        docker rm test-frontend-container
    "

    # 测试后端镜像
    run_test "Backend container starts" "
        docker run -d --name test-backend-container -p 8001:8000 \
            -e DATABASE_URL=sqlite:///./test.db \
            test-backend:latest &&
        sleep 10 &&
        curl -sf http://localhost:8001/health >/dev/null &&
        docker stop test-backend-container &&
        docker rm test-backend-container
    "
}

# 测试GitHub Actions配置
test_github_actions() {
    log_info "Testing GitHub Actions configuration..."

    run_test "Frontend workflow file exists" "test -f .github/workflows/frontend-ci.yml"
    run_test "Backend workflow file exists" "test -f .github/workflows/backend-ci.yml"

    # 验证workflow文件语法
    if command -v act >/dev/null 2>&1; then
        run_test "Frontend workflow syntax" "act --list -W .github/workflows/frontend-ci.yml >/dev/null"
        run_test "Backend workflow syntax" "act --list -W .github/workflows/backend-ci.yml >/dev/null"
    else
        log_warn "act is not installed, skipping workflow syntax validation"
    fi
}

# 测试Kubernetes配置
test_kubernetes_config() {
    log_info "Testing Kubernetes configuration..."

    run_test "Namespace config exists" "test -f deploy/kubernetes/namespace.yaml"
    run_test "ConfigMap config exists" "test -f deploy/kubernetes/configmap.yaml"
    run_test "Secret config exists" "test -f deploy/kubernetes/secret.yaml"
    run_test "PostgreSQL deployment exists" "test -f deploy/kubernetes/postgres-deployment.yaml"
    run_test "Backend deployment exists" "test -f deploy/kubernetes/backend-deployment.yaml"
    run_test "Frontend deployment exists" "test -f deploy/kubernetes/frontend-deployment.yaml"
    run_test "Ingress config exists" "test -f deploy/kubernetes/ingress.yaml"

    # 验证YAML语法
    if command -v kubectl >/dev/null 2>&1; then
        run_test "Kubernetes configs are valid" "
            kubectl apply --dry-run=client -f deploy/kubernetes/ >/dev/null 2>&1
        "
    else
        log_warn "kubectl is not installed, skipping Kubernetes config validation"
    fi
}

# 测试部署脚本
test_deployment_scripts() {
    log_info "Testing deployment scripts..."

    run_test "Deploy script exists and is executable" "test -x deploy/scripts/deploy.sh"
    run_test "Rollback script exists and is executable" "test -x deploy/scripts/rollback.sh"
    run_test "DB rollback script exists and is executable" "test -x deploy/scripts/db-rollback.sh"

    # 测试脚本语法
    run_test "Deploy script syntax" "bash -n deploy/scripts/deploy.sh"
    run_test "Rollback script syntax" "bash -n deploy/scripts/rollback.sh"
    run_test "DB rollback script syntax" "bash -n deploy/scripts/db-rollback.sh"
}

# 性能测试
test_performance() {
    log_info "Testing CI/CD performance requirements..."

    # 前端构建时间测试
    log_test "Frontend build time test"
    cd frontend
    START_TIME=$(date +%s)
    if npm run build >/dev/null 2>&1; then
        END_TIME=$(date +%s)
        BUILD_TIME=$((END_TIME - START_TIME))
        if [ $BUILD_TIME -lt 300 ]; then  # 5分钟
            log_info "✅ PASSED: Frontend build completed in ${BUILD_TIME}s (requirement: <300s)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            log_error "❌ FAILED: Frontend build took ${BUILD_TIME}s (requirement: <300s)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    else
        log_error "❌ FAILED: Frontend build failed"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    cd ..
}

# 清理函数
cleanup() {
    log_info "Cleaning up test artifacts..."

    # 停止并删除测试容器
    docker stop test-frontend-container test-backend-container 2>/dev/null || true
    docker rm test-frontend-container test-backend-container 2>/dev/null || true

    # 删除测试镜像
    docker rmi test-frontend:latest test-backend:latest 2>/dev/null || true

    log_info "Cleanup completed"
}

# 主测试流程
main() {
    log_info "Starting CI/CD Integration Tests"
    log_info "=================================="

    # 设置清理陷阱
    trap cleanup EXIT

    # 运行测试套件
    check_prerequisites
    test_github_actions
    test_kubernetes_config
    test_deployment_scripts
    test_frontend_build
    test_backend_build
    test_docker_build
    test_performance

    # 显示测试结果
    log_info "=================================="
    log_info "Test Results Summary"
    log_info "=================================="
    log_info "Total Tests: $TESTS_TOTAL"
    log_info "Passed: $TESTS_PASSED"
    log_info "Failed: $TESTS_FAILED"

    if [ $TESTS_FAILED -eq 0 ]; then
        log_info "🎉 All tests passed! CI/CD pipeline is ready."
        exit 0
    else
        log_error "💥 $TESTS_FAILED test(s) failed! Please fix the issues before proceeding."
        exit 1
    fi
}

# 运行主函数
main "$@"
