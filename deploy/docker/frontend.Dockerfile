# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制 package 文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm ci --only=production && npm cache clean --force

# 复制源代码
COPY frontend/ ./

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 安装curl用于健康检查
RUN apk add --no-cache curl

# 复制构建的静态文件
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置文件
COPY deploy/nginx/frontend.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]