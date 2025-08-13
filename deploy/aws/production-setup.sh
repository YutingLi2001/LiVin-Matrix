#!/bin/bash
# LiVin Matrix - EC2生产环境配置脚本
# 在EC2实例上运行此脚本以配置生产环境

set -e

echo "🚀 配置LiVin Matrix生产环境..."

# 1. 更新系统
echo "📦 更新系统包..."
sudo yum update -y

# 2. 安装Docker
echo "🐳 安装Docker..."
sudo yum install -y docker
sudo usermod -aG docker ec2-user
sudo systemctl enable docker
sudo systemctl start docker

# 安装Docker Compose
echo "🔧 安装Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# 3. 安装Nginx和SSL工具
echo "🔒 安装Nginx和SSL工具..."
sudo yum install -y nginx
sudo amazon-linux-extras install -y epel
sudo yum install -y certbot python3-certbot-nginx

# 4. 获取项目代码
PROJECT_REPO="${GITHUB_REPO:-https://github.com/your-username/LiVin-Matrix.git}"
PROJECT_DIR="LiVin-Matrix"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "📥 克隆项目从: $PROJECT_REPO"
    git clone "$PROJECT_REPO" "$PROJECT_DIR"
else
    echo "🔄 更新项目代码..."
    cd "$PROJECT_DIR"
    git pull origin main
    cd ..
fi

cd "$PROJECT_DIR"

# 5. 配置生产环境变量
echo "🔧 配置环境变量..."
if [ ! -f ".env.production" ]; then
    cp .env.example .env.production
    echo "⚠️  请编辑 .env.production 文件设置生产环境变量"
    echo "   - POSTGRES_PASSWORD"
    echo "   - GITHUB_CLIENT_ID"
    echo "   - GITHUB_CLIENT_SECRET"
    echo "   - RESEND_API_KEY"
    echo "   - JWT_SECRET_KEY"
fi

# 6. 启动服务
echo "🚀 启动Docker Compose服务..."
echo "ℹ️ 使用生产环境配置..."

# 检查.env.production是否存在并包含必要变量
if [ ! -f ".env.production" ]; then
    echo "❌ .env.production 文件不存在！请先配置环境变量。"
    exit 1
fi

# 使用生产环境配置启动
docker compose -f docker-compose.yml -f docker-compose.production.yml --env-file .env.production up -d

# 7. 验证部署
echo "🧪 验证部署..."
echo "⌛ 等待服务启动..."
sleep 30

# 检查服务状态
SERVICE_STATUS=$(docker compose -f docker-compose.yml -f docker-compose.production.yml ps --format "table {{.Service}}\t{{.Status}}")
echo "$SERVICE_STATUS"

if docker compose -f docker-compose.yml -f docker-compose.production.yml ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
    echo "🌐 应用访问地址:"
    echo "   前端: http://$PUBLIC_IP:3000"
    echo "   后端 API: http://$PUBLIC_IP:8000"
    echo "   健康检查: http://$PUBLIC_IP:8000/health"
else
    echo "❌ 部分服务可能未正常启动，请检查:"
    echo "   docker compose -f docker-compose.yml -f docker-compose.production.yml logs"
fi

echo "📝 生产环境配置完成！"
echo "🔒 配置SSL: sudo certbot --nginx -d your-domain.com"
