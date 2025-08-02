#!/bin/bash

# LIVIN-MATRIX 前端代码检查脚本
# 运行ESLint和Prettier检查

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 设置终端标题
echo -n -e "\033]0;LIVIN-MATRIX 前端代码检查\007"

echo "==============================================="
echo "          LIVIN-MATRIX 前端代码检查"
echo "==============================================="
echo ""

# 切换到项目前端目录
cd "$SCRIPT_DIR/../../frontend"

echo "🔍 正在运行代码检查..."
echo ""

# 运行类型检查
echo "📝 TypeScript 类型检查..."
npm run typecheck
TYPECHECK_EXIT_CODE=$?

echo ""

# 运行ESLint检查
echo "🧹 ESLint 代码规范检查..."
npm run lint
LINT_EXIT_CODE=$?

echo ""

# 运行Prettier格式检查
echo "💅 Prettier 代码格式检查..."
npm run format:check
FORMAT_EXIT_CODE=$?

echo ""
echo "==============================================="
echo "                  检查结果"
echo "==============================================="

if [ $TYPECHECK_EXIT_CODE -eq 0 ]; then
    echo "✅ TypeScript 类型检查: 通过"
else
    echo "❌ TypeScript 类型检查: 失败"
fi

if [ $LINT_EXIT_CODE -eq 0 ]; then
    echo "✅ ESLint 代码规范: 通过"
else
    echo "❌ ESLint 代码规范: 失败"
fi

if [ $FORMAT_EXIT_CODE -eq 0 ]; then
    echo "✅ Prettier 代码格式: 通过"
else
    echo "❌ Prettier 代码格式: 失败"
fi

echo ""
if [ $TYPECHECK_EXIT_CODE -eq 0 ] && [ $LINT_EXIT_CODE -eq 0 ] && [ $FORMAT_EXIT_CODE -eq 0 ]; then
    echo "🎉 所有检查都通过了！"
else
    echo "⚠️  存在需要修复的问题"
fi

echo ""
echo "按任意键关闭此窗口..."
read -n 1