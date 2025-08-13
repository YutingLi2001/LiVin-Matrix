#!/bin/bash
# LiVin Matrix - 端到端部署测试脚本
# 本地模拟生产环境测试

set -e

echo "🧪 开始端到端部署测试..."

# 1. 检查必需文件
echo "📋 检查必需文件..."
required_files=(
    ".env.example"
    "docker-compose.yml"
    "docker-compose.production.yml"
    "deploy/nginx/production.conf"
    "deploy/aws/simple-deploy.sh"
    "deploy/aws/production-setup.sh"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 缺失"
        exit 1
    fi
done

# 2. 创建测试环境配置
echo "🔧 创建测试环境配置..."
if [[ ! -f ".env.test" ]]; then
    cp .env.example .env.test

    # 设置测试值
    sed -i '' 's/your-secure-postgres-password/test_postgres_password/g' .env.test
    sed -i '' 's/your-super-secret-jwt-key-at-least-32-characters-long/test_jwt_secret_key_32_characters_long/g' .env.test
    sed -i '' 's/your-super-secret-session-key-at-least-32-characters-long/test_session_secret_key_32_characters_long/g' .env.test
    sed -i '' 's/your-github-oauth-client-id/test_github_client_id/g' .env.test
    sed -i '' 's/your-github-oauth-client-secret/test_github_client_secret/g' .env.test
    sed -i '' 's/https:\/\/your-domain.com\/api\/v1\/auth\/github\/callback/http:\/\/localhost:3000\/api\/v1\/auth\/github\/callback/g' .env.test
    sed -i '' 's/your-resend-api-key/test_resend_api_key/g' .env.test
    sed -i '' 's/production/test/g' .env.test
    sed -i '' 's/false/true/g' .env.test

    echo "  ✅ 测试环境配置创建完成"
fi

# 3. 验证Docker Compose配置
echo "🐳 验证Docker Compose配置..."
if docker compose -f docker-compose.yml -f docker-compose.production.yml --env-file .env.test config > /dev/null 2>&1; then
    echo "  ✅ Docker Compose配置验证通过"
else
    echo "  ❌ Docker Compose配置验证失败"
    exit 1
fi

# 4. 测试脚本语法
echo "📜 验证部署脚本语法..."
if bash -n deploy/aws/simple-deploy.sh; then
    echo "  ✅ simple-deploy.sh 语法正确"
else
    echo "  ❌ simple-deploy.sh 语法错误"
    exit 1
fi

if bash -n deploy/aws/production-setup.sh; then
    echo "  ✅ production-setup.sh 语法正确"
else
    echo "  ❌ production-setup.sh 语法错误"
    exit 1
fi

# 5. 测试本地生产环境启动
echo "🚀 测试本地生产环境启动..."
echo "停止现有容器..."
docker compose down > /dev/null 2>&1 || true

echo "启动生产环境配置..."
docker compose -f docker-compose.yml -f docker-compose.production.yml --env-file .env.test up -d

# 6. 等待服务启动
echo "⏳ 等待服务启动(30秒)..."
sleep 30

# 7. 健康检查
echo "🔍 执行健康检查..."
backend_health=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
if [[ "$backend_health" == "200" ]]; then
    echo "  ✅ 后端健康检查通过 (HTTP $backend_health)"
else
    echo "  ❌ 后端健康检查失败 (HTTP $backend_health)"
    echo "  📋 后端日志:"
    docker compose logs backend --tail=10
fi

frontend_health=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")
if [[ "$frontend_health" == "200" ]]; then
    echo "  ✅ 前端健康检查通过 (HTTP $frontend_health)"
else
    echo "  ❌ 前端健康检查失败 (HTTP $frontend_health)"
    echo "  📋 前端日志:"
    docker compose logs frontend --tail=10
fi

# 8. 数据库连接测试
echo "🗄️  测试数据库连接..."
db_test=$(docker compose exec -T postgres pg_isready -U postgres -d livin_matrix_dev 2>/dev/null || echo "failed")
if [[ "$db_test" == *"accepting connections"* ]]; then
    echo "  ✅ 数据库连接正常"
else
    echo "  ❌ 数据库连接失败"
    docker compose logs postgres --tail=10
fi

# 9. 显示服务状态
echo "📊 服务状态总览:"
docker compose ps

# 10. 清理
echo "🧹 清理测试环境..."
docker compose down
rm -f .env.test

# 11. 总结
echo ""
echo "🎉 端到端测试完成！"
echo ""
echo "📝 测试报告:"
echo "  - 配置文件: ✅ 完整"
echo "  - 脚本语法: ✅ 正确"
echo "  - Docker配置: ✅ 有效"
if [[ "$backend_health" == "200" ]]; then
    echo "  - 后端服务: ✅ 正常"
else
    echo "  - 后端服务: ❌ 异常"
fi
if [[ "$frontend_health" == "200" ]]; then
    echo "  - 前端服务: ✅ 正常"
else
    echo "  - 前端服务: ❌ 异常"
fi
if [[ "$db_test" == *"accepting connections"* ]]; then
    echo "  - 数据库: ✅ 正常"
else
    echo "  - 数据库: ❌ 异常"
fi

echo ""
echo "🚀 如果所有检查都通过，您可以放心进行AWS生产部署！"
