# AI实现指导：项目初始化步骤

> 专为AI代理（如Claude Code）设计的详细项目搭建指南

## 🎯 指南目标

本文档提供LiVin Matrix项目的完整初始化步骤，包含所有必需的命令、配置文件和验证步骤，确保AI代理能够独立完成项目搭建。

## 📋 前置要求检查

在开始之前，请验证以下工具已安装：

```bash
# 检查Node.js版本（需要18+）
node --version
# 预期输出：v18.x.x 或更高

# 检查Python版本（需要3.9+）
python --version
# 预期输出：Python 3.9.x 或更高

# 检查Docker
docker --version
# 预期输出：Docker version 20.x.x 或更高

# 检查Git
git --version
# 预期输出：git version 2.x.x
```

## 🗂️ 第1步：创建项目目录结构

```bash
# 在项目根目录执行
cd /Users/yutingli/Projects/LiVin-Matrix

# 创建完整目录结构
mkdir -p frontend/src/{components/{ui,forms,matrix,layout},pages,hooks,contexts,utils,styles}
mkdir -p backend/app/{api/v1,core,models,schemas,services,tests}
mkdir -p deploy/{docker,k3s}
mkdir -p scripts
mkdir -p docs/ai-implementation-guide/templates

echo "✅ 目录结构创建完成"
```

## ⚛️ 第2步：初始化前端项目

### 2.1 创建前端应用

```bash
cd frontend

# 创建React TypeScript应用
npx create-react-app . --template typescript

# 等待安装完成后，安装额外依赖
npm install \
  tailwindcss@latest \
  @headlessui/react \
  @heroicons/react \
  recharts \
  react-hook-form \
  @hookform/resolvers/zod \
  zod \
  @auth0/auth0-react \
  lucide-react \
  framer-motion

# 安装开发依赖
npm install -D \
  @types/react \
  @types/react-dom \
  autoprefixer \
  postcss
```

### 2.2 配置Tailwind CSS

```bash
# 初始化Tailwind配置
npx tailwindcss init -p

# 创建tailwind.config.js配置文件
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 赛博朋克配色方案
        primary: {
          50: '#f3f0ff',
          100: '#e9e5ff',
          200: '#d8d0ff',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6', // 主品牌色
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
        matrix: {
          negative: '#ff0066',
          neutral: '#404040',
          positive: '#00ff88',
          strong: '#8b5cf6',
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'SF Mono', 'Consolas', 'monospace'],
        sans: ['Inter', 'Helvetica Neue', 'system-ui', 'sans-serif'],
        display: ['Orbitron', 'Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
EOF

# 更新src/index.css
cat > src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 全局样式 */
body {
  @apply bg-black text-white font-sans;
  margin: 0;
  font-family: 'Inter', 'Helvetica Neue', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 赛博朋克效果 */
.neon-glow {
  text-shadow: 0 0 10px currentColor;
}

.glass-effect {
  @apply bg-black bg-opacity-20 backdrop-blur-sm border border-purple-500 border-opacity-30;
}
EOF
```

### 2.3 创建基础组件结构

```bash
# 创建基础UI组件
cat > src/components/ui/Button.tsx << 'EOF'
import React from 'react';
import { cn } from '../../utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  ...props
}) => {
  const baseClasses = 'font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500';
  
  const variants = {
    primary: 'bg-purple-600 hover:bg-purple-700 text-white',
    secondary: 'bg-gray-800 hover:bg-gray-700 text-white border border-gray-600',
    ghost: 'hover:bg-gray-800 text-purple-400 hover:text-purple-300'
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button
      className={cn(baseClasses, variants[variant], sizes[size], className)}
      {...props}
    >
      {children}
    </button>
  );
};
EOF

# 创建工具函数
mkdir -p src/utils
cat > src/utils/cn.ts << 'EOF'
import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
EOF

# 安装clsx和tailwind-merge
npm install clsx tailwind-merge
```

## 🐍 第3步：初始化后端项目

### 3.1 创建Python虚拟环境

```bash
cd ../backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（macOS/Linux）
source venv/bin/activate

# 安装FastAPI及相关依赖
pip install \
  fastapi[all] \
  uvicorn[standard] \
  sqlalchemy \
  psycopg2-binary \
  alembic \
  pydantic \
  python-jose[cryptography] \
  python-multipart \
  bcrypt \
  pytest \
  pytest-asyncio \
  httpx

# 创建requirements.txt
pip freeze > requirements.txt
```

### 3.2 创建FastAPI应用结构

```bash
# 创建主应用文件
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

app = FastAPI(
    title="LiVin Matrix API",
    description="个人生活数据矩阵分析API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "LiVin Matrix API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
EOF

# 创建配置文件
cat > app/core/config.py << 'EOF'
from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "LiVin Matrix"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/livinmatrix"
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://localhost:3000",
    ]
    
    # Auth0配置
    AUTH0_DOMAIN: str = ""
    AUTH0_AUDIENCE: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF

# 创建基础API路由
mkdir -p app/api/v1
cat > app/api/v1/api.py << 'EOF'
from fastapi import APIRouter
from app.api.v1.endpoints import auth, dimensions, matrix

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(dimensions.router, prefix="/dimensions", tags=["dimensions"])
api_router.include_router(matrix.router, prefix="/matrix", tags=["matrix"])
EOF

# 创建基础端点目录
mkdir -p app/api/v1/endpoints
touch app/api/v1/endpoints/__init__.py
touch app/api/v1/__init__.py
touch app/core/__init__.py
touch app/__init__.py
```

