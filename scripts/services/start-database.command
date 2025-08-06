#!/bin/bash

# LIVIN-MATRIX 数据库服务启动脚本
# 双击此文件即可启动数据库服务 (PostgreSQL + Redis)

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

# 设置终端标题
echo -n -e "\033]0;LIVIN-MATRIX 数据库服务\007"

# 打印启动信息
echo "==============================================="
echo "        LIVIN-MATRIX 数据库服务启动"
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
        case $port in
            5432) docker stop livin-matrix-postgres 2>/dev/null || true ;;
            6379) docker stop livin-matrix-redis 2>/dev/null || true ;;
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
        if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps $service | grep -q "healthy\|Up"; then
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
    echo "📊 数据库服务状态："
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps postgres redis
    echo ""
}

# 检查数据库连接
test_database_connection() {
    echo "🔍 测试数据库连接..."

    # 测试PostgreSQL连接
    if docker exec livin-matrix-postgres pg_isready -U postgres -d livin_matrix_dev > /dev/null 2>&1; then
        echo "✅ PostgreSQL 连接正常"
    else
        echo "❌ PostgreSQL 连接失败"
        return 1
    fi

    # 测试Redis连接
    if docker exec livin-matrix-redis redis-cli ping | grep -q "PONG"; then
        echo "✅ Redis 连接正常"
    else
        echo "❌ Redis 连接失败"
        return 1
    fi

    return 0
}

# 检查Docker Secrets环境
check_secrets_environment() {
    echo "🔐 检查Docker Secrets环境..."

    # 检查secrets目录是否存在
    if [ ! -d "secrets" ]; then
        echo "❌ 缺少 secrets/ 目录"
        echo ""
        echo "项目已迁移到Docker Secrets系统，请确保："
        echo "1. secrets/ 目录存在"
        echo "2. 包含所需的密钥文件"
        echo "3. 使用 docker-compose.secrets.yml 配置"
        echo ""
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi

    # 检查PostgreSQL密钥文件
    if [ ! -f "secrets/POSTGRES_PASSWORD" ]; then
        echo "❌ 缺少必需的密钥文件: secrets/POSTGRES_PASSWORD"
        echo ""
        echo "请确保PostgreSQL密钥文件存在后重新运行脚本"
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi

    echo "✅ Docker Secrets环境检查通过"
}

# 主启动流程
main() {
    echo "🔍 检查系统环境..."
    check_docker
    check_secrets_environment

    echo "🔍 检查端口冲突..."
    check_port_conflict 5432 "PostgreSQL"
    check_port_conflict 6379 "Redis"

    echo ""
    echo "🗄️  启动数据库服务..."

    # 仅启动数据库相关服务（使用Docker Secrets配置）
    if ! docker-compose -f docker-compose.yml -f docker-compose.secrets.yml up -d postgres redis; then
        echo "❌ 数据库服务启动失败"
        echo "请检查 Docker 配置和网络连接"
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi

    echo ""
    echo "⏳ 等待数据库服务就绪..."

    # 等待PostgreSQL服务
    if ! wait_for_service "postgres"; then
        echo "PostgreSQL启动失败，查看日志: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs postgres"
        exit 1
    fi

    # 等待Redis服务
    if ! wait_for_service "redis"; then
        echo "Redis启动失败，查看日志: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs redis"
        exit 1
    fi

    # 测试数据库连接
    if ! test_database_connection; then
        echo "数据库连接测试失败"
        exit 1
    fi

    show_service_status

    echo "🎉 数据库服务启动成功！"
    echo ""
    echo "🔗 连接信息:"
    echo "   • PostgreSQL: localhost:5432"
    echo "     - 数据库: livin_matrix_dev"
    echo "     - 用户名: postgres"
    echo "     - 密码: [已配置]"
    echo "   • Redis: localhost:6379"
    echo ""
    echo "📋 管理命令:"
    echo "   • 查看状态: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps postgres redis"
    echo "   • 查看日志: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs postgres redis"
    echo "   • 停止数据库: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml stop postgres redis"
    echo ""
    echo "🚀 下一步:"
    echo "   • 启动后端: ./scripts/services/start-backend.command"
    echo "   • 启动前端: ./scripts/services/start-frontend.command"
    echo "   • 启动全部: ./scripts/services/start-all.command"
    echo ""
    echo "💡 按 Ctrl+C 可以安全退出此脚本，数据库将继续在后台运行"
    echo ""

    # 持续监控数据库状态
    echo "🔄 监控数据库状态中... (按 Ctrl+C 退出监控)"
    while true; do
        sleep 30
        if ! docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps postgres redis | grep -q "Up"; then
            echo "⚠️  检测到数据库状态异常"
            show_service_status
        fi
    done
}

# 信号处理
trap 'echo -e "\n✅ 已退出监控，数据库继续运行"; exit 0' INT TERM

# 执行主函数
main
