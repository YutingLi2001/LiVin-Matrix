# 邮件服务测试指南

## 方法1: 使用curl命令行测试

### 1. 启动后端服务
```bash
cd /Users/yutingli/Projects/LiVin-Matrix/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 测试邮件发送API
```bash
# 发送测试邮件
curl -X POST 'http://localhost:8000/api/v1/auth/email/test' \
  -H 'Content-Type: application/json' \
  -d '{"email": "your-email@example.com"}'

# 预期成功响应
{"message": "测试邮件发送成功！请检查收件箱"}
```

### 3. 测试用户注册流程（包含邮件发送）
```bash
# 注册新用户
curl -X POST 'http://localhost:8000/api/v1/auth/email/register' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "test@example.com",
    "password": "Test123456",
    "name": "测试用户"
  }'

# 预期成功响应
{"message": "注册成功！请检查邮箱并点击验证链接完成注册", "data": {"user_id": 1, "email_sent": true}}
```

## 方法2: 使用Python测试脚本

### 修改并运行测试脚本
```bash
# 1. 编辑测试脚本中的邮箱地址
nano /Users/yutingli/Projects/LiVin-Matrix/backend/simple_email_test.py

# 2. 将第31行的邮箱地址改为您的真实邮箱:
TEST_EMAIL = "your-real-email@gmail.com"

# 3. 运行测试
python3 simple_email_test.py
```

## 方法3: 使用Postman测试

### 创建Postman请求
1. **方法**: POST
2. **URL**: `http://localhost:8000/api/v1/auth/email/test`
3. **Headers**:
   - Content-Type: application/json
4. **Body** (raw JSON):
   ```json
   {
     "email": "your-email@example.com"
   }
   ```

## 期望的邮件内容

测试邮件会包含以下内容:
- **主题**: "LiVin Matrix - 邮件服务测试"
- **发件人**: "LiVin Matrix Team <noreply@resend.dev>"
- **内容**: 包含测试时间和服务状态的HTML邮件

## 故障排除

### 如果邮件发送失败:
1. **检查API Key**: 确认 `re_Ax8gF7Ds_FjVx8o5bDfzUfVdeFmotCp1z` 是否有效
2. **检查网络**: 确认服务器能访问 resend.com
3. **检查依赖**: 确认 resend SDK 已正确安装
4. **检查配置**: 验证所有环境变量设置正确

### 如果没有收到邮件:
1. **检查垃圾邮件文件夹**
2. **等待几分钟**: 邮件发送可能有延迟
3. **尝试不同邮箱**: 某些邮箱服务商可能有限制
4. **查看Resend控制台**: 访问 https://resend.com/logs 查看发送日志

## 成功标志

✅ **测试成功的标志**:
- API返回成功消息
- 邮箱收到测试邮件
- Resend控制台显示"delivered"状态

完成邮件测试后，您就可以继续测试完整的用户注册和验证流程了！