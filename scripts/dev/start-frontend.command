#!/bin/bash

# LIVIN-MATRIX 前端开发服务器启动脚本
# 双击此文件即可启动前端开发服务器

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 设置终端标题
echo -n -e "\033]0;LIVIN-MATRIX 前端开发服务器\007"

# 打印启动信息
echo "==============================================="
echo "        LIVIN-MATRIX 前端开发服务器启动"
echo "==============================================="
echo ""

# 切换到项目前端目录
cd "$SCRIPT_DIR/../../frontend"

# 检查是否存在node_modules
if [ ! -d "node_modules" ]; then
    echo "🔄 检测到缺少依赖，正在安装..."
    npm install
    echo ""
fi

# 检查端口5173是否被占用
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口5173已被占用，正在尝试清理..."
    pkill -f "vite.*5173" 2>/dev/null || true
    sleep 2
fi

echo "🚀 正在启动前端开发服务器..."
echo "📱 服务器地址: http://localhost:5173"
echo "💡 按 Ctrl+C 或关闭此窗口来停止服务器"
echo ""

# 启动开发服务器
npm run dev

# 如果脚本执行到这里，说明服务器已经停止
echo ""
echo "✅ 前端开发服务器已停止"
echo "按任意键关闭此窗口..."
read -n 1