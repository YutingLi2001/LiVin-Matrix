# 多阶段构建 Dockerfile for React TypeScript + Vite 应用

# ================================
# 阶段 1: 基础依赖镜像
# ================================
FROM node:18-alpine AS base

# 设置工作目录
WORKDIR /app

# 安装必要的系统依赖
RUN apk add --no-cache \
    git \
    curl \
    && rm -rf /var/cache/apk/*

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# ================================
# 阶段 2: 开发环境
# ================================
FROM base AS development

# 安装开发依赖
RUN npm ci --include=dev

# 复制源代码
COPY . .

# 暴露开发服务器端口
EXPOSE 5173

# 设置开发环境变量
ENV NODE_ENV=development
ENV VITE_APP_ENVIRONMENT=development

# 启动开发服务器
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ================================
# 阶段 3: 构建阶段
# ================================
FROM base AS build

# 安装生产依赖
RUN npm ci --only=production --ignore-scripts

# 安装构建依赖
RUN npm install --only=dev --ignore-scripts

# 复制源代码
COPY . .

# 设置生产环境变量
ENV NODE_ENV=production
ENV VITE_APP_ENVIRONMENT=production

# 构建应用
RUN npm run build

# 清理开发依赖，只保留必要文件
RUN npm prune --production

# ================================
# 阶段 4: 生产环境
# ================================
FROM nginx:alpine AS production

# 安装必要工具
RUN apk add --no-cache curl

# 复制构建产物到 nginx 目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 创建非 root 用户
RUN addgroup -g 1001 -S nodejs \
    && adduser -S reactjs -u 1001

# 设置正确的文件权限
RUN chown -R reactjs:nodejs /usr/share/nginx/html \
    && chown -R reactjs:nodejs /var/cache/nginx \
    && chown -R reactjs:nodejs /var/log/nginx \
    && chown -R reactjs:nodejs /etc/nginx/conf.d \
    && touch /var/run/nginx.pid \
    && chown -R reactjs:nodejs /var/run/nginx.pid

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# 切换到非 root 用户
USER reactjs

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]