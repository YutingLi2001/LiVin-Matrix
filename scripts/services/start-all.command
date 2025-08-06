#!/bin/bash

# LIVIN-MATRIX 全服务启动脚本
# 双击此文件即可启动所有服务 (PostgreSQL, Redis, 后端API, 前端)

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

# 设置终端标题
echo -n -e "\033]0;LIVIN-MATRIX 全服务启动\007"

# 打印启动信息
echo "==============================================="
echo "         LIVIN-MATRIX 全服务启动"
echo "==============================================="
echo ""

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 检查Docker是否运行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker 未运行，请先启动 Docker Desktop"
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi
}

# 检查端口占用
check_port_conflict() {
    local port=$1
    local service=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  端口 $port 已被占用 ($service)，正在尝试清理..."
        # 尝试停止可能的冲突服务
        case $port in
            5432) docker stop livin-matrix-postgres 2>/dev/null || true ;;
            6379) docker stop livin-matrix-redis 2>/dev/null || true ;;
            8000) docker stop livin-matrix-backend 2>/dev/null || true ;;
            3000|5173)
                docker stop livin-matrix-frontend 2>/dev/null || true
                pkill -f "vite.*$port" 2>/dev/null || true
                ;;
        esac
        sleep 2
    fi
}

# 等待服务健康检查
wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=1

    echo "🔄 等待 $service 服务启动..."

    while [ $attempt -le $max_attempts ]; do
        # 使用docker-compose ps检查服务状态
        if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps --services --filter "status=running" | grep -q "$service"; then
            echo "✅ $service 服务已启动"
            return 0
        fi

        echo "   尝试 $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "❌ $service 服务启动超时"
    return 1
}

# 显示服务状态
show_service_status() {
    echo ""
    echo "📊 服务状态："
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps
    echo ""
}

# 检查Secrets文件
check_secrets_files() {
    echo "🔐 检查Secrets文件配置..."

    local required_secrets=("POSTGRES_PASSWORD" "JWT_SECRET_KEY" "GITHUB_CLIENT_SECRET"
                           "SESSION_SECRET_KEY" "RESEND_API_KEY" "GITHUB_CLIENT_ID" "GITHUB_REDIRECT_URI")
    local missing_secrets=()

    for secret in "${required_secrets[@]}"; do
        if [ ! -f "secrets/$secret" ]; then
            missing_secrets+=("$secret")
        fi
    done

    if [ ${#missing_secrets[@]} -gt 0 ]; then
        echo "❌ 缺少必要的Secrets文件:"
        for secret in "${missing_secrets[@]}"; do
            echo "   - secrets/$secret"
        done
        echo ""
        echo "请先运行密钥初始化脚本创建所需的Secrets文件"
        echo "或参考: docs/stories/epic1.5/1.5.4.1.docker-secrets-management.md"
        echo ""
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi

    echo "✅ 所有Secrets文件配置完成"
}

# 检查必要的配置文件
check_configuration() {
    if [ ! -f "docker-compose.yml" ]; then
        echo "❌ 缺少 docker-compose.yml 文件"
        exit 1
    fi

    if [ ! -f "docker-compose.secrets.yml" ]; then
        echo "❌ 缺少 docker-compose.secrets.yml 文件"
        echo "请确保已经完成 Docker Secrets 配置"
        echo "参考: docs/stories/epic1.5/1.5.4.1.docker-secrets-management.md"
        echo ""
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi

    echo "✅ 配置文件检查完成"
}

# 主启动流程
main() {
    echo "🔍 检查系统环境..."
    check_docker
    check_secrets_files
    check_configuration

    echo "🔍 检查端口冲突..."
    check_port_conflict 5432 "PostgreSQL"
    check_port_conflict 6379 "Redis"
    check_port_conflict 8000 "Backend API"
    check_port_conflict 3000 "Frontend"

    echo ""
    echo "🚀 启动所有服务..."

    # 使用Docker Compose启动所有服务（测试模式）
    if ! docker-compose -f docker-compose.yml -f docker-compose.secrets.yml up -d; then
        echo "❌ 服务启动失败"
        echo "请检查 Docker 配置和网络连接"
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi

    echo ""
    echo "⏳ 等待服务就绪..."

    # 等待数据库服务
    if ! wait_for_service "postgres"; then
        echo "数据库启动失败，查看日志: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs postgres"
        exit 1
    fi

    # 等待Redis服务
    if ! wait_for_service "redis"; then
        echo "Redis启动失败，查看日志: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs redis"
        exit 1
    fi

    # 等待后端服务
    if ! wait_for_service "backend"; then
        echo "后端服务启动失败，查看日志: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs backend"
        exit 1
    fi

    show_service_status

    echo "🎉 所有服务启动成功！"
    echo ""
    echo "📱 访问地址:"
    echo "   • 前端应用: http://localhost:3000"
    echo "   • 后端API:  http://localhost:8000"
    echo "   • API文档:  http://localhost:8000/docs"
    echo ""
    echo "📋 管理命令:"
    echo "   • 查看状态: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps"
    echo "   • 查看日志: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs [service]"
    echo "   • 停止服务: ./scripts/services/stop-all.command"
    echo ""
    echo "💡 按 Ctrl+C 可以安全退出此脚本，服务将继续在后台运行"
    echo "   要停止所有服务，请运行停止脚本或使用 docker-compose -f docker-compose.yml -f docker-compose.secrets.yml down"
    echo ""

    # 持续监控服务状态
    echo "🔄 监控服务状态中... (按 Ctrl+C 退出监控)"
    while true; do
        sleep 30
        # 检查是否有服务不在运行状态
        if ! docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps --filter "status=running" | grep -q "Up"; then
            echo "⚠️  检测到服务状态异常"
            show_service_status
        fi
    done
}

# 信号处理
trap 'echo -e "\n✅ 已退出监控，服务继续运行"; exit 0' INT TERM

# 执行主函数
main
