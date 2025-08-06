# 安全配置指南

## 环境变量配置

本项目使用环境变量管理敏感配置信息。**绝不要将实际的 `.env` 文件提交到 git 仓库。**

### 快速设置

1. 运行设置脚本：
   ```bash
   ./scripts/setup-env.sh
   ```

2. 编辑创建的 `.env` 文件，填入实际配置值：
   - `backend/.env` - 数据库凭据、API 密钥、JWT 密钥
   - `frontend/.env` - GitHub OAuth 客户端 ID、API 端点

### 手动设置

如果您偏好手动设置：

1. 复制模板文件：
   ```bash
   cp backend/.env.template backend/.env
   cp frontend/.env.template frontend/.env
   ```

2. 编辑文件并填入实际凭据

### 必需的敏感配置

#### 后端 (.env)
- `DATABASE_URL` - PostgreSQL 连接字符串
- `SECRET_KEY` - 应用程序密钥（生成随机值）
- `JWT_SECRET_KEY` - JWT 签名密钥（生成随机值）
- `GITHUB_CLIENT_SECRET` - GitHub OAuth 应用密钥

#### 前端 (.env)
- `VITE_GITHUB_CLIENT_ID` - GitHub OAuth 应用客户端 ID

### 生成安全密钥

生产环境请生成安全的随机密钥：

```bash
# 生成 SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 生成 JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 安全最佳实践

1. **绝不提交 `.env` 文件** - 它们已在 `.gitignore` 中被排除
2. **不同环境使用不同凭据** - 开发/测试/生产环境应使用独立的密钥
3. **定期轮换密钥** - 特别是团队成员变动时
4. **使用强随机密码** - 密钥至少 32 个字符
5. **限制访问权限** - 仅与需要的团队成员分享凭据

## Git-crypt 替代方案（高级）

如需在 git 中加密存储密钥以便团队协作，可考虑使用 git-crypt：

```bash
# 安装 git-crypt
brew install git-crypt  # macOS
# 或 apt-get install git-crypt  # Ubuntu

# 初始化 git-crypt
git-crypt init
git-crypt add-gpg-user YOUR_GPG_KEY_ID
```

这样可以在保持仓库公开的同时，在仓库中加密存储敏感信息。
