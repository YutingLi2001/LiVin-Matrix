# 3. 技术栈决策 (Technology Stack Decisions)

## 3.1 前端技术栈

**核心框架选择：**
```typescript
{
  "framework": "React 18+",           // 现代前端标准，生态成熟
  "language": "TypeScript",           // 类型安全，提升开发效率
  "styling": "Tailwind CSS",          // 快速开发，高度可定制
  "charts": "Recharts",               // React原生图表库，简化配置
  "forms": "React Hook Form",         // 成熟稳定的表单管理
  "state": "React Context + useReducer", // 避免Redux复杂性
  "routing": "React Router",          // 标准路由解决方案
  "icons": "Lucide React",            // 简洁稳定的图标库
  "animation": "Framer Motion (渐进式)" // 高质量动画库，渐进引入
}
```

**选择理由：**
- **React生态成熟**：丰富的组件库和工具支持
- **TypeScript类型安全**：减少运行时错误，提升开发体验
- **Tailwind快速开发**：避免编写大量自定义CSS
- **渐进式动画策略**：Framer Motion按需引入，避免影响核心功能

## 3.2 后端技术栈

**API框架选择：**
```python
{
  "framework": "FastAPI",             # 现代Python web框架，自动API文档
  "orm": "SQLAlchemy",                # 成熟的ORM，支持数据迁移
  "validation": "Pydantic",           # 类型安全，自动验证
  "auth": "GitHub OAuth + JWT",       # 免费OAuth方案，零月费成本
  "database": "PostgreSQL 13+",      # 关系型数据，支持JSON字段
  "migration": "Alembic"              # 版本控制数据库schema变更
}
```

**选择理由：**
- **FastAPI性能优秀**：异步支持，自动API文档生成
- **SQLAlchemy成熟稳定**：丰富的ORM功能，支持复杂查询
- **GitHub OAuth零成本**：100%免费认证方案，节省$35/月，保持企业级安全标准
- **PostgreSQL功能强大**：支持JSON字段，满足灵活数据模型需求

## 3.3 基础设施技术栈

**零成本部署方案：**
```yaml
frontend_hosting: "GitHub Pages"     # 免费静态网站托管
backend_deployment: "AWS API Gateway + EKS"  # 免费tier
database: "AWS RDS PostgreSQL"       # 免费tier 20GB
file_storage: "AWS S3"               # 免费tier 5GB
containerization: "Docker + Docker Compose"  # 开发环境一致性
orchestration: "K3s"                 # 轻量Kubernetes，学习容器编排
ci_cd: "GitHub Actions"              # 代码到生产的自动化流水线
```

**架构优势：**
- **完全免费运营**：充分利用各平台免费tier
- **学习价值丰富**：涵盖容器化、编排、CI/CD完整流程
- **生产就绪**：基于成熟的云服务，具备生产级可靠性
