# Auth0认证功能用户测试指南

## 测试准备

### 1. Auth0应用配置

1. **创建Auth0账户和应用**：
   - 访问 [Auth0.com](https://auth0.com) 注册账户
   - 创建新的Single Page Application类型应用
   - 记录Domain、Client ID、和Audience信息

2. **配置应用设置**：
   ```
   Allowed Callback URLs: http://localhost:3000
   Allowed Logout URLs: http://localhost:3000
   Allowed Web Origins: http://localhost:3000
   ```

3. **启用邮箱/密码认证**：
   - 在Authentication > Database中启用Username-Password-Authentication

### 2. 环境配置

**前端环境变量** (frontend/.env)：
```bash
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id  
VITE_AUTH0_AUDIENCE=your-api-identifier
VITE_API_BASE_URL=http://localhost:8000
```

**后端环境变量** (backend/.env)：
```bash
DATABASE_URL=postgresql://postgres:devpassword123@localhost:5432/livin_matrix_dev
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_AUDIENCE=your-api-identifier
AUTH0_ALGORITHM=RS256
SECRET_KEY=your-secret-key-here
BACKEND_CORS_ORIGINS=http://localhost:3000
```

### 3. 启动服务

**启动后端**：
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**启动前端**：
```bash
cd frontend
npm install
npm run dev
```

## 用户测试场景

### 场景1：新用户注册和首次登录

**测试步骤**：
1. 访问 http://localhost:3000
2. 系统应自动重定向到登录页面
3. 点击"安全登录"按钮
4. 在Auth0登录页面点击"Sign up"
5. 使用新邮箱注册账户
6. 验证邮箱（如果启用了邮箱验证）
7. 完成登录，系统应重定向到Dashboard

**预期结果**：
- ✅ 成功注册新账户
- ✅ 首次登录时系统自动创建用户记录
- ✅ 登录后显示Dashboard页面
- ✅ 页面显示用户信息（邮箱、用户名等）

### 场景2：已有用户登录

**测试步骤**：
1. 访问 http://localhost:3000/login
2. 点击"安全登录"
3. 使用已有账户邮箱/密码登录
4. 验证是否成功进入Dashboard

**预期结果**：
- ✅ 登录成功，重定向到Dashboard
- ✅ 显示正确的用户信息
- ✅ 可以正常访问受保护页面

### 场景3：受保护页面访问控制

**测试步骤**：
1. 在未登录状态下访问：
   - http://localhost:3000/dashboard
   - http://localhost:3000/data-entry
2. 验证是否被重定向到登录页面
3. 登录后再次访问这些页面

**预期结果**：
- ✅ 未登录时无法访问受保护页面
- ✅ 自动重定向到登录页面
- ✅ 登录后可以正常访问

### 场景4：登出功能

**测试步骤**：
1. 在已登录状态下，在Dashboard页面找到登出按钮
2. 点击登出按钮
3. 验证是否成功登出
4. 尝试访问受保护页面

**预期结果**：
- ✅ 成功登出，清除登录状态
- ✅ 重定向到登录页面
- ✅ 无法再访问受保护页面

### 场景5：用户信息获取和显示

**测试步骤**：
1. 登录后访问Dashboard
2. 检查页面是否显示用户信息
3. 访问用户档案相关功能

**预期结果**：
- ✅ 正确显示用户邮箱
- ✅ 显示用户名（来自Auth0或邮箱前缀）
- ✅ API调用成功获取用户数据

### 场景6：API认证保护测试

**测试步骤**：
1. 打开浏览器开发者工具
2. 在未登录状态下，尝试直接访问API端点：
   ```
   GET http://localhost:8000/api/v1/auth/profile
   GET http://localhost:8000/api/v1/users/profile
   ```
3. 登录后再次尝试访问这些端点

**预期结果**：
- ✅ 未登录时API返回401/403错误
- ✅ 登录后API返回正确的用户数据
- ✅ 请求头包含有效的Authorization Bearer token

## 测试检查清单

### 功能性测试
- [ ] 新用户注册功能正常
- [ ] 已有用户登录功能正常
- [ ] 登出功能正常
- [ ] 受保护页面访问控制正常
- [ ] 用户信息获取和显示正常
- [ ] API认证保护正常

### 用户体验测试
- [ ] 登录流程流畅，无明显延迟
- [ ] 错误信息清晰易懂
- [ ] 页面加载状态提示适当
- [ ] 登录状态在页面刷新后保持
- [ ] 响应式设计在不同设备上正常工作

### 安全性测试
- [ ] JWT token在localStorage中安全存储
- [ ] 未授权访问被正确阻止
- [ ] 登出后token被正确清除
- [ ] API端点认证保护有效

## 常见问题排查

### 问题1：Auth0登录页面无法显示
- 检查VITE_AUTH0_DOMAIN和VITE_AUTH0_CLIENT_ID是否正确配置
- 检查Auth0应用的Callback URLs设置

### 问题2：登录成功但API调用失败
- 检查后端AUTH0_DOMAIN和AUTH0_AUDIENCE配置
- 检查CORS设置是否包含前端域名

### 问题3：页面刷新后登录状态丢失
- 检查Auth0 SDK配置是否正确
- 检查浏览器是否阻止了第三方cookie

### 问题4：数据库连接错误
- 确保PostgreSQL服务运行
- 检查DATABASE_URL配置是否正确
- 运行数据库迁移：`alembic upgrade head`

## 测试数据准备

建议准备以下测试账户：
1. **新用户**：使用从未注册过的邮箱测试注册流程
2. **已有用户**：使用已注册的测试邮箱测试登录流程
3. **边界情况**：测试特殊字符邮箱、长用户名等

## 性能测试指标

关注以下性能指标：
- 登录流程完成时间 < 3秒
- JWT验证时间 < 50ms
- 用户信息查询时间 < 100ms
- 页面首次加载时间 < 2秒