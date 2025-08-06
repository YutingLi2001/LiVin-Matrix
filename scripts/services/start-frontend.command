#!/bin/bash

# LIVIN-MATRIX 前端服务启动脚本
# 双击此文件即可启动前端服务 (Docker容器模式)

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

# 设置终端标题
echo -n -e "\033]0;LIVIN-MATRIX 前端服务\007"

# 打印启动信息
echo "==============================================="
echo "        LIVIN-MATRIX 前端服务启动"
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
        if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps $service | grep -q "Up"; then
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
    echo "📊 前端服务状态："
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps frontend
    echo ""
}

# 测试前端连接
test_frontend_connection() {
    echo "🔍 测试前端服务连接..."

    local max_attempts=15
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
            echo "✅ 前端服务连接正常"
            return 0
        fi

        echo "   测试连接 $attempt/$max_attempts..."
        sleep 5
        attempt=$((attempt + 1))
    done

    echo "⚠️  前端服务可能仍在构建中，请稍后手动访问"
    return 1
}

# 检查后端依赖 (可选)
check_backend_dependency() {
    echo "🔍 检查后端API依赖..."

    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 后端API可用，前端功能将完全正常"
    else
        echo "⚠️  后端API不可用，前端将以开发模式运行"
        echo "💡 如需完整功能，请先启动后端: ./scripts/services/start-backend.command"
    fi
}

# 主启动流程
main() {
    echo "🔍 检查系统环境..."
    check_docker

    echo "🔍 检查端口冲突..."
    check_port_conflict 3000 "Frontend"

    # 检查后端依赖状态
    check_backend_dependency

    echo ""
    echo "🎨 启动前端服务..."

    # 启动前端服务
    if ! docker-compose -f docker-compose.yml -f docker-compose.secrets.yml up -d frontend; then
        echo "❌ 前端服务启动失败"
        echo "请检查 Docker 配置和网络连接"
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi

    echo ""
    echo "⏳ 等待前端服务就绪..."
    echo "📝 注意：首次启动可能需要较长时间进行依赖安装和构建"

    # 等待前端服务
    if ! wait_for_service "frontend"; then
        echo "前端服务启动可能失败，查看日志: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs frontend"
        echo "前端服务通常需要更长时间启动，请查看日志确认状态"
    fi

    # 给前端更多时间进行构建
    echo "⏳ 等待前端构建完成..."
    sleep 10

    # 测试前端连接
    test_frontend_connection

    show_service_status

    echo "🎉 前端服务启动完成！"
    echo ""
    echo "🌐 访问地址:"
    echo "   • 前端应用: http://localhost:3000"
    echo "   • 开发工具: 在浏览器中按 F12 打开"
    echo ""
    echo "🔗 相关服务:"
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   • 后端API:  http://localhost:8000 ✅"
        echo "   • API文档:  http://localhost:8000/docs ✅"
    else
        echo "   • 后端API:  http://localhost:8000 ❌ (未启动)"
        echo "   • 启动后端: ./scripts/services/start-backend.command"
    fi
    echo ""
    echo "📋 管理命令:"
    echo "   • 查看状态: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps frontend"
    echo "   • 查看日志: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs frontend"
    echo "   • 停止前端: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml stop frontend"
    echo ""
    echo "🚀 全栈开发:"
    echo "   • 启动全部: ./scripts/services/start-all.command"
    echo ""
    echo "💡 按 Ctrl+C 可以安全退出此脚本，前端将继续在后台运行"
    echo "   前端支持热重载，修改代码后会自动刷新浏览器"
    echo ""

    # 持续监控前端服务状态
    echo "🔄 监控前端服务状态中... (按 Ctrl+C 退出监控)"
    while true; do
        sleep 30
        if ! docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps frontend | grep -q "Up"; then
            echo "⚠️  检测到前端服务状态异常"
            show_service_status
        fi
    done
}

# 信号处理
trap 'echo -e "\n✅ 已退出监控，前端服务继续运行"; exit 0' INT TERM

# 执行主函数
main
