#!/bin/bash

# LIVIN-MATRIX 全服务状态检查脚本
# 双击此文件即可查看所有服务状态

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

# 设置终端标题
echo -n -e "\033]0;LIVIN-MATRIX 服务状态检查\007"

# 打印状态信息
echo "==============================================="
echo "        LIVIN-MATRIX 服务状态检查"
echo "==============================================="
echo ""

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 检查Docker是否运行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker 未运行，无法检查服务状态"
        echo "请先启动 Docker Desktop"
        echo ""
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi
}

# 显示服务状态
show_service_status() {
    echo "📊 Docker Compose 服务状态："
    echo "======================================================"
    
    if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps | grep -q "Up\|Exited"; then
        docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps
    else
        echo "   没有运行的 LIVIN-MATRIX 服务"
    fi
    
    echo ""
}

# 详细健康检查
detailed_health_check() {
    echo "🏥 详细健康检查："
    echo "======================================================"
    
    local overall_health=true
    
    # 检查PostgreSQL
    echo "🗄️  PostgreSQL 数据库:"
    local postgres_container=$(docker ps --filter "name=livin-matrix_postgres" --format "{{.Names}}" | head -1)
    if [ -n "$postgres_container" ]; then
        if docker exec "$postgres_container" pg_isready -U postgres -d livin_matrix_dev > /dev/null 2>&1; then
            echo "   ✅ 运行中 - 连接正常"
            echo "   📍 端口: 5432"
            echo "   📊 数据库: livin_matrix_dev"
        else
            echo "   ⚠️  容器运行但连接失败"
            overall_health=false
        fi
    else
        echo "   ❌ 未运行"
        overall_health=false
    fi
    echo ""
    
    # 检查Redis
    echo "🔴 Redis 缓存:"
    local redis_container=$(docker ps --filter "name=livin-matrix_redis" --format "{{.Names}}" | head -1)
    if [ -n "$redis_container" ]; then
        if docker exec "$redis_container" redis-cli ping 2>/dev/null | grep -q "PONG"; then
            echo "   ✅ 运行中 - 连接正常"
            echo "   📍 端口: 6379"
        else
            echo "   ⚠️  容器运行但连接失败"
            overall_health=false
        fi
    else
        echo "   ❌ 未运行"
        overall_health=false
    fi
    echo ""
    
    # 检查后端API
    echo "🚀 后端 FastAPI:"
    if docker ps | grep -q "livin-matrix-backend"; then
        echo "   📍 端口: 8000"
        if curl -f -s -m 5 http://localhost:8000/health > /dev/null 2>&1; then
            echo "   ✅ 运行中 - API 健康"
            echo "   🌐 健康检查: http://localhost:8000/health"
            echo "   📚 API文档: http://localhost:8000/docs"
        else
            echo "   ⚠️  容器运行但API不可访问"
            echo "   💡 可能仍在启动中..."
            overall_health=false
        fi
    else
        echo "   ❌ 未运行"
        overall_health=false
    fi
    echo ""
    
    # 检查前端
    echo "🎨 前端 React:"
    if docker ps | grep -q "livin-matrix-frontend"; then
        echo "   📍 端口: 3000"
        if curl -f -s -m 5 http://localhost:3000 > /dev/null 2>&1; then
            echo "   ✅ 运行中 - 页面可访问"
            echo "   🌐 应用地址: http://localhost:3000"
        else
            echo "   ⚠️  容器运行但页面不可访问"
            echo "   💡 可能仍在构建中..."
            overall_health=false
        fi
    else
        echo "   ❌ 未运行"
        overall_health=false
    fi
    echo ""
    
    # 总体状态
    echo "🎯 总体状态:"
    if [ "$overall_health" = true ]; then
        echo "   ✅ 所有服务运行正常"
    else
        echo "   ⚠️  部分服务存在问题"
    fi
    echo ""
}

# 端口占用检查
check_port_usage() {
    echo "🔌 端口占用检查："
    echo "======================================================"
    
    local ports=(5432 6379 8000 3000)
    local port_names=("PostgreSQL" "Redis" "Backend API" "Frontend")
    
    for i in "${!ports[@]}"; do
        local port=${ports[$i]}
        local name=${port_names[$i]}
        
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            local process=$(lsof -Pi :$port -sTCP:LISTEN | tail -n +2 | head -1)
            echo "   ✅ 端口 $port ($name) - 已占用"
            echo "      $process"
        else
            echo "   ⚪ 端口 $port ($name) - 空闲"
        fi
        echo ""
    done
}

