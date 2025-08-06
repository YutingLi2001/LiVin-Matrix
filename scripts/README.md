# LIVIN-MATRIX 开发脚本

这个目录包含了LIVIN-MATRIX项目的各种开发和部署脚本，所有脚本都支持Mac双击运行。

## 📁 目录结构

```
scripts/
├── README.md           # 本说明文档
├── services/          # 服务管理脚本 (Docker)
├── dev/               # 开发环境脚本
├── build/             # 构建相关脚本
└── deploy/            # 部署相关脚本（待扩展）
```

## 🐳 服务管理脚本 (services/)

### 一键启动脚本

#### `start-all.command` - 启动所有服务
- **功能**: 一键启动完整的开发环境
- **包含服务**: PostgreSQL, Redis, 后端API, 前端应用
- **自动功能**:
  - Docker环境检查
  - 端口冲突检测和清理
  - 服务健康检查和等待
  - 环境变量配置
- **访问地址**: http://localhost:3000 (前端), http://localhost:8000 (后端API)

### 单独服务启动脚本

#### `start-database.command` - 启动数据库服务
- **功能**: 仅启动数据库相关服务
- **包含服务**: PostgreSQL (端口5432), Redis (端口6379)
- **用途**: 后端开发时使用，无需启动前端

#### `start-backend.command` - 启动后端服务
- **功能**: 启动数据库依赖 + 后端API
- **包含服务**: PostgreSQL, Redis, FastAPI后端
- **自动功能**:
  - 数据库迁移执行
  - API健康检查
- **访问地址**: http://localhost:8000 (API), http://localhost:8000/docs (文档)

#### `start-frontend.command` - 启动前端服务
- **功能**: 启动前端开发服务器 (Docker模式)
- **包含服务**: React/Vite前端 (端口3000)
- **自动功能**:
  - 后端依赖检查
  - 热重载支持
- **访问地址**: http://localhost:3000

### 服务管理脚本

#### `stop-all.command` - 停止所有服务
- **功能**: 优雅停止所有Docker服务
- **清理选项**:
  - 仅停止服务（保留数据）
  - 清理网络
  - 清理所有数据（⚠️ 删除数据库数据）
- **安全特性**: 端口释放检查

#### `restart-all.command` - 重启所有服务
- **功能**: 多种重启模式
- **重启选项**:
  - 优雅重启（推荐）
  - 强制重启
  - 完全重建（重新构建镜像）
  - 单独重启后端/前端
- **健康检查**: 重启后自动验证服务状态

#### `status-all.command` - 查看服务状态
- **功能**: 全面的服务状态检查
- **检查内容**:
  - Docker容器状态
  - 服务健康检查
  - 端口占用情况
  - 资源使用统计
  - 快速诊断建议
- **交互特性**: 支持状态刷新

#### `logs-all.command` - 查看服务日志
- **功能**: 交互式日志查看工具
- **查看选项**:
  - 所有服务实时日志
  - 单独服务日志
  - 错误日志筛选
  - 启动日志查看
  - 日志内容搜索
  - 导出日志到文件
- **交互特性**: 菜单式操作界面

## 🚀 开发脚本 (dev/)

### `start-frontend.command` - 启动前端开发服务器
- **功能**: 启动Vite开发服务器
- **端口**: http://localhost:5173
- **自动功能**:
  - 检测并安装缺失依赖
  - 清理端口占用
  - 提供启动状态反馈

### `stop-frontend.command` - 停止前端开发服务器
- **功能**: 强制停止所有相关进程
- **智能检测**:
  - Vite进程
  - Node.js相关进程
  - 端口5173占用情况
- **安全关闭**: 先优雅关闭，再强制关闭

### `frontend-lint.command` - 前端代码检查
- **功能**: 运行代码质量检查
- **包含检查**:
  - TypeScript类型检查
  - ESLint代码规范
  - Prettier代码格式
- **结果汇总**: 显示所有检查的通过/失败状态

## 🏗️ 构建脚本 (build/)

### `build-frontend.command` - 构建前端应用
- **功能**: 构建生产版本
- **流程**:
  1. 检查依赖安装
  2. 运行代码质量检查
  3. 清理旧构建文件
  4. 执行构建
  5. 显示构建统计
- **输出**: `frontend/dist/` 目录

## 📋 使用指南

### 双击运行
所有 `.command` 文件都可以直接在Finder中双击运行，无需使用终端。

### 典型开发工作流

#### 🎯 全栈开发 (推荐)
1. **启动完整环境**
   ```
   双击: services/start-all.command
   ```

2. **检查服务状态**
   ```
   双击: services/status-all.command
   ```

3. **查看日志** (如有问题)
   ```
   双击: services/logs-all.command
   ```

4. **代码检查** (提交前)
   ```
   双击: dev/frontend-lint.command
   ```

5. **结束开发**
   ```
   双击: services/stop-all.command
   ```

#### 🔧 后端开发模式
1. **启动后端服务**
   ```
   双击: services/start-backend.command
   ```

2. **使用外部前端工具**
   ```
   双击: dev/start-frontend.command (原生模式)
   ```

#### 🎨 前端开发模式
1. **启动数据库**
   ```
   双击: services/start-database.command
   ```

2. **启动前端**
   ```
   双击: services/start-frontend.command
   ```

#### 🚀 快速服务管理
- **重启服务**: `services/restart-all.command`
- **查看状态**: `services/status-all.command`
- **查看日志**: `services/logs-all.command`

### 权限说明
所有脚本已设置可执行权限 (`chmod +x`)，可直接运行。

## 🔧 自定义和扩展

### 添加新脚本
1. 在相应目录创建 `.command` 文件
2. 设置可执行权限: `chmod +x your-script.command`
3. 在此README中更新文档

### 脚本模板
```bash
#!/bin/bash
# 脚本描述

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 设置终端标题
echo -n -e "\033]0;你的脚本标题\007"

# 脚本逻辑
echo "脚本内容..."

# 等待用户按键
echo "按任意键关闭此窗口..."
read -n 1
```

## 🚫 注意事项

### Docker服务脚本
- 确保Docker Desktop已安装并运行
- 首次启动会下载镜像，可能需要较长时间
- 服务启动后会持续在后台运行，关闭终端不影响服务
- 数据库数据持久化存储在Docker卷中
- 需要确保必要端口未被占用 (3000, 5432, 6379, 8000)

### 开发脚本
- 确保Node.js和npm已正确安装
- 首次运行可能需要安装依赖，请耐心等待
- 如遇权限问题，请检查脚本的可执行权限
- 建议在代码提交前运行lint检查

### 故障排除
- 服务启动失败: 检查Docker状态和端口占用
- 权限错误: 运行 `chmod +x scripts/services/*.command`
- 端口冲突: 使用status脚本检查端口占用情况
- 服务异常: 使用logs脚本查看错误日志

## 📚 相关文档

- [前端开发文档](../docs/frontend-spec.md)
- [项目架构文档](../docs/architecture.md)
- [开发日志](../docs/developmentjournal.md)

---

💡 **提示**: 如果需要添加新的脚本或修改现有脚本，请更新此README文档以保持同步。
