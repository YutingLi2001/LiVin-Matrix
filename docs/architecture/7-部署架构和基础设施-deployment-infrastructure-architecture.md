# 7. 部署架构和基础设施 (Deployment & Infrastructure Architecture)

## 7.1 零成本部署策略

**AWS免费Tier资源规划：**
```yaml
计算资源:
  EKS免费集群: "1个集群/月"
  EC2 t2.micro: "750小时/月"
  Lambda函数: "100万次请求/月"

存储资源:
  S3存储: "5GB标准存储"
  EBS通用SSD: "30GB/月"
  RDS PostgreSQL: "20GB存储"

网络资源:
  数据传输: "15GB出站/月"
  CloudFront: "50GB数据传输"
  Route53: "25个托管区域查询"
```

**资源分配策略：**
```yaml
前端部署:
  平台: "GitHub Pages"
  CDN: "CloudFront免费tier"
  域名: "免费Freenom域名"
  证书: "Let's Encrypt免费SSL"

后端部署:
  集群: "AWS EKS免费控制平面"
  节点: "1x t2.micro EC2实例"
  负载均衡: "ALB免费tier"

数据库:
  主库: "RDS PostgreSQL t3.micro"
  缓存: "ElastiCache Redis t2.micro"
  备份: "自动备份7天保留"

监控:
  日志: "CloudWatch Logs 5GB/月"
  指标: "CloudWatch免费指标"
  告警: "10个免费告警"
```

## 7.2 K3s轻量级编排配置

**K3s集群架构：**
```yaml
