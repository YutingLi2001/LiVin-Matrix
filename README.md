# LiVin Matrix 🌟

[![Frontend CI/CD](https://github.com/your-org/livin-matrix/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/your-org/livin-matrix/actions/workflows/frontend-ci.yml)
[![Backend CI/CD](https://github.com/your-org/livin-matrix/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/your-org/livin-matrix/actions/workflows/backend-ci.yml)
[![codecov](https://codecov.io/gh/your-org/livin-matrix/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/livin-matrix)

> 生活数据相关性分析平台 - 通过数据发现生活维度间的隐藏联系

LiVin Matrix 是一个现代化的全栈应用，帮助用户记录和分析生活各个维度的数据（睡眠、饮食、运动、情绪等），并通过相关性矩阵和热力图可视化展示这些维度之间的关联性，为用户提供个性化的生活洞察。

## ✨ 特性

- 🎯 **多维度数据录入** - 支持睡眠、饮食、运动、情绪、工作效率、社交等六大生活维度
- 📊 **相关性矩阵分析** - 智能计算各维度间的相关性，生成6x6矩阵热力图
- 🎨 **赛博朋克主题** - 深色主题界面，霓虹发光效果，Matrix风格视觉体验
- 📱 **响应式设计** - 完美适配桌面端和移动端
- 🔐 **安全认证** - 基于JWT的用户认证和授权
- 🚀 **高性能** - React + FastAPI + PostgreSQL 现代技术栈
- 🐳 **容器化部署** - Docker + Docker Compose 一键启动

## 🏗️ 技术架构

### 前端技术栈
- **React 18+** - 现代前端框架
- **TypeScript** - 类型安全的 JavaScript
- **Vite** - 快速构建工具
- **Tailwind CSS** - 实用优先的 CSS 框架
- **React Router** - 声明式路由管理

### 后端技术栈
- **FastAPI** - 现代高性能 Python Web 框架
- **SQLAlchemy** - Python SQL 工具包和 ORM
- **Pydantic** - 数据验证和序列化
- **PostgreSQL** - 强大的关系型数据库
- **Redis** - 高性能缓存和会话存储

### 基础设施
- **Docker** - 容器化部署
- **Nginx** - 反向代理和静态文件服务
- **GitHub Actions** - CI/CD 自动化

## 🚀 快速开始

### 环境要求

- **Node.js** 18+
- **Python** 3.9+
- **Docker** 20.x+
- **Docker Compose** 2.x+

### 一键启动

```bash
# 克隆项目
git clone https://github.com/your-org/livin-matrix.git
cd livin-matrix

# 启动所有服务
docker-compose up -d

# 等待服务启动完成，然后访问
# 前端: http://localhost:5173
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 本地开发

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 代码检查和格式化
npm run lint
npm run format
```

#### 后端开发

```bash
cd backend

# 设置开发环境
./setup.sh

# 或手动设置
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
pytest

# 代码检查和格式化
make lint
make format
```

## 📁 项目结构

```
livin-matrix/
├── frontend/                 # React 前端应用
│   ├── src/
│   │   ├── components/       # 可复用组件
│   │   ├── pages/           # 页面组件
│   │   ├── hooks/           # 自定义 Hooks
│   │   └── utils/           # 工具函数
│   ├── Dockerfile           # 前端容器配置
│   └── package.json
├── backend/                  # FastAPI 后端应用
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # Pydantic 模式
│   │   └── services/        # 业务逻辑
│   ├── tests/               # 测试文件
│   ├── Dockerfile           # 后端容器配置
│   └── requirements.txt
├── database/                 # 数据库相关
│   ├── migrations/          # 数据库迁移
│   └── scripts/             # 初始化脚本
├── deploy/                   # 部署配置
│   ├── k3s/                 # Kubernetes 配置
│   └── github-actions/      # CI/CD 工作流
├── docs/                     # 项目文档
├── docker-compose.yml        # 开发环境配置
└── README.md
```

## 🎯 功能说明

### 数据录入
- 支持六大生活维度数据录入
- 直观的评分滑块和数值输入
- 数据验证和格式化

### 相关性分析
- 智能计算维度间相关性系数
- 6x6 矩阵热力图可视化
- 实时数据更新和分析

### 可视化展示
- 赛博朋克风格热力图
- 交互式数据钻取
- 时间维度趋势分析

## 🔧 开发指南

### 代码规范

#### 前端
- 使用 TypeScript 进行类型检查
- 遵循 ESLint 和 Prettier 规范
- 组件使用函数式写法和 Hooks
- CSS 使用 Tailwind 实用类

#### 后端
- 遵循 PEP 8 Python 代码规范
- 使用 Black 进行代码格式化
- 类型注解和 Pydantic 模型验证
- 异步编程和依赖注入

### 测试策略

#### 前端测试
```bash
# 运行所有测试
npm test

# 监听模式
npm run test:watch

# 生成覆盖率报告
npm run test:coverage
```

#### 后端测试
```bash
# 运行所有测试
pytest

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 🚢 部署指南

### 开发环境

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 生产环境

```bash
# 使用生产配置启动
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 或使用 Kubernetes
kubectl apply -f deploy/k3s/manifests/
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发流程

1. 确保代码通过所有测试
2. 遵循代码规范和格式化要求
3. 更新相关文档
4. 通过 CI/CD 检查

## 📊 API 文档

启动后端服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔍 常见问题

### Q: 如何重置数据库？
```bash
docker-compose down -v
docker-compose up -d
```

### Q: 如何查看应用日志？
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f frontend
docker-compose logs -f backend
```

### Q: 如何更新依赖？
```bash
# 前端依赖
cd frontend && npm update

# 后端依赖
cd backend && pip-compile requirements.in
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 团队

- **项目负责人**: Yuting Li
- **前端开发**: [Frontend Dev]
- **后端开发**: [Backend Dev]
- **UI/UX 设计**: [Designer]

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和设计师！

---

<div align="center">
  <p>用 ❤️ 和 ☕ 制作</p>
  <p>© 2025 LiVin Matrix Team</p>
</div>
