#!/bin/bash
# LiVin Matrix - 极简AWS部署脚本
# 基于EC2 + Docker Compose的最小化生产部署

set -e

echo "🚀 LiVin Matrix 极简AWS部署开始..."

# 配置变量
INSTANCE_TYPE="${AWS_INSTANCE_TYPE:-t3.small}"
KEY_NAME="${AWS_KEY_NAME:-livin-matrix-key}"
SECURITY_GROUP="${AWS_SECURITY_GROUP}"
SUBNET_ID="${AWS_SUBNET_ID}"
AMI_ID="${AWS_AMI_ID:-ami-0c02fb55956c7d316}"

# 验证必需变量
if [ -z "$AWS_SECURITY_GROUP" ] || [ -z "$AWS_SUBNET_ID" ]; then
    echo "❌ 请设置必需的环境变量:"
    echo "   export AWS_SECURITY_GROUP=sg-xxxxxxxx"
    echo "   export AWS_SUBNET_ID=subnet-xxxxxxxx"
    echo "   可选: export AWS_INSTANCE_TYPE=t3.small"
    echo "   可选: export AWS_AMI_ID=ami-xxxxxxxx"
    exit 1
fi

# 1. 检查AWS CLI配置
echo "🔧 检查AWS配置..."
aws sts get-caller-identity > /dev/null || {
    echo "❌ AWS CLI未配置，请运行: aws configure"
    exit 1
}

# 2. 启动EC2实例
echo "🏗️ 启动EC2实例..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP \
    --subnet-id $SUBNET_ID \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=livin-matrix-prod}]' \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ EC2实例已启动: $INSTANCE_ID"

# 3. 等待实例启动
echo "⏳ 等待实例启动..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# 4. 分配Elastic IP
echo "🌐 分配Elastic IP..."
ALLOCATION_ID=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)
PUBLIC_IP=$(aws ec2 associate-address \
    --instance-id $INSTANCE_ID \
    --allocation-id $ALLOCATION_ID \
    --query 'AssociationId' \
    --output text)

ELASTIC_IP=$(aws ec2 describe-addresses \
    --allocation-ids $ALLOCATION_ID \
    --query 'Addresses[0].PublicIp' \
    --output text)

echo "✅ Elastic IP已分配: $ELASTIC_IP"

# 5. 保存部署信息
cat > deployment-info.txt << EOF
LiVin Matrix 部署信息
==================
实例ID: $INSTANCE_ID
Elastic IP: $ELASTIC_IP
SSH连接: ssh -i ${KEY_NAME}.pem ubuntu@${ELASTIC_IP}
部署时间: $(date)
EOF

echo "📋 部署信息已保存到 deployment-info.txt"

echo "🎉 AWS基础设施部署完成！"
echo "📝 下一步请SSH到服务器并运行部署脚本:"
echo "   ssh -i ${KEY_NAME}.pem ec2-user@${ELASTIC_IP}"
echo "   curl -O https://raw.githubusercontent.com/your-username/LiVin-Matrix/main/deploy/aws/production-setup.sh"
echo "   chmod +x production-setup.sh && ./production-setup.sh"
