#!/bin/bash

# LiVin Matrix Backend 环境设置脚本

set -e

echo "🚀 设置 LiVin Matrix 后端开发环境..."

# 检查 Python 版本
echo "📋 检查 Python 版本..."
python3 --version

# 创建虚拟环境
echo "🔧 创建 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "ℹ️  虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip

# 安装生产依赖
echo "📦 安装生产依赖..."
pip install -r requirements.txt

# 安装开发依赖
echo "🛠️  安装开发依赖..."
pip install -r requirements-dev.txt

# 创建 .env 文件（如果不存在）
if [ ! -f ".env" ]; then
    echo "📝 创建 .env 配置文件..."
    cat > .env << EOF
# 环境配置
ENVIRONMENT=development
DEBUG=true

# 数据库配置
DATABASE_URL=postgresql://postgres:devpassword123@localhost:5432/livin_matrix_dev

# Redis 配置
REDIS_URL=redis://localhost:6379

# 安全配置
SECRET_KEY=your-secret-key-here-change-in-production

# CORS 配置
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 日志配置
LOG_LEVEL=INFO
EOF
    echo "✅ .env 文件创建成功"
else
    echo "ℹ️  .env 文件已存在，跳过创建"
fi

echo ""
echo "🎉 后端环境设置完成！"
echo ""
echo "下一步操作："
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 启动开发服务器: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "3. 访问 API 文档: http://localhost:8000/docs"
echo ""