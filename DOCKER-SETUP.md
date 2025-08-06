# Docker 部署指南

本项目完全使用Docker配置，无需.env文件。

## 📋 配置文件说明

### 基础配置
- `docker-compose.yml` - 基础服务定义
- `docker-compose.dev.yml` - 开发环境配置（包含密钥，不提交Git）
- `docker-compose.secrets.yml` - 生产环境配置（使用Docker Secrets）

### 模板文件
- `docker-compose.dev.template.yml` - 开发环境配置模板

## 🚀 快速开始

### 开发环境

1. **复制配置模板**：
   ```bash
   cp docker-compose.dev.template.yml docker-compose.dev.yml
   ```

2. **编辑开发配置**：
   ```bash
   # 编辑 docker-compose.dev.yml，填入实际密钥值
   vi docker-compose.dev.yml
   ```

3. **启动开发环境**：
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

### 生产环境

1. **创建Docker Secrets**：
   ```bash
   # 创建密钥文件
   echo "your_github_client_secret" | docker secret create fastapi_github_oauth_client_secret -
   echo "your_jwt_signing_key" | docker secret create fastapi_jwt_signing_key -
   echo "your_postgres_password" | docker secret create postgres_db_password -
   echo "your_app_secret_key" | docker secret create fastapi_session_secret_key -
   ```

2. **启动生产环境**：
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.secrets.yml up -d
   ```

## 🔧 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs backend

# 停止服务
docker-compose down

# 重建服务
docker-compose build --no-cache
```

## 🔒 安全说明

- ✅ 所有敏感配置都在Docker Compose文件中
- ✅ `docker-compose.dev.yml` 已加入 `.gitignore`
- ✅ 生产环境使用Docker Secrets加密存储
- ✅ 无需.env文件，避免密钥泄露风险

## 📝 密钥生成

```bash
# 生成随机密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 或使用OpenSSL
openssl rand -base64 32
```