### 3.3 创建数据库模型

```bash
# 创建数据库模型
cat > app/models/__init__.py << 'EOF'
from app.models.user import User
from app.models.dimension import DimensionRecord
EOF

cat > app/models/user.py << 'EOF'
from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth0_user_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100))
    timezone = Column(String(50), default="UTC")
    preferences = Column(JSONB, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
EOF

# 创建数据库连接配置
cat > app/core/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF
```

## 🐳 第4步：创建Docker开发环境

### 4.1 创建Docker Compose配置

```bash
cd ../deploy/docker

cat > docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  frontend:
    build:
      context: ../../frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ../../frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ../../backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ../../backend:/app
    environment:
      - DATABASE_URL=postgresql://livinmatrix:password@db:5432/livinmatrix
      - PYTHONPATH=/app
    depends_on:
      - db
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: livinmatrix
      POSTGRES_USER: livinmatrix
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ../../backend/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
EOF
```

### 4.2 创建Dockerfile

```bash
# 前端Dockerfile
cat > ../../frontend/Dockerfile.dev << 'EOF'
FROM node:18-alpine

WORKDIR /app

# 复制package文件
COPY package*.json ./
RUN npm install

# 复制源码
COPY . .

EXPOSE 3000

CMD ["npm", "start"]
EOF

# 后端Dockerfile
cat > ../../backend/Dockerfile.dev << 'EOF'
FROM python:3.9

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements并安装Python依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制源码
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF
```

## 🧪 第5步：创建启动脚本

```bash
cd ../../scripts

cat > setup-dev-environment.sh << 'EOF'
#!/bin/bash

echo "🚀 LiVin Matrix 开发环境设置"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请启动Docker Desktop"
    exit 1
fi

# 进入项目根目录
cd "$(dirname "$0")/.."

echo "📁 当前目录: $(pwd)"

# 构建和启动服务
echo "🐳 启动开发环境..."
docker-compose -f deploy/docker/docker-compose.dev.yml up --build -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f deploy/docker/docker-compose.dev.yml ps

# 检查健康状态
echo "🏥 检查API健康状态..."
curl -f http://localhost:8000/health || echo "后端未就绪"
curl -f http://localhost:3000 || echo "前端未就绪"

echo "✅ 开发环境设置完成！"
echo ""
echo "🌐 访问地址："
echo "   前端: http://localhost:3000"
echo "   后端API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo "   数据库: localhost:5432"
echo ""
echo "📝 有用的命令："
echo "   查看日志: docker-compose -f deploy/docker/docker-compose.dev.yml logs -f"
echo "   停止服务: docker-compose -f deploy/docker/docker-compose.dev.yml down"
echo "   重启服务: docker-compose -f deploy/docker/docker-compose.dev.yml restart"
EOF

chmod +x setup-dev-environment.sh
```

## ✅ 第6步：验证安装

```bash
# 创建验证脚本
cat > verify-setup.sh << 'EOF'
#!/bin/bash

echo "🔍 验证项目设置..."

# 检查目录结构
echo "📁 检查目录结构..."
REQUIRED_DIRS=(
    "frontend/src/components"
    "backend/app/api"
    "deploy/docker"
    "docs/ai-implementation-guide"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✅ $dir"
    else
        echo "  ❌ $dir 缺失"
    fi
done

# 检查关键文件
echo ""
echo "📄 检查关键文件..."
REQUIRED_FILES=(
    "frontend/package.json"
    "frontend/tailwind.config.js"
    "backend/requirements.txt"
    "backend/app/main.py"
    "deploy/docker/docker-compose.dev.yml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file 缺失"
    fi
done

echo ""
echo "🎯 下一步："
echo "1. 运行 ./scripts/setup-dev-environment.sh 启动开发环境"
echo "2. 验证前端和后端服务正常运行"
echo "3. 开始第一个Epic的开发任务"

EOF

chmod +x verify-setup.sh
```

## 📋 成功标准

完成本步骤后，您应该能够：

1. ✅ **目录结构完整** - 所有必需的目录都已创建
2. ✅ **前端项目就绪** - React + TypeScript + Tailwind配置完成
3. ✅ **后端项目就绪** - FastAPI + SQLAlchemy基础架构完成
4. ✅ **Docker环境就绪** - 开发环境可以一键启动
5. ✅ **脚本工具就绪** - 自动化启动和验证脚本可用

## 🔧 故障排除

### 常见问题

**Q: npm install失败**
```bash
# 清理缓存重试
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Q: Python依赖安装失败**
```bash
# 升级pip重试
pip install --upgrade pip
pip install -r requirements.txt
```

**Q: Docker构建失败**
```bash
# 清理Docker缓存
docker system prune -a
```

## 📚 下一步

项目初始化完成后，请继续查看：
- [02-component-templates.md](./02-component-templates.md) - React组件模板库
- [03-api-patterns.md](./03-api-patterns.md) - FastAPI接口模式
- [04-database-operations.md](./04-database-operations.md) - 数据库操作样例

---

*本文档专为AI代理优化，包含完整的命令和配置，确保项目可以自动化搭建。*