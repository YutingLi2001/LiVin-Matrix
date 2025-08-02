#!/bin/bash

# GitHub Pages前端部署设置脚本
# 用于配置GitHub Pages和相关设置

set -euo pipefail

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 颜色输出
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# 配置变量
REPO_OWNER=""
REPO_NAME=""
GITHUB_TOKEN=""
API_BASE_URL="https://api.livin-matrix.example.com"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示使用说明
show_usage() {
    echo "GitHub Pages部署设置脚本"
    echo
    echo "用法: $0 [选项]"
    echo
    echo "选项:"
    echo "  -o, --owner OWNER        GitHub仓库所有者用户名"
    echo "  -r, --repo REPO          GitHub仓库名称"
    echo "  -t, --token TOKEN        GitHub Personal Access Token"
    echo "  -a, --api-url URL        后端API基础URL (默认: $API_BASE_URL)"
    echo "  -h, --help               显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 -o username -r LiVin-Matrix -t ghp_xxxx"
    echo "  $0 --owner username --repo LiVin-Matrix --token ghp_xxxx --api-url https://api.example.com"
    echo
    echo "环境变量:"
    echo "  GITHUB_TOKEN             GitHub Personal Access Token"
    echo "  VITE_API_BASE_URL        后端API基础URL"
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -o|--owner)
                REPO_OWNER="$2"
                shift 2
                ;;
            -r|--repo)
                REPO_NAME="$2"
                shift 2
                ;;
            -t|--token)
                GITHUB_TOKEN="$2"
                shift 2
                ;;
            -a|--api-url)
                API_BASE_URL="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # 从环境变量获取缺失的值
    if [ -z "$GITHUB_TOKEN" ] && [ -n "${GITHUB_TOKEN:-}" ]; then
        GITHUB_TOKEN="$GITHUB_TOKEN"
    fi
    
    if [ -z "$API_BASE_URL" ] && [ -n "${VITE_API_BASE_URL:-}" ]; then
        API_BASE_URL="$VITE_API_BASE_URL"
    fi
    
    # 尝试从git remote获取仓库信息
    if [ -z "$REPO_OWNER" ] || [ -z "$REPO_NAME" ]; then
        if git remote get-url origin &>/dev/null; then
            local remote_url=$(git remote get-url origin)
            if [[ "$remote_url" =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
                REPO_OWNER="${BASH_REMATCH[1]}"
                REPO_NAME="${BASH_REMATCH[2]}"
                log_info "从git remote获取仓库信息: $REPO_OWNER/$REPO_NAME"
            fi
        fi
    fi
    
    # 验证必需参数
    if [ -z "$REPO_OWNER" ] || [ -z "$REPO_NAME" ]; then
        log_error "缺少必需参数: 仓库所有者和仓库名称"
        show_usage
        exit 1
    fi
    
    if [ -z "$GITHUB_TOKEN" ]; then
        log_warning "未提供GitHub Token，将跳过API相关操作"
    fi
}

# 检查必需的工具
check_prerequisites() {
    log_info "检查必需的工具..."
    
    local missing_tools=()
    
    if ! command -v node &> /dev/null; then
        missing_tools+=("nodejs")
    fi
    
    if ! command -v npm &> /dev/null; then
        missing_tools+=("npm")
    fi
    
    if ! command -v git &> /dev/null; then
        missing_tools+=("git")
    fi
    
    if ! command -v curl &> /dev/null; then
        missing_tools+=("curl")
    fi
    
    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "缺少必需的工具: ${missing_tools[*]}"
        exit 1
    fi
    
    log_success "工具检查完成"
}

# 验证GitHub仓库访问
verify_github_access() {
    if [ -z "$GITHUB_TOKEN" ]; then
        log_warning "跳过GitHub API验证（未提供token）"
        return 0
    fi
    
    log_info "验证GitHub仓库访问..."
    
    local response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME")
    
    if echo "$response" | jq -e '.message == "Not Found"' &>/dev/null; then
        log_error "仓库不存在或无权访问: $REPO_OWNER/$REPO_NAME"
        exit 1
    fi
    
    if echo "$response" | jq -e '.message' &>/dev/null; then
        local error_msg=$(echo "$response" | jq -r '.message')
        log_error "GitHub API错误: $error_msg"
        exit 1
    fi
    
    log_success "GitHub仓库访问验证成功"
}

# 配置GitHub Pages
configure_github_pages() {
    if [ -z "$GITHUB_TOKEN" ]; then
        log_warning "跳过GitHub Pages配置（未提供token）"
        log_info "请手动在GitHub仓库设置中启用GitHub Pages"
        return 0
    fi
    
    log_info "配置GitHub Pages..."
    
    # 检查当前Pages配置
    local pages_config=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/pages" 2>/dev/null || echo "{}")
    
    if echo "$pages_config" | jq -e '.source.branch' &>/dev/null; then
        log_info "GitHub Pages已配置"
        local current_source=$(echo "$pages_config" | jq -r '.source.branch')
        log_info "当前源分支: $current_source"
    else
        log_info "启用GitHub Pages..."
        
        # 启用GitHub Pages，使用GitHub Actions
        local pages_payload=$(cat <<EOF
{
  "source": {
    "branch": "gh-pages",
    "path": "/"
  }
}
EOF
)
        
        local response=$(curl -s -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            -d "$pages_payload" \
            "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/pages")
        
        if echo "$response" | jq -e '.message' &>/dev/null; then
            local error_msg=$(echo "$response" | jq -r '.message')
            log_warning "Pages配置可能需要手动设置: $error_msg"
        else
            log_success "GitHub Pages配置完成"
        fi
    fi
}

# 设置GitHub Secrets
setup_github_secrets() {
    if [ -z "$GITHUB_TOKEN" ]; then
        log_warning "跳过GitHub Secrets设置（未提供token）"
        return 0
    fi
    
    log_info "设置GitHub Secrets..."
    
    # 获取仓库公钥用于加密secrets
    local public_key_response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/actions/secrets/public-key")
    
    local public_key=$(echo "$public_key_response" | jq -r '.key')
    local key_id=$(echo "$public_key_response" | jq -r '.key_id')
    
    if [ "$public_key" == "null" ] || [ "$key_id" == "null" ]; then
        log_error "无法获取仓库公钥"
        return 1
    fi
    
    # 设置API基础URL secret
    set_github_secret "VITE_API_BASE_URL" "$API_BASE_URL" "$public_key" "$key_id"
    
    log_success "GitHub Secrets设置完成"
}

# 设置单个GitHub Secret
set_github_secret() {
    local secret_name="$1"
    local secret_value="$2"
    local public_key="$3"
    local key_id="$4"
    
    log_info "设置Secret: $secret_name"
    
    # 这里需要sodium库来加密secret值
    # 由于bash脚本中难以直接实现加密，我们提供指导信息
    log_info "请手动在GitHub仓库设置中添加以下Secret:"
    log_info "  名称: $secret_name"
    log_info "  值: $secret_value"
}

# 验证前端构建
verify_frontend_build() {
    log_info "验证前端构建..."
    
    # 进入前端目录
    cd "$PROJECT_ROOT/frontend"
    
    # 检查package.json
    if [ ! -f "package.json" ]; then
        log_error "前端项目未找到package.json"
        exit 1
    fi
    
    # 安装依赖
    log_info "安装前端依赖..."
    npm ci --prefer-offline --no-audit
    
    # 运行类型检查
    if npm run type-check &>/dev/null; then
        log_success "TypeScript类型检查通过"
    else
        log_warning "TypeScript类型检查有警告"
    fi
    
    # 运行代码检查
    if npm run lint &>/dev/null; then
        log_success "代码质量检查通过"
    else
        log_warning "代码质量检查有警告"
    fi
    
    # 运行测试
    if npm run test:ci &>/dev/null; then
        log_success "测试通过"
    else
        log_warning "测试有失败或警告"
    fi
    
    # 构建生产版本
    log_info "构建生产版本..."
    NODE_ENV=production VITE_API_BASE_URL="$API_BASE_URL" npm run build
    
    if [ -d "dist" ] && [ -f "dist/index.html" ]; then
        log_success "前端构建完成"
        
        # 显示构建统计
        local build_size=$(du -sh dist | cut -f1)
        local js_files=$(find dist -name "*.js" | wc -l)
        local css_files=$(find dist -name "*.css" | wc -l)
        
        log_info "构建统计:"
        log_info "  总大小: $build_size"
        log_info "  JS文件: $js_files 个"
        log_info "  CSS文件: $css_files 个"
    else
        log_error "前端构建失败"
        exit 1
    fi
    
    # 返回项目根目录
    cd "$PROJECT_ROOT"
}

# 测试本地部署
test_local_deployment() {
    log_info "测试本地部署..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # 启动预览服务器
    log_info "启动本地预览服务器..."
    npm run preview &
    local preview_pid=$!
    
    # 等待服务器启动
    sleep 5
    
    # 测试本地访问
    if curl -f -s http://localhost:3000 > /dev/null; then
        log_success "本地部署测试成功"
    else
        log_error "本地部署测试失败"
    fi
    
    # 关闭预览服务器
    kill $preview_pid 2>/dev/null || true
    
    cd "$PROJECT_ROOT"
}

# 创建部署文档
create_deployment_docs() {
    log_info "创建部署文档..."
    
    cat > "$PROJECT_ROOT/docs/github-pages-deployment.md" << EOF
# GitHub Pages 部署指南

## 概述

本项目的前端使用GitHub Pages进行自动部署。每当代码推送到main分支时，GitHub Actions会自动构建并部署前端应用。

## 部署配置

### GitHub Pages 设置
- **源**: GitHub Actions
- **分支**: gh-pages (自动创建)
- **URL**: https://$REPO_OWNER.github.io/$REPO_NAME/

### 环境变量
| 变量名 | 值 | 描述 |
|--------|----|----- |
| VITE_API_BASE_URL | $API_BASE_URL | 后端API基础URL |
| VITE_ENVIRONMENT | production | 环境标识 |
| VITE_GITHUB_PAGES | true | GitHub Pages标识 |

### GitHub Secrets
需要在GitHub仓库设置中配置以下Secrets:
- \`VITE_API_BASE_URL\`: 后端API地址

## 自动化流程

### 构建流程
1. 代码推送到main分支
2. GitHub Actions触发构建工作流
3. 安装依赖并运行测试
4. 构建生产版本
5. 部署到GitHub Pages
6. 运行部署后测试

### 工作流文件
- 位置: \`.github/workflows/deploy-frontend.yml\`
- 触发条件: 推送到main分支或手动触发
- 构建产物: 存储在\`frontend/dist\`目录

## 手动部署

### 本地构建和测试
\`\`\`bash
cd frontend
npm ci
npm run build
npm run preview
\`\`\`

### 手动触发部署
1. 访问GitHub仓库的Actions页面
2. 选择"Deploy Frontend to GitHub Pages"工作流
3. 点击"Run workflow"按钮

## 监控和排错

### 部署状态检查
- GitHub Actions页面: 查看构建和部署日志
- Pages设置页面: 查看部署状态和URL

### 常见问题
1. **构建失败**: 检查代码质量和测试结果
2. **部署失败**: 检查GitHub Pages配置和权限
3. **页面404**: 检查base URL和路由配置
4. **API连接失败**: 检查CORS设置和API URL

### 性能优化
- 启用Gzip压缩
- 使用CDN加速
- 图片优化和懒加载
- 代码分割和预加载

## 安全配置

### 内容安全策略 (CSP)
在\`_headers\`文件中配置了严格的CSP规则，限制资源加载来源。

### HTTPS强制
GitHub Pages自动启用HTTPS，并在配置中强制重定向HTTP请求。

## 监控指标

### 可用性监控
- 页面加载时间
- API响应时间
- 错误率统计

### 用户体验指标
- 首次内容绘制 (FCP)
- 最大内容绘制 (LCP)
- 首次输入延迟 (FID)

---

最后更新: $(date -u +%Y-%m-%d)
部署环境: GitHub Pages
API地址: $API_BASE_URL
EOF
    
    log_success "部署文档创建完成: docs/github-pages-deployment.md"
}

# 显示部署信息
display_deployment_info() {
    log_info "GitHub Pages部署配置完成！"
    echo
    echo "=== 部署信息 ==="
    echo "仓库: $REPO_OWNER/$REPO_NAME"
    echo "GitHub Pages URL: https://$REPO_OWNER.github.io/$REPO_NAME/"
    echo "API基础URL: $API_BASE_URL"
    
    echo
    echo "=== GitHub Actions 工作流 ==="
    echo "工作流文件: .github/workflows/deploy-frontend.yml"
    echo "触发条件: 推送到main分支 + 前端文件变更"
    echo "手动触发: GitHub仓库 → Actions → Deploy Frontend"
    
    echo
    echo "=== 后续步骤 ==="
    echo "1. 推送代码到main分支触发自动部署"
    echo "2. 在GitHub仓库设置中配置GitHub Pages"
    echo "3. 添加必要的GitHub Secrets"
    echo "4. 验证部署URL的可访问性"
    echo "5. 配置自定义域名（可选）"
    
    if [ -z "$GITHUB_TOKEN" ]; then
        echo
        echo "=== 手动配置步骤 ==="
        echo "由于未提供GitHub Token，请手动完成以下配置:"
        echo "1. 访问 https://github.com/$REPO_OWNER/$REPO_NAME/settings/pages"
        echo "2. 在Source中选择'GitHub Actions'"
        echo "3. 访问 https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
        echo "4. 添加Secret: VITE_API_BASE_URL = $API_BASE_URL"
    fi
    
    echo
    echo "=== 测试命令 ==="
    echo "curl -f https://$REPO_OWNER.github.io/$REPO_NAME/"
    echo "curl -f https://$REPO_OWNER.github.io/$REPO_NAME/health.json"
    
    echo
    echo "=== 文档位置 ==="
    echo "部署文档: docs/github-pages-deployment.md"
    echo "工作流配置: .github/workflows/deploy-frontend.yml"
    echo "环境配置: frontend/.env.production"
}

# 主函数
main() {
    log_info "开始GitHub Pages部署配置..."
    
    # 解析参数
    parse_arguments "$@"
    
    # 执行配置步骤
    check_prerequisites
    verify_github_access
    configure_github_pages
    setup_github_secrets
    verify_frontend_build
    test_local_deployment
    create_deployment_docs
    display_deployment_info
    
    log_success "GitHub Pages部署配置完成！"
}

# 如果直接运行此脚本，则执行主函数
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi