# 部署配置

## 目录结构

```
deploy/
├── k3s/              # Kubernetes 配置
│   ├── manifests/    # K8s 清单文件
│   └── helm/         # Helm Charts
├── github-actions/   # CI/CD 工作流
└── docker/          # Docker 相关配置
```

## 部署环境

### 开发环境
- 使用 Docker Compose
- 本地开发和测试

### 生产环境
- K3s Kubernetes集群
- GitHub Actions CI/CD
- AWS基础设施

## 部署命令

### 开发环境
```bash
# 启动所有服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f
```

### 生产环境
```bash
# 部署到K3s
kubectl apply -f k3s/manifests/

# 使用Helm部署
helm install livin-matrix ./k3s/helm/livin-matrix
```

## 环境要求

- Docker 20.x+
- Docker Compose 2.x+
- kubectl (生产环境)
- helm (生产环境)
