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

# 检查必要的环境变量
echo "🔍 检查环境变量配置..."
missing_vars=()

# 检查必要的环境变量
if [ -z "${DATABASE_URL:-}" ]; then
    missing_vars+=("DATABASE_URL")
fi

if [ -z "${SECRET_KEY:-}" ]; then
    missing_vars+=("SECRET_KEY")
fi

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "⚠️  缺少以下环境变量："
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "请通过以下方式之一设置环境变量："
    echo "1. 使用 docker-compose.dev.yml 启动开发环境"
    echo "2. 手动设置环境变量，例如："
    echo "   export DATABASE_URL=postgresql://postgres:devpassword123@localhost:5432/livin_matrix_dev"
    echo "   export SECRET_KEY=your-secret-key-here"
else
    echo "✅ 环境变量配置完整"
fi

echo ""
echo "🎉 后端环境设置完成！"
echo ""
echo "下一步操作："
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 启动开发服务器: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "3. 访问 API 文档: http://localhost:8000/docs"
echo ""