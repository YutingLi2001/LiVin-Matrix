#!/bin/bash

# LIVIN-MATRIX 全服务重启脚本
# 双击此文件即可重启所有服务

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

# 设置终端标题
echo -n -e "\033]0;LIVIN-MATRIX 全服务重启\007"

# 打印重启信息
echo "==============================================="
echo "         LIVIN-MATRIX 全服务重启"
echo "==============================================="
echo ""

# 切换到项目根目录
cd "$PROJECT_ROOT"

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

    # 检查关键密钥文件
    local required_secrets=("POSTGRES_PASSWORD" "GITHUB_CLIENT_ID" "GITHUB_CLIENT_SECRET")
    local missing_secrets=()

    for secret in "${required_secrets[@]}"; do
        if [ ! -f "secrets/$secret" ]; then
            missing_secrets+=("$secret")
        fi
    done

    if [ ${#missing_secrets[@]} -gt 0 ]; then
        echo "❌ 缺少必需的密钥文件:"
        for secret in "${missing_secrets[@]}"; do
            echo "   - secrets/$secret"
        done
        echo ""
        echo "请确保所有必需的密钥文件存在后重新运行脚本"
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi

    echo "✅ Docker Secrets环境检查通过"
}

# 检查Docker是否运行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker 未运行，请先启动 Docker Desktop"
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi
}

# 显示当前服务状态
show_current_status() {
    echo "📊 当前服务状态："
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps
    echo ""
}

# 重启选项
restart_options() {
    echo "🔄 重启选项："
    echo "1. 优雅重启 (先停止再启动，保留数据)"
    echo "2. 强制重启 (docker-compose restart)"
    echo "3. 完全重建 (重新构建镜像，⚠️  较慢)"
    echo "4. 仅重启后端服务"
    echo "5. 仅重启前端服务"
    echo ""
    read -p "请选择重启方式 (1-5): " restart_type

    case $restart_type in
        1) graceful_restart ;;
        2) force_restart ;;
        3) rebuild_restart ;;
        4) restart_backend_only ;;
        5) restart_frontend_only ;;
        *) echo "❌ 无效选择，执行优雅重启"; graceful_restart ;;
    esac
}

# 优雅重启 (推荐)
graceful_restart() {
    echo ""
    echo "🔄 执行优雅重启..."

    # 先停止所有服务
    echo "🛑 停止所有服务..."
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml stop

    echo "⏳ 等待服务完全停止..."
    sleep 5

    # 重新启动
    echo "🚀 重新启动所有服务..."
    # 使用Docker Secrets配置
    if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml up -d; then
        echo "✅ 优雅重启完成"
    else
        echo "❌ 重启失败"
        exit 1
    fi
}

# 强制重启
force_restart() {
    echo ""
    echo "⚡ 执行强制重启..."

    if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml restart; then
        echo "✅ 强制重启完成"
    else
        echo "❌ 重启失败"
        exit 1
    fi
}

# 重建重启
rebuild_restart() {
    echo ""
    echo "🏗️  执行重建重启..."
    echo "⚠️  这将重新构建所有镜像，可能需要较长时间"

    read -p "确认继续? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "❌ 重建已取消"
        exit 1
    fi

    # 停止并删除容器
    echo "🛑 停止并清理现有容器..."
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml down

    # 重新构建并启动
    echo "🏗️  重新构建并启动服务..."
    if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml up -d --build; then
        echo "✅ 重建重启完成"
    else
        echo "❌ 重建失败"
        exit 1
    fi
}

# 仅重启后端
restart_backend_only() {
    echo ""
    echo "🔧 仅重启后端服务..."

    # 重启后端及其依赖
    if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml restart postgres redis backend; then
        echo "✅ 后端服务重启完成"
    else
        echo "❌ 后端重启失败"
        exit 1
    fi
}

# 仅重启前端
restart_frontend_only() {
    echo ""
    echo "🎨 仅重启前端服务..."

    if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml restart frontend; then
        echo "✅ 前端服务重启完成"
    else
        echo "❌ 前端重启失败"
        exit 1
    fi
}

# 等待服务就绪
wait_for_services() {
    echo ""
    echo "⏳ 等待服务就绪..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        local healthy_count=$(docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps | grep -c "healthy\|Up")
        local total_services=$(docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps | grep -c "livin-matrix")

        if [ "$healthy_count" -ge 3 ]; then  # 至少3个核心服务
            echo "✅ 主要服务已就绪"
            break
        fi

        echo "   等待服务启动 $attempt/$max_attempts (已就绪: $healthy_count)"
        sleep 3
        attempt=$((attempt + 1))
    done

    if [ $attempt -gt $max_attempts ]; then
        echo "⚠️  部分服务可能仍在启动中"
    fi
}

# 服务健康检查
health_check() {
    echo ""
    echo "🏥 执行健康检查..."

    local all_healthy=true

    # 检查数据库
    if docker exec livin-matrix-postgres pg_isready -U postgres -d livin_matrix_dev > /dev/null 2>&1; then
        echo "✅ PostgreSQL 健康"
    else
        echo "❌ PostgreSQL 不健康"
        all_healthy=false
    fi

    # 检查Redis
    if docker exec livin-matrix-redis redis-cli ping | grep -q "PONG"; then
        echo "✅ Redis 健康"
    else
        echo "❌ Redis 不健康"
        all_healthy=false
    fi

    # 检查后端API
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 后端API 健康"
    else
        echo "⚠️  后端API 可能仍在启动"
        all_healthy=false
    fi

    # 检查前端
    if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ 前端服务 健康"
    else
        echo "⚠️  前端服务 可能仍在构建"
        all_healthy=false
    fi

    if [ "$all_healthy" = true ]; then
        echo "🎉 所有服务健康检查通过！"
    else
        echo "⚠️  部分服务可能需要更多时间启动"
    fi
}

# 主重启流程
main() {
    echo "🔍 检查系统环境..."
    check_docker
    check_secrets_environment

    show_current_status

    # 显示重启选项
    restart_options

    # 等待服务就绪
    wait_for_services

    # 健康检查
    health_check

    echo ""
    echo "📊 重启后服务状态："
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps

    echo ""
    echo "🎉 服务重启完成！"
    echo ""
    echo "🌐 访问地址:"
    echo "   • 前端应用: http://localhost:3000"
    echo "   • 后端API:  http://localhost:8000"
    echo "   • API文档:  http://localhost:8000/docs"
    echo ""
    echo "📋 管理命令:"
    echo "   • 查看状态: ./scripts/services/status-all.command"
    echo "   • 查看日志: ./scripts/services/logs-all.command"
    echo "   • 停止服务: ./scripts/services/stop-all.command"
    echo ""
    echo "💡 如果服务仍有问题，请查看日志或使用重建选项"
    echo ""
    echo "按任意键关闭此窗口..."
    read -n 1
}

# 信号处理
trap 'echo -e "\n⚠️  重启操作被中断"; exit 1' INT TERM

# 执行主函数
main
