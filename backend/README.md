# 后端API服务

## 技术栈

- **FastAPI** - 现代高性能 Python Web 框架
- **SQLAlchemy** - Python SQL 工具包和 ORM
- **Pydantic** - 数据验证和序列化
- **Uvicorn** - ASGI 服务器
- **pytest** - 测试框架

## 开发命令

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
pytest

# 代码格式化
black app/
isort app/
```

## 项目结构

```
app/
├── api/           # API路由
├── core/          # 核心配置
├── models/        # 数据模型
├── schemas/       # Pydantic 模式
├── services/      # 业务逻辑
└── main.py        # 应用入口
tests/             # 测试文件
requirements.txt   # Python依赖
```

## 环境要求

- Python 3.9+
- pip

## API 文档

开发环境: http://localhost:8000/docs