# 资源使用情况
show_resource_usage() {
    echo "📈 资源使用情况："
    echo "======================================================"
    
    if docker ps | grep -q "livin-matrix"; then
        # 显示容器资源使用
        echo "💾 容器资源使用:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
            $(docker ps --filter "name=livin-matrix" --format "{{.Names}}" | tr '\n' ' ') 2>/dev/null || \
            echo "   无法获取资源统计信息"
        echo ""
        
        # 显示存储卷使用
        echo "💿 存储卷使用:"
        docker system df -v | grep -E "(TYPE|livin.*matrix)" || echo "   无相关存储卷"
    else
        echo "   没有运行的服务容器"
    fi
    echo ""
}

# 快速诊断
quick_diagnosis() {
    echo "🔍 快速诊断："
    echo "======================================================"
    
    local running_services=0
    local total_services=4  # postgres, redis, backend, frontend
    
    # 计算运行中的服务数量
    if docker ps | grep -q "livin-matrix-postgres"; then ((running_services++)); fi
    if docker ps | grep -q "livin-matrix-redis"; then ((running_services++)); fi
    if docker ps | grep -q "livin-matrix-backend"; then ((running_services++)); fi
    if docker ps | grep -q "livin-matrix-frontend"; then ((running_services++)); fi
    
    echo "📊 服务统计: $running_services/$total_services 个服务运行中"
    echo ""
    
    # 诊断建议
    if [ $running_services -eq 0 ]; then
        echo "💡 诊断建议:"
        echo "   • 所有服务都未运行"
        echo "   • 运行: ./scripts/services/start-all.command"
    elif [ $running_services -lt $total_services ]; then
        echo "💡 诊断建议:"
        echo "   • 部分服务未运行"
        echo "   • 检查日志: ./scripts/services/logs-all.command"
        echo "   • 重启服务: ./scripts/services/restart-all.command"
    else
        echo "💡 诊断建议:"
        echo "   • 所有主要服务都在运行"
        echo "   • 如有问题，检查具体服务健康状态"
    fi
    echo ""
}

# 管理建议
show_management_commands() {
    echo "📋 管理命令："
    echo "======================================================"
    echo "   🚀 启动服务:"
    echo "      • 全部启动: ./scripts/services/start-all.command"
    echo "      • 仅数据库: ./scripts/services/start-database.command"
    echo "      • 仅后端:   ./scripts/services/start-backend.command"
    echo "      • 仅前端:   ./scripts/services/start-frontend.command"
    echo ""
    echo "   🔄 服务管理:"
    echo "      • 重启服务: ./scripts/services/restart-all.command"
    echo "      • 停止服务: ./scripts/services/stop-all.command"
    echo "      • 查看日志: ./scripts/services/logs-all.command"
    echo ""
    echo "   🛠️  直接命令:"
    echo "      • docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps           - 查看容器状态"
    echo "      • docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs [service] - 查看特定服务日志"
    echo "      • docker-compose -f docker-compose.yml -f docker-compose.secrets.yml restart [service] - 重启特定服务"
    echo ""
}

# 主检查流程
main() {
    echo "🔍 检查 Docker 环境..."
    check_docker
    
    # 显示各种状态信息
    show_service_status
    detailed_health_check
    check_port_usage
    show_resource_usage
    quick_diagnosis
    show_management_commands
    
    echo "======================================================"
    echo "✅ 状态检查完成！"
    echo ""
    echo "💡 此窗口将保持打开，按任意键刷新状态或关闭"
    
    # 提供刷新选项
    while true; do
        echo ""
        read -p "按 [R] 刷新状态, [Q] 退出: " choice
        case $choice in
            [Rr]* ) 
                clear
                echo "🔄 刷新状态中..."
                main
                return
                ;;
            [Qq]* ) 
                echo "👋 状态检查结束"
                exit 0
                ;;
            * ) 
                echo "请输入 R (刷新) 或 Q (退出)"
                ;;
        esac
    done
}

# 信号处理
trap 'echo -e "\n👋 状态检查已中断"; exit 0' INT TERM

# 执行主函数
main