#!/bin/bash
# PostgreSQL 自定义 Entrypoint 脚本
# 支持从多种方式读取密码：Docker Secrets、环境变量文件、环境变量

set -e

# 优先级：Docker Secret > 环境变量文件 > 环境变量
if [ -f /run/secrets/POSTGRES_PASSWORD ]; then
    echo "🔐 从 Docker Secret 读取 POSTGRES_PASSWORD"
    export POSTGRES_PASSWORD=$(cat /run/secrets/POSTGRES_PASSWORD)
elif [ -f /var/secrets/POSTGRES_PASSWORD ]; then
    echo "🔐 从密钥文件读取 POSTGRES_PASSWORD"
    export POSTGRES_PASSWORD=$(cat /var/secrets/POSTGRES_PASSWORD)
elif [ -n "$POSTGRES_PASSWORD" ]; then
    echo "🔐 使用环境变量 POSTGRES_PASSWORD"
else
    echo "❌ 错误：POSTGRES_PASSWORD 未找到任何配置源"
    echo "请提供以下任一配置："
    echo "  1. Docker Secret: /run/secrets/POSTGRES_PASSWORD"
    echo "  2. 密钥文件: /var/secrets/postgres_password"
    echo "  3. 环境变量: POSTGRES_PASSWORD"
    exit 1
fi

# 验证密码是否设置
if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ 错误：POSTGRES_PASSWORD 读取后为空"
    exit 1
fi

echo "✅ PostgreSQL 密码配置完成"

# 调用官方 PostgreSQL entrypoint
exec docker-entrypoint.sh "$@"
