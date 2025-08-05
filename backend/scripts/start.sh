#!/bin/bash
# Backend 服务启动脚本
# 自动运行数据库迁移，然后启动应用

set -e  # 遇到错误立即退出

echo "🚀 Starting LiVin Matrix Backend..."

# 等待数据库就绪
echo "⏳ Waiting for database to be ready..."
python -c "
import time
import sys
import psycopg2

max_retries = 15
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            host='postgres',
            database='livin_matrix_dev', 
            user='postgres',
            password='Ji9Cof39rWMTPxwyaCzmGGIwROGwVuFk'
        )
        conn.close()
        print('✅ Database is ready!')
        break
    except Exception as e:
        retry_count += 1
        print(f'⏳ Database not ready yet... ({retry_count}/{max_retries})')
        time.sleep(2)
        if retry_count >= max_retries:
            print(f'❌ Database connection failed after {max_retries} retries: {e}')
            sys.exit(1)
"

# 运行数据库迁移
echo "🔄 Running database migrations..."
python -m alembic upgrade head
echo "✅ Database migrations completed"

# 启动应用
echo "🌟 Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload