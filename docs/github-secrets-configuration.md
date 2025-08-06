# GitHub Secrets 配置指南

## 概述
本文档说明了LiVin-Matrix项目CI/CD流水线需要配置的GitHub Secrets，以确保与Docker Secrets的命名一致性。

## 必需的GitHub Secrets配置

### 认证和安全密钥
- `SESSION_SECRET_KEY`: FastAPI会话密钥（原FASTAPI_SECRET_KEY）
- `JWT_SECRET_KEY`: JWT令牌签名密钥

### 数据库配置
- `POSTGRES_PASSWORD`: PostgreSQL数据库密码

### 第三方服务集成
- `RESEND_API_KEY`: Resend邮件服务API密钥
- `GITHUB_CLIENT_ID`: GitHub OAuth客户端ID（原GH_OAUTH_CLIENT_ID）
- `GITHUB_CLIENT_SECRET`: GitHub OAuth客户端密钥（原GH_OAUTH_CLIENT_SECRET）
- `GITHUB_REDIRECT_URI`: GitHub OAuth重定向URI

## 配置说明

### 在GitHub Repository中设置Secrets
1. 前往仓库的 **Settings** > **Secrets and variables** > **Actions**
2. 点击 **New repository secret**
3. 输入Secret名称和值
4. 点击 **Add secret**

### 命名一致性验证
所有GitHub Secrets的命名都与Docker Secrets文件保持一致：

| Docker Secrets文件 | GitHub Repository Secrets |
|-------------------|-------------------------|
| `POSTGRES_PASSWORD` | `POSTGRES_PASSWORD` ✅ |
| `JWT_SECRET_KEY` | `JWT_SECRET_KEY` ✅ |
| `SESSION_SECRET_KEY` | `SESSION_SECRET_KEY` ✅ |
| `RESEND_API_KEY` | `RESEND_API_KEY` ✅ |
| `GITHUB_CLIENT_ID` | `GITHUB_CLIENT_ID` ✅ |
| `GITHUB_CLIENT_SECRET` | `GITHUB_CLIENT_SECRET` ✅ |
| `GITHUB_REDIRECT_URI` | `GITHUB_REDIRECT_URI` ✅ |

## 安全注意事项
- 所有Secrets值都是敏感信息，不要在日志或代码中暴露
- 定期轮换密钥以确保安全
- 使用强密码和加密安全的随机值

## 验证配置
配置完成后，CI/CD流水线将能够：
1. 正确运行98个测试用例
2. 构建和部署服务
3. 执行安全检查和质量保证

更新日期: 2025-08-06
