#!/bin/bash

# LIVIN-MATRIX 全服务停止脚本
# 双击此文件即可优雅停止所有服务

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/../.."

# 设置终端标题
echo -n -e "\033]0;LIVIN-MATRIX 全服务停止\007"

# 打印停止信息
echo "==============================================="
echo "         LIVIN-MATRIX 全服务停止"
echo "==============================================="
echo ""

# 切换到项目根目录
cd "$PROJECT_ROOT"

# 检查Docker是否运行
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker 未运行，无法执行停止操作"
        echo "按任意键关闭此窗口..."
        read -n 1
        exit 1
    fi
}

# 显示当前服务状态
show_current_status() {
    echo "📊 当前服务状态："
    if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps | grep -q "Up\|Exited"; then
        docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps
    else
        echo "ℹ️  没有正在运行的LiVin-Matrix服务"
    fi
    echo ""
}


# 清理网络和卷 (可选)
optional_cleanup() {
    echo ""
    echo "🗑️  可选清理选项："
    echo "1. 仅停止服务 (保留数据)"
    echo "2. 停止并清理网络"
    echo "3. 停止并清理所有数据 (⚠️  删除数据库数据)"
    echo "4. 跳过额外清理"
    echo ""
    read -p "请选择清理级别 (1-4): " cleanup_level

    case $cleanup_level in
        1)
            echo "ℹ️  仅停止服务，保留所有数据"
            ;;
        2)
            echo "🔄 清理网络..."
            docker network prune -f
            echo "✅ 网络清理完成"
            ;;
        3)
            echo "⚠️  警告：即将删除所有数据！"
            read -p "确认删除所有数据? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                echo "🔄 清理网络和数据卷..."
                docker network prune -f
                docker volume prune -f
                echo "✅ 所有数据已清理"
            else
                echo "ℹ️  取消数据清理"
            fi
            ;;
        4|*)
            echo "ℹ️  跳过额外清理"
            ;;
    esac
}

# 检查端口释放
check_ports_released() {
    echo ""
    echo "🔍 检查端口释放状态..."

    local ports=(5432 6379 8000 3000)
    local all_released=true

    for port in "${ports[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "⚠️  端口 $port 仍被占用"
            all_released=false
        else
            echo "✅ 端口 $port 已释放"
        fi
    done

    if [ "$all_released" = true ]; then
        echo "✅ 所有端口已成功释放"
    else
        echo "⚠️  部分端口仍被占用，可能需要手动处理"
    fi
}

# 主停止流程
main() {
    echo "🔍 检查系统环境..."
    check_docker

    show_current_status

    echo "🛑 开始停止所有服务..."

    # 检查是否有正在运行的服务
    if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps | grep -q "Up"; then
        echo "🔄 正在停止 LiVin-Matrix 服务..."
        if docker-compose -f docker-compose.yml -f docker-compose.secrets.yml stop; then
            echo "✅ 所有服务已停止"

            # 等待服务完全停止
            echo "⏳ 等待服务完全停止..."
            local attempts=0
            while docker-compose -f docker-compose.yml -f docker-compose.secrets.yml ps | grep -q "Up" && [ $attempts -lt 30 ]; do
                sleep 2
                attempts=$((attempts + 1))
            done

            if [ $attempts -ge 30 ]; then
                echo "⚠️  部分服务停止耗时较长，但正在后台停止"
            else
                echo "✅ 所有服务已完全停止"
            fi
        else
            echo "❌ 服务停止失败"
            exit 1
        fi
    else
        echo "ℹ️  没有正在运行的服务，无需停止"
    fi

    # 可选清理
    optional_cleanup

    # 检查端口释放
    check_ports_released

    echo ""
    echo "🎉 所有服务已停止！"
    echo ""
    echo "📋 后续操作："
    echo "   • 重新启动: ./scripts/services/start-all.command"
    echo "   • 启动特定服务:"
    echo "     - 数据库: ./scripts/services/start-database.command"
    echo "     - 后端: ./scripts/services/start-backend.command"
    echo "     - 前端: ./scripts/services/start-frontend.command"
    echo ""
    echo "💡 服务已完全停止，系统资源已释放"
    echo ""
    echo "按任意键关闭此窗口..."
    read -n 1
}

# 信号处理
trap 'echo -e "\n⚠️  停止操作被中断"; exit 1' INT TERM

# 执行主函数
main
