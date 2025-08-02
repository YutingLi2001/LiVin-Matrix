# LIVIN-MATRIX 开发脚本

这个目录包含了LIVIN-MATRIX项目的各种开发和部署脚本，所有脚本都支持Mac双击运行。

## 📁 目录结构

```
scripts/
├── README.md           # 本说明文档
├── dev/               # 开发环境脚本
├── build/             # 构建相关脚本
└── deploy/            # 部署相关脚本（待扩展）
```

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

1. **开始开发**
   ```
   双击: dev/start-frontend.command
   ```

2. **代码检查** (提交前)
   ```
   双击: dev/frontend-lint.command
   ```

3. **构建测试**
   ```
   双击: build/build-frontend.command
   ```

4. **结束开发**
   ```
   双击: dev/stop-frontend.command
   ```

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

- 确保Node.js和npm已正确安装
- 首次运行可能需要安装依赖，请耐心等待
- 如遇权限问题，请检查脚本的可执行权限
- 建议在代码提交前运行lint检查

## 📚 相关文档

- [前端开发文档](../docs/frontend-spec.md)
- [项目架构文档](../docs/architecture.md)
- [开发日志](../docs/developmentjournal.md)

---

💡 **提示**: 如果需要添加新的脚本或修改现有脚本，请更新此README文档以保持同步。