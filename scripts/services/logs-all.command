#!/bin/bash

# LIVIN-MATRIX 全服务日志查看脚本
# 双击此文件即可查看所有服务日志

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

# 设置终端标题
echo -n -e "\033]0;LIVIN-MATRIX 服务日志查看\007"

# 打印日志信息
echo "==============================================="
echo "        LIVIN-MATRIX 服务日志查看"
echo "==============================================="
echo ""

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 检查Docker是否运行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker 未运行，无法查看服务日志"
        echo "请先启动 Docker Desktop"
        echo ""
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi
}

# 检查服务是否运行
check_services() {
    if ! docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps | grep -q "livin-matrix"; then
        echo "⚠️  没有运行的 LIVIN-MATRIX 服务"
        echo "💡 请先启动服务: ./scripts/services/start-all.command"
        echo ""
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi
}

# 显示日志选项菜单
show_log_menu() {
    clear
    echo "==============================================="
    echo "        LIVIN-MATRIX 日志查看选项"
    echo "==============================================="
    echo ""
    echo "📋 可用选项："
    echo ""
    echo "   1. 📊 查看所有服务日志 (实时)"
    echo "   2. 🗄️  仅查看数据库日志 (PostgreSQL + Redis)"
    echo "   3. 🚀 仅查看后端日志 (FastAPI)"
    echo "   4. 🎨 仅查看前端日志 (React/Vite)"
    echo "   5. ⚡ 查看最近错误日志"
    echo "   6. 📈 查看服务启动日志"
    echo "   7. 🔍 搜索特定内容"
    echo "   8. 💾 导出日志到文件"
    echo "   9. 🔄 刷新菜单"
    echo "   0. ❌ 退出"
    echo ""
    echo "💡 提示: 在实时日志模式下按 Ctrl+C 返回菜单"
    echo ""
}

# 查看所有服务日志
view_all_logs() {
    echo "📊 查看所有服务实时日志..."
    echo "💡 按 Ctrl+C 返回菜单"
    echo ""
    sleep 2
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs -f --tail=50
}

# 查看数据库日志
view_database_logs() {
    echo "🗄️  查看数据库服务日志..."
    echo "💡 按 Ctrl+C 返回菜单"
    echo ""
    sleep 2
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs -f --tail=50 postgres redis
}

# 查看后端日志
view_backend_logs() {
    echo "🚀 查看后端服务日志..."
    echo "💡 按 Ctrl+C 返回菜单"
    echo ""
    sleep 2
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs -f --tail=50 backend
}

# 查看前端日志
view_frontend_logs() {
    echo "🎨 查看前端服务日志..."
    echo "💡 按 Ctrl+C 返回菜单"
    echo ""
    sleep 2
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs -f --tail=50 frontend
}

# 查看错误日志
view_error_logs() {
    echo "⚡ 查看最近错误日志..."
    echo "🔍 搜索包含 'error', 'Error', 'ERROR', 'exception' 等关键词的日志"
    echo ""
    
    # 搜索错误关键词
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs --tail=100 | grep -i -E "(error|exception|fail|fatal|critical)" | tail -20
    
    echo ""
    echo "📋 如需查看完整错误上下文，请选择具体服务查看详细日志"
    echo "按任意键返回菜单..."
    read -n 1
}

# 查看启动日志
view_startup_logs() {
    echo "📈 查看服务启动日志..."
    echo "🔍 显示各服务的启动过程"
    echo ""
    
    echo "🗄️  PostgreSQL 启动日志："
    echo "----------------------------------------"
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs postgres | tail -10
    echo ""
    
    echo "🔴 Redis 启动日志："
    echo "----------------------------------------"
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs redis | tail -10
    echo ""
    
    echo "🚀 Backend 启动日志："
    echo "----------------------------------------"
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs backend | tail -10
    echo ""
    
    echo "🎨 Frontend 启动日志："
    echo "----------------------------------------"
    docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs frontend | tail -10
    echo ""
    
    echo "按任意键返回菜单..."
    read -n 1
}

# 搜索特定内容
search_logs() {
    echo ""
    read -p "🔍 输入要搜索的内容: " search_term
    
    if [ -z "$search_term" ]; then
        echo "❌ 搜索内容不能为空"
        sleep 2
        return
    fi
    
    echo ""
    echo "🔍 搜索结果 (包含: '$search_term'):"
    echo "================================================="
    
    # 在所有日志中搜索
    local results=$(docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs | grep -i "$search_term")
    
    if [ -n "$results" ]; then
        echo "$results" | tail -20
        echo ""
        echo "📊 显示最近20条匹配结果"
    else
        echo "❌ 未找到包含 '$search_term' 的日志"
    fi
    
    echo ""
    echo "💡 如需搜索更多结果，可使用: docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs | grep -i '$search_term'"
    echo "按任意键返回菜单..."
    read -n 1
}

# 导出日志到文件
export_logs() {
    echo ""
    echo "💾 导出日志选项："
    echo "1. 导出所有服务日志"
    echo "2. 导出特定服务日志"
    echo "3. 导出错误日志"
    echo ""
    read -p "选择导出类型 (1-3): " export_type
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local export_dir="logs_export_$timestamp"
    
    mkdir -p "$export_dir"
    
    case $export_type in
        1)
            echo "📊 导出所有服务日志..."
            docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs > "$export_dir/all_services.log"
            docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs postgres > "$export_dir/postgres.log"
            docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs redis > "$export_dir/redis.log"
            docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs backend > "$export_dir/backend.log"
            docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs frontend > "$export_dir/frontend.log"
            ;;
        2)
            echo "选择服务:"
            echo "1. PostgreSQL"
            echo "2. Redis"
            echo "3. Backend"
            echo "4. Frontend"
            read -p "输入选择 (1-4): " service_choice
            
            case $service_choice in
                1) docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs postgres > "$export_dir/postgres.log" ;;
                2) docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs redis > "$export_dir/redis.log" ;;
                3) docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs backend > "$export_dir/backend.log" ;;
                4) docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs frontend > "$export_dir/frontend.log" ;;
                *) echo "❌ 无效选择"; return ;;
            esac
            ;;
        3)
            echo "⚡ 导出错误日志..."
            docker-compose -f docker-compose.yml -f docker-compose.secrets.yml logs | grep -i -E "(error|exception|fail|fatal|critical)" > "$export_dir/errors.log"
            ;;
        *)
            echo "❌ 无效选择"
            return
            ;;
    esac
    
    echo "✅ 日志已导出到: $export_dir/"
    echo "📁 导出文件列表:"
    ls -la "$export_dir/"
    echo ""
    echo "按任意键返回菜单..."
    read -n 1
}

# 主日志查看流程
main() {
    echo "🔍 检查 Docker 环境..."
    check_docker
    check_services
    
    # 主菜单循环
    while true; do
        show_log_menu
        read -p "请选择操作 (0-9): " choice
        
        case $choice in
            1)
                view_all_logs
                ;;
            2)
                view_database_logs
                ;;
            3)
                view_backend_logs
                ;;
            4)
                view_frontend_logs
                ;;
            5)
                view_error_logs
                ;;
            6)
                view_startup_logs
                ;;
            7)
                search_logs
                ;;
            8)
                export_logs
                ;;
            9)
                continue
                ;;
            0)
                echo "👋 日志查看结束"
                exit 0
                ;;
            *)
                echo "❌ 无效选择，请输入 0-9"
                sleep 2
                ;;
        esac
    done
}

# 信号处理 - 返回菜单而不是直接退出
trap 'echo -e "\n🔄 返回菜单..."; sleep 1; main' INT

# 执行主函数
main