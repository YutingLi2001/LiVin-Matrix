# LIVIN-MATRIX 安全设置指南

## 🔐 环境变量安全配置

为了确保敏感信息的安全，本项目使用本地环境变量文件来管理密钥和配置。

### 快速设置

1. **复制环境变量模板**
   ```bash
   cp .env.local.template .env.local
   ```

2. **编辑配置文件**
   ```bash
   # 使用您喜欢的编辑器打开 .env.local
   nano .env.local  # 或 vim .env.local
   ```

3. **填入实际配置**
   根据您的实际环境填入以下值：
   
   ```bash
   # 数据库配置
   POSTGRES_PASSWORD=your_secure_postgres_password_here
   
   # GitHub OAuth 配置
   GITHUB_CLIENT_ID=your_github_client_id_here
   GITHUB_CLIENT_SECRET=your_github_client_secret_here
   
   # 邮件服务配置
   RESEND_API_KEY=your_resend_api_key_here
   
   # JWT 配置
   JWT_SECRET_KEY=your_jwt_secret_key_here
   SESSION_SECRET_KEY=your_session_secret_key_here
   ```

### 🛡️ 安全原则

#### 1. 文件权限保护
```bash
# 确保环境变量文件只有您可以读取
chmod 600 .env.local
```

#### 2. Git 忽略规则
`.env.local` 文件已经被添加到 `.gitignore` 中，确保不会被提交到版本控制。

#### 3. 强密码建议
- 使用至少32位的随机字符串作为JWT密钥
- 数据库密码应包含大小写字母、数字和特殊字符
- 定期轮换密钥

### 🔑 获取必要的密钥

#### GitHub OAuth
1. 访问 [GitHub Developer Settings](https://github.com/settings/developers)
2. 创建新的 OAuth App
3. 设置回调URL: `http://localhost:8000/api/v1/auth/github/callback`
4. 复制 Client ID 和 Client Secret

#### Resend API
1. 访问 [Resend Dashboard](https://resend.com/api-keys)
2. 创建新的 API Key
3. 复制密钥到配置文件

#### JWT 密钥生成
```bash
# 生成安全的JWT密钥
openssl rand -hex 32

# 或使用Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 🚀 启动服务

配置完成后，您可以使用以下脚本启动服务：

```bash
# 启动所有服务
./scripts/services/start-all.command

# 或仅启动特定服务
./scripts/services/start-database.command
./scripts/services/start-backend.command
./scripts/services/start-frontend.command
```

### 🔧 故障排除

#### 环境变量未加载
- 确保 `.env.local` 文件存在于项目根目录
- 检查文件内容格式（键=值，无空格）
- 验证文件权限

#### 服务启动失败
- 检查所有必需的环境变量是否已设置
- 验证密钥的有效性
- 查看服务日志: `docker-compose logs [service_name]`

### 🏢 生产环境建议

对于生产环境，建议使用：
1. **Docker Secrets** (已配置在 `docker-compose.secrets.yml`)
2. **环境变量注入** (通过CI/CD管道)
3. **密钥管理服务** (如AWS Secrets Manager、Azure Key Vault)

### 📞 获取帮助

如果遇到安全相关问题：
1. 检查本文档的故障排除部分
2. 查看项目的issue tracker
3. 确保不在issue中包含任何敏感信息

---

⚠️ **重要提醒**: 永远不要在代码、文档或issue中包含真实的密钥或密码！