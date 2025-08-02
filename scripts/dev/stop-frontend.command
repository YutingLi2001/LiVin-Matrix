#!/bin/bash

# LIVIN-MATRIX 前端开发服务器停止脚本
# 双击此文件即可强制关闭前端开发服务器

# 设置终端标题
echo -n -e "\033]0;停止 LIVIN-MATRIX 前端开发服务器\007"

# 打印停止信息
echo "==============================================="
echo "       LIVIN-MATRIX 前端开发服务器停止"
echo "==============================================="
echo ""

# 查找并显示正在运行的相关进程
echo "🔍 正在搜索运行中的前端开发服务器..."

# 查找Vite相关进程
VITE_PIDS=$(pgrep -f "vite" 2>/dev/null)
NODE_VITE_PIDS=$(pgrep -f "node.*vite" 2>/dev/null)
PORT_5173_PIDS=$(lsof -ti:5173 2>/dev/null)

# 收集所有相关进程ID
ALL_PIDS=""
for pid in $VITE_PIDS $NODE_VITE_PIDS $PORT_5173_PIDS; do
    if [ ! -z "$pid" ]; then
        ALL_PIDS="$ALL_PIDS $pid"
    fi
done

# 去重
ALL_PIDS=$(echo $ALL_PIDS | tr ' ' '\n' | sort -u | tr '\n' ' ')

if [ -z "$ALL_PIDS" ]; then
    echo "✅ 没有发现正在运行的前端开发服务器进程"
else
    echo "📋 发现以下进程:"
    echo ""
    
    # 显示进程详情
    for pid in $ALL_PIDS; do
        if kill -0 "$pid" 2>/dev/null; then
            process_info=$(ps -p "$pid" -o pid,ppid,command 2>/dev/null | tail -n 1)
            echo "   PID: $pid - $process_info"
        fi
    done
    
    echo ""
    echo "🛑 正在强制关闭这些进程..."
    
    # 首先尝试优雅关闭
    for pid in $ALL_PIDS; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "   正在发送SIGTERM信号给进程 $pid..."
            kill -TERM "$pid" 2>/dev/null || true
        fi
    done
    
    # 等待2秒
    sleep 2
    
    # 检查并强制关闭仍在运行的进程
    for pid in $ALL_PIDS; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "   强制关闭进程 $pid..."
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done
    
    echo ""
    echo "✅ 前端开发服务器已停止"
fi

# 额外检查端口5173
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo ""
    echo "⚠️  端口5173仍被占用，尝试清理..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    sleep 1
    
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ 端口5173仍被占用，可能需要手动处理"
    else
        echo "✅ 端口5173已释放"
    fi
fi

echo ""
echo "🔄 最终状态检查:"
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   端口5173: ❌ 仍被占用"
else
    echo "   端口5173: ✅ 已释放"
fi

if pgrep -f "vite" >/dev/null 2>&1; then
    echo "   Vite进程: ❌ 仍在运行"
else
    echo "   Vite进程: ✅ 已停止"
fi

echo ""
echo "按任意键关闭此窗口..."
read -n 1