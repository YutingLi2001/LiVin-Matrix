# GitHub 配置指南

本目录包含LiVin Matrix项目的GitHub相关配置和文档。

## GitHub Secrets 配置

### 必需的Repository Secrets

项目CI/CD流水线需要以下GitHub Secrets配置：

#### 认证和安全密钥
- `SESSION_SECRET_KEY`: FastAPI会话密钥
- `JWT_SECRET_KEY`: JWT令牌签名密钥

#### 数据库配置
- `POSTGRES_PASSWORD`: PostgreSQL数据库密码

#### 第三方服务集成
- `RESEND_API_KEY`: Resend邮件服务API密钥
- `GITHUB_CLIENT_ID`: GitHub OAuth客户端ID
- `GITHUB_CLIENT_SECRET`: GitHub OAuth客户端密钥
- `GITHUB_REDIRECT_URI`: GitHub OAuth重定向URI

### 配置步骤

1. 前往仓库的 **Settings** > **Secrets and variables** > **Actions**
2. 点击 **New repository secret**
3. 输入Secret名称和值
4. 点击 **Add secret**

### 命名一致性验证

所有GitHub Secrets的命名都与Docker Secrets文件保持一致：

| Docker Secrets文件 | GitHub Repository Secrets | 状态 |
|-------------------|-------------------------|------|
| `POSTGRES_PASSWORD` | `POSTGRES_PASSWORD` | ✅ |
| `JWT_SECRET_KEY` | `JWT_SECRET_KEY` | ✅ |
| `SESSION_SECRET_KEY` | `SESSION_SECRET_KEY` | ✅ |
| `RESEND_API_KEY` | `RESEND_API_KEY` | ✅ |
| `GITHUB_CLIENT_ID` | `GITHUB_CLIENT_ID` | ✅ |
| `GITHUB_CLIENT_SECRET` | `GITHUB_CLIENT_SECRET` | ✅ |
| `GITHUB_REDIRECT_URI` | `GITHUB_REDIRECT_URI` | ✅ |

### 验证配置正确性

配置完成后，CI/CD流水线将能够：
1. 正确运行所有测试用例
2. 构建和部署服务
3. 执行安全检查和质量保证

### 安全注意事项

- 所有Secrets值都是敏感信息，不要在日志或代码中暴露
- 定期轮换密钥以确保安全 (建议每6个月)
- 使用强密码和加密安全的随机值
- 遵循最小权限原则，只授予必要的访问权限

---

**相关文档**: 更多安全策略详见 `docs/planning/security-architecture.md`
