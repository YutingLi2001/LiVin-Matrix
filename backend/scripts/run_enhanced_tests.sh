#!/bin/bash
# 增强测试套件运行脚本

set -e

echo "🧪 LiVin Matrix 增强测试套件"
echo "================================"

# 确保在正确的目录
cd "$(dirname "$0")/.."

# 检查虚拟环境
if [[ -z "$VIRTUAL_ENV" ]] && [[ ! -d ".venv" ]]; then
    echo "⚠️  警告: 未检测到虚拟环境"
    echo "建议创建虚拟环境: python -m venv .venv && source .venv/bin/activate"
fi

# 安装测试依赖
echo "📦 安装测试依赖..."
pip install -r requirements-test.txt

echo ""
echo "🔧 测试环境信息:"
echo "Python版本: $(python --version)"
echo "Pytest版本: $(pytest --version)"
echo "当前目录: $(pwd)"
echo ""

# 运行不同类型的测试
run_test_suite() {
    local test_type=$1
    local test_files=$2
    local description=$3

    echo "🏃 运行 $description..."
    echo "----------------------------------------"

    if pytest $test_files -m "$test_type" --tb=short -v; then
        echo "✅ $description 通过"
    else
        echo "❌ $description 失败"
        return 1
    fi
    echo ""
}

# 检查命令行参数
case "${1:-all}" in
    "migration"|"migrations")
        echo "🔄 仅运行迁移测试..."
        pytest tests/test_migrations.py -v
        ;;

    "performance"|"perf")
        echo "⚡ 仅运行性能测试..."
        pytest tests/test_performance.py::TestDatabasePerformance -v --benchmark-enable
        ;;

    "concurrency"|"concurrent")
        echo "🔄 仅运行并发测试..."
        pytest tests/test_concurrency.py -v
        ;;

    "benchmark"|"bench")
        echo "📊 运行基准测试..."
        pytest tests/test_performance.py -v --benchmark-enable --benchmark-only
        ;;

    "quick"|"fast")
        echo "⚡ 快速测试（跳过慢速测试）..."
        pytest tests/ -v -m "not slow" --benchmark-disable
        ;;

    "all"|*)
        echo "🎯 运行完整测试套件..."

        # 1. 迁移集成测试
        echo "1️⃣ 迁移集成测试"
        pytest tests/test_migrations.py -v

        echo ""

        # 2. 性能基准测试
        echo "2️⃣ 性能基准测试"
        pytest tests/test_performance.py -v --benchmark-disable

        echo ""

        # 3. 并发访问测试
        echo "3️⃣ 并发访问测试"
        pytest tests/test_concurrency.py -v

        echo ""

        # 4. 其他现有测试（如果存在）
        if ls tests/test_*.py 2>/dev/null | grep -v -E "(migrations|performance|concurrency)" > /dev/null; then
            echo "4️⃣ 其他集成测试"
            pytest tests/ -v --ignore=tests/test_migrations.py --ignore=tests/test_performance.py --ignore=tests/test_concurrency.py --benchmark-disable
        fi
        ;;
esac

echo ""
echo "📈 测试完成！"
echo ""
echo "💡 其他测试选项:"
echo "  $0 migration     - 仅迁移测试"
echo "  $0 performance   - 仅性能测试"
echo "  $0 concurrency   - 仅并发测试"
echo "  $0 benchmark     - 仅基准测试"
echo "  $0 quick         - 快速测试"
echo "  $0 all          - 完整测试套件（默认）"
echo ""
echo "📊 生成测试报告:"
echo "  覆盖率报告: htmlcov/index.html"
echo "  基准测试: pytest tests/test_performance.py --benchmark-enable --benchmark-save=baseline"
