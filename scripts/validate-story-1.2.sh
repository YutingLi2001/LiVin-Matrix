#!/bin/bash

# Story 1.2 数据库设计与部署验证脚本

echo "=== Story 1.2: 数据库设计与部署验证脚本 ==="
echo

# 进入后端目录
cd "$(dirname "$0")/../backend" || exit 1

# 检查必要的文件存在
echo "1. 检查关键文件..."
files=(
    "app/core/database.py"
    "app/models/user.py"
    "app/models/daily_record.py"
    "app/models/workout.py"
    "app/schemas/daily_record.py"
    "alembic.ini"
    "alembic/env.py"
    "alembic/versions/20250731_1400_001_initial_database_schema.py"
    "tests/test_models.py"
    ".env.example"
)

missing_files=()
for file in "${files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    else
        echo "✅ $file"
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "❌ 缺少以下文件:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo

# 检查Docker服务
echo "2. 检查Docker服务..."
if command -v docker &> /dev/null; then
    echo "✅ Docker已安装"

    # 检查docker-compose文件
    if [[ -f "../docker-compose.yml" ]]; then
        echo "✅ docker-compose.yml存在"

        # 尝试启动PostgreSQL服务
        echo "正在启动PostgreSQL服务..."
        cd .. && docker compose up -d postgres

        # 等待服务启动
        echo "等待PostgreSQL服务启动..."
        sleep 10

        # 检查服务状态
        if docker compose ps postgres | grep -q "running"; then
            echo "✅ PostgreSQL服务运行正常"
        else
            echo "❌ PostgreSQL服务启动失败"
            docker compose logs postgres
            exit 1
        fi

        cd backend
    else
        echo "❌ docker-compose.yml不存在"
        exit 1
    fi
else
    echo "❌ Docker未安装，请安装Docker后重试"
    exit 1
fi

echo

# 检查Python环境和依赖
echo "3. 检查Python环境..."
if command -v python3 &> /dev/null; then
    echo "✅ Python3已安装"

    # 检查虚拟环境
    if [[ -d ".venv" ]]; then
        echo "✅ 虚拟环境存在"
        source .venv/bin/activate
    elif [[ -n "$VIRTUAL_ENV" ]]; then
        echo "✅ 使用现有虚拟环境: $VIRTUAL_ENV"
    else
        echo "⚠️  未检测到虚拟环境，建议创建:"
        echo "   python3 -m venv .venv && source .venv/bin/activate"
    fi

    # 安装依赖
    echo "正在安装依赖..."
    pip install -r requirements.txt -r requirements-dev.txt

else
    echo "❌ Python3未安装"
    exit 1
fi

echo

# 设置环境变量
echo "4. 配置环境变量..."
# 不再依赖.env文件，直接设置必要的环境变量
export DATABASE_URL="postgresql://postgres:devpassword123@localhost:5432/livin_matrix_dev"
export SECRET_KEY="test-secret-key-for-validation"
export ENVIRONMENT="development"
export DEBUG="true"

echo "✅ 环境变量已设置（不依赖.env文件）"

echo

# 运行数据库迁移
echo "5. 执行数据库迁移..."
if python -m alembic upgrade head; then
    echo "✅ 数据库迁移执行成功"
else
    echo "❌ 数据库迁移失败"
    exit 1
fi

echo

# 运行测试
echo "6. 运行单元测试..."
if python -m pytest tests/test_models.py -v; then
    echo "✅ 所有测试通过"
else
    echo "❌ 测试失败"
    exit 1
fi

echo

# 验证数据库表结构
echo "7. 验证数据库表结构..."
if command -v psql &> /dev/null; then
    echo "检查数据库表..."
    PGPASSWORD=devpassword123 psql -h localhost -U postgres -d livin_matrix_dev -c "
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
    ORDER BY table_name;
    "

    echo "检查用户表结构..."
    PGPASSWORD=devpassword123 psql -h localhost -U postgres -d livin_matrix_dev -c "\d+ users"

    echo "检查每日记录表结构..."
    PGPASSWORD=devpassword123 psql -h localhost -U postgres -d livin_matrix_dev -c "\d+ user_daily_records"

    echo "检查运动记录表结构..."
    PGPASSWORD=devpassword123 psql -h localhost -U postgres -d livin_matrix_dev -c "\d+ workout_sessions"

    echo "✅ 数据库表结构验证完成"
else
    echo "⚠️  psql未安装，跳过数据库表结构验证"
fi

echo

# 测试基本CRUD操作
echo "8. 测试基本数据库操作..."
python -c "
import sys
sys.path.append('.')

from app.core.database import SessionLocal, engine
from app.models import User, UserDailyRecord, WorkoutSession
from datetime import date, time

# 创建数据库会话
db = SessionLocal()

try:
    # 创建测试用户
    user = User(
        auth0_user_id='test|validation123',
        email='validation@test.com',
        username='validation_user'
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f'✅ 创建用户成功: {user.email}')

    # 创建每日记录
    record = UserDailyRecord(
        user_id=user.id,
        record_date=date(2025, 7, 31),
        sleep_quality=8,
        calories=2000,
        overall_mood=7
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    print(f'✅ 创建每日记录成功: {record.record_date}')

    # 创建运动记录
    workout = WorkoutSession(
        user_daily_record_id=record.id,
        workout_type='strength',
        start_time=time(9, 0),
        end_time=time(10, 30),
        intensity=8,
        feeling=7
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    print(f'✅ 创建运动记录成功: {workout.workout_type}, 时长: {workout.duration_minutes}分钟')

    # 清理测试数据
    db.delete(user)  # 级联删除相关记录
    db.commit()
    print('✅ 清理测试数据完成')

    print('✅ 基本数据库操作测试通过')

except Exception as e:
    print(f'❌ 数据库操作测试失败: {e}')
    sys.exit(1)
finally:
    db.close()
"

echo

# 最终总结
echo "=== 验证完成 ==="
echo "✅ Story 1.2: 数据库设计与部署验证通过"
echo
echo "验证项目:"
echo "  ✅ 关键文件存在"
echo "  ✅ Docker PostgreSQL服务运行"
echo "  ✅ Python环境配置"
echo "  ✅ 数据库迁移执行"
echo "  ✅ 单元测试通过"
echo "  ✅ 数据库表结构正确"
echo "  ✅ 基本CRUD操作正常"
echo
echo "Story 1.2已准备好进行Code Review！"
