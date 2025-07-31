# AI实现指导文档库

> 专为AI代理（如Claude Code）设计的LiVin Matrix项目实现指南

## 📚 文档概览

本指导库提供完整的代码模板、实现样例和最佳实践，帮助AI代理独立实现LiVin Matrix项目的各个组件。

### 📋 文档清单

| 文档 | 状态 | 描述 |
|------|------|------|
| [01-project-setup.md](./01-project-setup.md) | ✅ 完成 | 项目初始化完整步骤 |
| [02-component-templates.md](./02-component-templates.md) | 🚧 待创建 | React组件模板库 |
| [03-api-patterns.md](./03-api-patterns.md) | 🚧 待创建 | FastAPI接口模式 |
| [04-database-operations.md](./04-database-operations.md) | 🚧 待创建 | 数据库操作样例 |
| [05-testing-examples.md](./05-testing-examples.md) | 🚧 待创建 | 测试代码样例 |
| [06-deployment-scripts.md](./06-deployment-scripts.md) | 🚧 待创建 | 部署配置模板 |
| [reference-projects.md](./reference-projects.md) | 🚧 待创建 | 参考项目清单 |

## 🎯 使用指南

### 对于AI代理

1. **项目初始化**: 从 `01-project-setup.md` 开始
2. **组件开发**: 使用 `02-component-templates.md` 中的模板
3. **API开发**: 参考 `03-api-patterns.md` 的接口模式
4. **数据库操作**: 遵循 `04-database-operations.md` 的样例
5. **测试实现**: 使用 `05-testing-examples.md` 的测试模式

### 对于人工开发者

1. 可以直接使用模板快速开发
2. 参考最佳实践避免常见问题
3. 使用代码样例作为起点自定义实现

## 🔍 快速查找

### 按技术栈分类

**前端 (React + TypeScript)**
- 组件模板: `02-component-templates.md`
- 状态管理: `templates/contexts/`
- 样式系统: `templates/styles/`

**后端 (FastAPI + Python)**
- API路由: `03-api-patterns.md`
- 数据模型: `04-database-operations.md`
- 业务逻辑: `templates/services/`

**部署 (Docker + K3s)**
- 配置文件: `06-deployment-scripts.md`
- CI/CD: `templates/github-actions/`

### 按功能分类

**核心功能**
- 用户认证: `03-api-patterns.md#认证模块`
- 数据录入: `02-component-templates.md#表单组件`
- 矩阵可视化: `02-component-templates.md#图表组件`
- 相关性分析: `04-database-operations.md#分析查询`

**基础设施**
- 项目搭建: `01-project-setup.md`
- 数据库设计: `04-database-operations.md#Schema设计`
- 测试框架: `05-testing-examples.md`
- 部署配置: `06-deployment-scripts.md`

## 🏗️ 架构对应关系

本指导库与主要架构文档的对应关系：

```
architecture.md (设计) → ai-implementation-guide (实现)
├── 前端架构设计 → 02-component-templates.md
├── 后端架构设计 → 03-api-patterns.md
├── 数据架构设计 → 04-database-operations.md
├── 部署架构设计 → 06-deployment-scripts.md
└── 测试策略 → 05-testing-examples.md
```

## ⚡ 快速开始

### 新项目启动
```bash
# 1. 跟随项目初始化指南
docs/ai-implementation-guide/01-project-setup.md

# 2. 运行自动化设置脚本
./scripts/setup-dev-environment.sh

# 3. 验证环境
./scripts/verify-setup.sh
```

### 组件开发
```bash
# 1. 查看组件模板
docs/ai-implementation-guide/02-component-templates.md

# 2. 使用模板创建组件
cp templates/components/BaseComponent.tsx src/components/NewComponent.tsx
```

### API开发
```bash
# 1. 查看API模式
docs/ai-implementation-guide/03-api-patterns.md

# 2. 使用模板创建路由
cp templates/api/base_router.py backend/app/api/v1/endpoints/new_endpoint.py
```

## 🎨 模板库

### 代码模板目录
```
templates/
├── components/          # React组件模板
│   ├── ui/             # 基础UI组件
│   ├── forms/          # 表单组件
│   ├── charts/         # 图表组件
│   └── layouts/        # 布局组件
├── api/                # FastAPI模板
│   ├── routers/        # 路由模板
│   ├── models/         # 数据模型模板
│   └── services/       # 业务逻辑模板
├── database/           # 数据库模板
│   ├── migrations/     # 迁移脚本
│   └── queries/        # 查询样例
└── deployment/         # 部署模板
    ├── docker/         # Docker配置
    └── k3s/           # K3s配置
```

## 🔧 工具和脚本

### 自动化工具
- `scripts/setup-dev-environment.sh` - 开发环境一键搭建
- `scripts/generate-component.sh` - 组件快速生成
- `scripts/create-api-endpoint.sh` - API端点快速创建
- `scripts/run-tests.sh` - 测试执行脚本

### 验证工具
- `scripts/verify-setup.sh` - 项目设置验证
- `scripts/check-code-quality.sh` - 代码质量检查
- `scripts/validate-api.sh` - API接口验证

## 📈 使用统计

随着项目进展，请更新以下使用情况：

- [ ] 项目初始化指南使用
- [ ] 组件模板使用情况
- [ ] API模式采用情况
- [ ] 问题和改进点记录

## 🤝 贡献指南

### 添加新模板
1. 在相应的 `templates/` 目录中添加模板文件
2. 在对应的指导文档中添加使用说明
3. 更新本README的模板清单

### 改进现有模板
1. 基于实际使用经验优化模板
2. 添加更多错误处理和边界情况
3. 补充注释和使用示例

---

**最后更新**: 2024年
**维护者**: BMad Master
**用途**: AI代理实现指导