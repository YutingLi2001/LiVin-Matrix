# LiVin Matrix Backend Makefile

.PHONY: help install dev test lint format clean

# 默认目标
help:
	@echo "LiVin Matrix Backend 开发命令:"
	@echo ""
	@echo "  install     安装依赖"
	@echo "  dev         启动开发服务器"
	@echo "  test        运行测试"
	@echo "  lint        代码检查"
	@echo "  format      代码格式化"
	@echo "  clean       清理缓存文件"
	@echo ""

# 安装依赖
install:
	@echo "📦 安装依赖..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# 启动开发服务器
dev:
	@echo "🚀 启动开发服务器..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
test:
	@echo "🧪 运行测试..."
	pytest -v --cov=app --cov-report=html

# 代码检查
lint:
	@echo "🔍 代码检查..."
	flake8 app tests
	mypy app
	black --check app tests
	isort --check-only app tests

# 代码格式化
format:
	@echo "✨ 代码格式化..."
	black app tests
	isort app tests

# 清理缓存文件
clean:
	@echo "🧹 清理缓存文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/