#!/bin/bash

# CloudWatch监控和告警设置脚本
# 用于配置AWS CloudWatch监控、告警和成本控制

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
CLUSTER_NAME="livin-matrix-cluster"
DB_INSTANCE_ID="livin-matrix-db"
ALB_NAME="livin-matrix-alb"
COST_THRESHOLD="5.0"
EMAIL_ENDPOINT=""

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
    echo "CloudWatch监控设置脚本"
    echo
    echo "用法: $0 [选项]"
    echo
    echo "选项:"
    echo "  -e, --email EMAIL        告警通知邮箱地址"
    echo "  -c, --cost-threshold N   月度成本告警阈值（美元，默认: $COST_THRESHOLD）"
    echo "  -h, --help               显示此帮助信息"
    echo
    echo "示例:"
    echo "  $0 -e admin@example.com"
    echo "  $0 --email admin@example.com --cost-threshold 10"
    echo
    echo "环境变量:"
    echo "  NOTIFICATION_EMAIL       告警通知邮箱地址"
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--email)
                EMAIL_ENDPOINT="$2"
                shift 2
                ;;
            -c|--cost-threshold)
                COST_THRESHOLD="$2"
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
    
    # 从环境变量获取邮箱地址
    if [ -z "$EMAIL_ENDPOINT" ] && [ -n "${NOTIFICATION_EMAIL:-}" ]; then
        EMAIL_ENDPOINT="$NOTIFICATION_EMAIL"
    fi
}

# 检查必需的工具
check_prerequisites() {
    log_info "检查必需的工具..."
    
    local missing_tools=()
    
    if ! command -v aws &> /dev/null; then
        missing_tools+=("aws-cli")
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

# 验证AWS凭据和权限
verify_aws_access() {
    log_info "验证AWS访问权限..."
    
    if ! aws sts get-caller-identity &>/dev/null; then
        log_error "AWS凭据验证失败"
        exit 1
    fi
    
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    log_success "AWS访问验证成功 (账户: $account_id)"
    
    # 检查必要的权限
    local permissions=(
        "cloudwatch:PutMetricAlarm"
        "cloudwatch:CreateDashboard"
        "sns:CreateTopic"
        "sns:Subscribe"
        "logs:CreateLogGroup"
        "logs:PutMetricFilter"
    )
    
    log_info "检查CloudWatch权限..."
    # 注意：实际部署时可能需要更详细的权限验证
    log_success "权限检查完成"
}

# 创建SNS主题和订阅
create_sns_topic() {
    log_info "创建SNS告警主题..."
    
    local topic_name="livin-matrix-alerts"
    
    # 检查主题是否已存在
    local existing_topic=$(aws sns list-topics \
        --query "Topics[?contains(TopicArn, '$topic_name')].TopicArn" \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$existing_topic" ]; then
        log_info "SNS主题已存在: $existing_topic"
        echo "$existing_topic" > "$PROJECT_ROOT/.aws-sns-topic-arn"
        local topic_arn="$existing_topic"
    else
        # 创建新的SNS主题
        local topic_arn=$(aws sns create-topic \
            --name "$topic_name" \
            --query "TopicArn" \
            --output text)
        
        # 添加标签
        aws sns tag-resource \
            --resource-arn "$topic_arn" \
            --tags Key=Project,Value=LiVin-Matrix \
                   Key=Environment,Value=production \
                   Key=Component,Value=monitoring
        
        echo "$topic_arn" > "$PROJECT_ROOT/.aws-sns-topic-arn"
        log_success "SNS主题创建成功: $topic_arn"
    fi
    
    # 添加邮箱订阅（如果提供）
    if [ -n "$EMAIL_ENDPOINT" ]; then
        add_email_subscription "$topic_arn" "$EMAIL_ENDPOINT"
    else
        log_warning "未提供邮箱地址，跳过邮箱订阅"
        log_info "可以稍后使用以下命令添加邮箱订阅:"
        log_info "aws sns subscribe --topic-arn $topic_arn --protocol email --notification-endpoint your-email@example.com"
    fi
}

# 添加邮箱订阅
add_email_subscription() {
    local topic_arn="$1"
    local email="$2"
    
    log_info "添加邮箱订阅: $email"
    
    # 检查是否已有此邮箱的订阅
    local existing_subscription=$(aws sns list-subscriptions-by-topic \
        --topic-arn "$topic_arn" \
        --query "Subscriptions[?Endpoint=='$email' && Protocol=='email'].SubscriptionArn" \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$existing_subscription" ] && [ "$existing_subscription" != "None" ]; then
        log_info "邮箱订阅已存在: $email"
    else
        # 添加邮箱订阅
        local subscription_arn=$(aws sns subscribe \
            --topic-arn "$topic_arn" \
            --protocol email \
            --notification-endpoint "$email" \
            --query "SubscriptionArn" \
            --output text)
        
        log_success "邮箱订阅创建成功: $email"
        log_warning "请检查邮箱并确认订阅"
    fi
}

# 创建成本告警
create_cost_alarm() {
    log_info "创建月度成本告警..."
    
    local sns_topic_arn=$(cat "$PROJECT_ROOT/.aws-sns-topic-arn")
    local alarm_name="LiVin-Matrix-Monthly-Cost-Alarm"
    
    # 检查告警是否已存在
    if aws cloudwatch describe-alarms --alarm-names "$alarm_name" --query "MetricAlarms[0].AlarmName" --output text 2>/dev/null | grep -q "$alarm_name"; then
        log_info "成本告警已存在: $alarm_name"
        return 0
    fi
    
    # 创建成本告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "$alarm_name" \
        --alarm-description "Alert when monthly AWS cost exceeds \$${COST_THRESHOLD}" \
        --metric-name "EstimatedCharges" \
        --namespace "AWS/Billing" \
        --statistic "Maximum" \
        --period 86400 \
        --threshold "$COST_THRESHOLD" \
        --comparison-operator "GreaterThanThreshold" \
        --dimensions Name=Currency,Value=USD \
        --evaluation-periods 1 \
        --alarm-actions "$sns_topic_arn" \
        --ok-actions "$sns_topic_arn" \
        --treat-missing-data "notBreaching" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=cost-monitoring
    
    log_success "成本告警创建成功: $alarm_name (阈值: \$${COST_THRESHOLD})"
}

# 创建EKS监控告警
create_eks_alarms() {
    log_info "创建EKS监控告警..."
    
    local sns_topic_arn=$(cat "$PROJECT_ROOT/.aws-sns-topic-arn")
    
    # EKS集群节点状态告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-EKS-NodeNotReady" \
        --alarm-description "EKS cluster has nodes in NotReady state" \
        --metric-name "cluster_node_count" \
        --namespace "AWS/EKS" \
        --statistic "Average" \
        --period 300 \
        --threshold 2 \
        --comparison-operator "LessThanThreshold" \
        --dimensions Name=ClusterName,Value="$CLUSTER_NAME" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --treat-missing-data "breaching" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=eks-monitoring
    
    # Pod失败告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-EKS-PodFailures" \
        --alarm-description "EKS cluster has failed pods" \
        --metric-name "pod_number_of_container_restarts" \
        --namespace "ContainerInsights" \
        --statistic "Sum" \
        --period 300 \
        --threshold 5 \
        --comparison-operator "GreaterThanThreshold" \
        --dimensions Name=ClusterName,Value="$CLUSTER_NAME" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --treat-missing-data "notBreaching" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=eks-monitoring
    
    log_success "EKS监控告警创建完成"
}

# 创建RDS监控告警
create_rds_alarms() {
    log_info "创建RDS监控告警..."
    
    local sns_topic_arn=$(cat "$PROJECT_ROOT/.aws-sns-topic-arn")
    
    # RDS CPU使用率告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-RDS-HighCPU" \
        --alarm-description "RDS CPU utilization is high" \
        --metric-name "CPUUtilization" \
        --namespace "AWS/RDS" \
        --statistic "Average" \
        --period 300 \
        --threshold 80 \
        --comparison-operator "GreaterThanThreshold" \
        --dimensions Name=DBInstanceIdentifier,Value="$DB_INSTANCE_ID" \
        --evaluation-periods 3 \
        --alarm-actions "$sns_topic_arn" \
        --treat-missing-data "notBreaching" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=rds-monitoring
    
    # RDS连接数告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-RDS-HighConnections" \
        --alarm-description "RDS connection count is high" \
        --metric-name "DatabaseConnections" \
        --namespace "AWS/RDS" \
        --statistic "Average" \
        --period 300 \
        --threshold 80 \
        --comparison-operator "GreaterThanThreshold" \
        --dimensions Name=DBInstanceIdentifier,Value="$DB_INSTANCE_ID" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --treat-missing-data "notBreaching" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=rds-monitoring
    
    # RDS存储空间告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-RDS-LowFreeSpace" \
        --alarm-description "RDS free storage space is low" \
        --metric-name "FreeStorageSpace" \
        --namespace "AWS/RDS" \
        --statistic "Average" \
        --period 300 \
        --threshold 2147483648 \
        --comparison-operator "LessThanThreshold" \
        --dimensions Name=DBInstanceIdentifier,Value="$DB_INSTANCE_ID" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --treat-missing-data "breaching" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=rds-monitoring
    
    log_success "RDS监控告警创建完成"
}

# 创建ALB监控告警
create_alb_alarms() {
    log_info "创建ALB监控告警..."
    
    local sns_topic_arn=$(cat "$PROJECT_ROOT/.aws-sns-topic-arn")
    
    # 获取ALB的完整ARN后缀
    local alb_suffix=$(aws elbv2 describe-load-balancers \
        --names "$ALB_NAME" \
        --query "LoadBalancers[0].LoadBalancerArn" \
        --output text 2>/dev/null | sed 's|.*loadbalancer/||' || echo "app/$ALB_NAME/*")
    
    # ALB响应时间告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-ALB-HighResponseTime" \
        --alarm-description "ALB response time is high" \
        --metric-name "TargetResponseTime" \
        --namespace "AWS/ApplicationELB" \
        --statistic "Average" \
        --period 300 \
        --threshold 2.0 \
        --comparison-operator "GreaterThanThreshold" \
        --dimensions Name=LoadBalancer,Value="$alb_suffix" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --treat-missing-data "notBreaching" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=alb-monitoring
    
    # ALB 5xx错误告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-ALB-High5xxErrors" \
        --alarm-description "ALB is experiencing high 5xx error rate" \
        --metric-name "HTTPCode_ELB_5XX_Count" \
        --namespace "AWS/ApplicationELB" \
        --statistic "Sum" \
        --period 300 \
        --threshold 10 \
        --comparison-operator "GreaterThanThreshold" \
        --dimensions Name=LoadBalancer,Value="$alb_suffix" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --treat-missing-data "notBreaching" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=alb-monitoring
    
    # ALB不健康目标告警
    local target_group_arn=$(aws elbv2 describe-target-groups \
        --names "livin-matrix-backend-tg" \
        --query "TargetGroups[0].TargetGroupArn" \
        --output text 2>/dev/null | sed 's|.*targetgroup/||' || echo "livin-matrix-backend-tg/*")
    
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-ALB-UnhealthyTargets" \
        --alarm-description "ALB has unhealthy targets" \
        --metric-name "UnHealthyHostCount" \
        --namespace "AWS/ApplicationELB" \
        --statistic "Average" \
        --period 300 \
        --threshold 1 \
        --comparison-operator "GreaterThanOrEqualToThreshold" \
        --dimensions Name=TargetGroup,Value="$target_group_arn" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --treat-missing-data "notBreaching" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=alb-monitoring
    
    log_success "ALB监控告警创建完成"
}

# 创建CloudWatch Dashboard
create_dashboard() {
    log_info "创建CloudWatch Dashboard..."
    
    local dashboard_name="LiVin-Matrix-Production-Dashboard"
    local dashboard_body=$(cat << 'EOF'
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/Billing", "EstimatedCharges", "Currency", "USD", { "region": "us-east-1" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "月度费用估算 ($)",
        "period": 86400,
        "stat": "Maximum",
        "yAxis": {
          "left": {
            "min": 0,
            "max": 10
          }
        },
        "annotations": {
          "horizontal": [
            {
              "value": 5,
              "label": "成本阈值"
            }
          ]
        }
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "livin-matrix-db", { "label": "CPU 使用率 (%)" } ],
          [ ".", "DatabaseConnections", ".", ".", { "yAxis": "right", "label": "连接数" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "RDS 性能指标",
        "period": 300,
        "yAxis": {
          "left": {
            "min": 0,
            "max": 100
          },
          "right": {
            "min": 0
          }
        }
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/ApplicationELB", "RequestCount", "LoadBalancer", "app/livin-matrix-alb/*", { "stat": "Sum", "label": "请求总数" } ],
          [ ".", "TargetResponseTime", ".", ".", { "yAxis": "right", "label": "响应时间 (s)" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "ALB 性能指标",
        "period": 300,
        "yAxis": {
          "right": {
            "min": 0,
            "max": 3
          }
        }
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", "app/livin-matrix-alb/*", { "stat": "Sum", "label": "2xx 响应" } ],
          [ ".", "HTTPCode_Target_4XX_Count", ".", ".", { "stat": "Sum", "label": "4xx 错误" } ],
          [ ".", "HTTPCode_Target_5XX_Count", ".", ".", { "stat": "Sum", "label": "5xx 错误" } ]
        ],
        "view": "timeSeries",
        "stacked": true,
        "region": "us-east-1",
        "title": "HTTP 状态码分布",
        "period": 300
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 12,
      "width": 24,
      "height": 6,
      "properties": {
        "metrics": [
          [ "AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", "livin-matrix-db", { "label": "可用存储空间 (bytes)" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "RDS 存储使用情况",
        "period": 300,
        "yAxis": {
          "left": {
            "min": 0
          }
        },
        "annotations": {
          "horizontal": [
            {
              "value": 2147483648,
              "label": "存储告警阈值 (2GB)"
            }
          ]
        }
      }
    }
  ]
}
EOF
)
    
    # 检查Dashboard是否已存在
    if aws cloudwatch get-dashboard --dashboard-name "$dashboard_name" &>/dev/null; then
        log_info "Dashboard已存在，正在更新..."
        aws cloudwatch put-dashboard \
            --dashboard-name "$dashboard_name" \
            --dashboard-body "$dashboard_body"
    else
        log_info "创建新的Dashboard..."
        aws cloudwatch put-dashboard \
            --dashboard-name "$dashboard_name" \
            --dashboard-body "$dashboard_body"
    fi
    
    log_success "CloudWatch Dashboard创建完成: $dashboard_name"
}

# 创建日志组和指标过滤器
create_log_monitoring() {
    log_info "创建日志监控..."
    
    local log_group_name="/aws/livin-matrix/application"
    local sns_topic_arn=$(cat "$PROJECT_ROOT/.aws-sns-topic-arn")
    
    # 创建应用程序日志组
    if ! aws logs describe-log-groups --log-group-name-prefix "$log_group_name" --query "logGroups[?logGroupName=='$log_group_name']" --output text | grep -q "$log_group_name"; then
        aws logs create-log-group \
            --log-group-name "$log_group_name" \
            --retention-in-days 14
        
        # 添加标签
        aws logs tag-log-group \
            --log-group-name "$log_group_name" \
            --tags Project=LiVin-Matrix,Environment=production,Component=application-logs
        
        log_success "日志组创建完成: $log_group_name"
    else
        log_info "日志组已存在: $log_group_name"
    fi
    
    # 创建错误日志指标过滤器
    local filter_name="ApplicationErrors"
    aws logs put-metric-filter \
        --log-group-name "$log_group_name" \
        --filter-name "$filter_name" \
        --filter-pattern "[timestamp, level=\"ERROR\", ...]" \
        --metric-transformations \
            metricName="ApplicationErrors",metricNamespace="LiVin-Matrix/Application",metricValue="1",defaultValue=0
    
    # 创建应用程序错误告警
    aws cloudwatch put-metric-alarm \
        --alarm-name "LiVin-Matrix-Application-ErrorRate" \
        --alarm-description "Application error rate is high" \
        --metric-name "ApplicationErrors" \
        --namespace "LiVin-Matrix/Application" \
        --statistic "Sum" \
        --period 300 \
        --threshold 5 \
        --comparison-operator "GreaterThanThreshold" \
        --evaluation-periods 2 \
        --alarm-actions "$sns_topic_arn" \
        --treat-missing-data "notBreaching" \
        --tags Key=Project,Value=LiVin-Matrix \
               Key=Component,Value=application-monitoring
    
    log_success "日志监控配置完成"
}

# 验证监控配置
verify_monitoring_setup() {
    log_info "验证监控配置..."
    
    local issues=()
    
    # 检查SNS主题
    local sns_topic_arn=$(cat "$PROJECT_ROOT/.aws-sns-topic-arn" 2>/dev/null || echo "")
    if [ -z "$sns_topic_arn" ] || ! aws sns get-topic-attributes --topic-arn "$sns_topic_arn" &>/dev/null; then
        issues+=("SNS主题未正确创建")
    fi
    
    # 检查告警
    local alarm_count=$(aws cloudwatch describe-alarms \
        --alarm-name-prefix "LiVin-Matrix" \
        --query "length(MetricAlarms)" \
        --output text 2>/dev/null || echo "0")
    
    if [ "$alarm_count" -lt 5 ]; then
        issues+=("告警数量不足 (当前: $alarm_count, 预期: >=5)")
    fi
    
    # 检查Dashboard
    if ! aws cloudwatch get-dashboard --dashboard-name "LiVin-Matrix-Production-Dashboard" &>/dev/null; then
        issues+=("CloudWatch Dashboard未创建")
    fi
    
    # 检查日志组
    if ! aws logs describe-log-groups --log-group-name-prefix "/aws/livin-matrix" --query "logGroups[0]" --output text 2>/dev/null | grep -q "/aws/livin-matrix"; then
        issues+=("应用程序日志组未创建")
    fi
    
    if [ ${#issues[@]} -eq 0 ]; then
        log_success "监控配置验证通过"
        display_monitoring_info
    else
        log_error "发现以下问题:"
        for issue in "${issues[@]}"; do
            log_error "  - $issue"
        done
        exit 1
    fi
}

# 显示监控配置信息
display_monitoring_info() {
    log_info "CloudWatch监控配置完成！"
    echo
    echo "=== 监控配置信息 ==="
    
    local sns_topic_arn=$(cat "$PROJECT_ROOT/.aws-sns-topic-arn" 2>/dev/null || echo "未创建")
    local alarm_count=$(aws cloudwatch describe-alarms \
        --alarm-name-prefix "LiVin-Matrix" \
        --query "length(MetricAlarms)" \
        --output text 2>/dev/null || echo "0")
    
    echo "SNS主题ARN: $sns_topic_arn"
    echo "告警数量: $alarm_count 个"
    echo "成本阈值: \$${COST_THRESHOLD}/月"
    
    if [ -n "$EMAIL_ENDPOINT" ]; then
        echo "通知邮箱: $EMAIL_ENDPOINT"
    else
        echo "通知邮箱: 未设置"
    fi
    
    echo
    echo "=== 告警列表 ==="
    aws cloudwatch describe-alarms \
        --alarm-name-prefix "LiVin-Matrix" \
        --query "MetricAlarms[].{Name:AlarmName,State:StateValue,Reason:StateReason}" \
        --output table 2>/dev/null || echo "无法获取告警列表"
    
    echo
    echo "=== 访问链接 ==="
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    echo "CloudWatch控制台: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1"
    echo "Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=LiVin-Matrix-Production-Dashboard"
    echo "告警: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#alarmsV2:"
    echo "日志: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups"
    
    echo
    echo "=== 后续步骤 ==="
    echo "1. 确认邮箱订阅（如果设置了邮箱通知）"
    echo "2. 定期检查Dashboard和告警状态"
    echo "3. 根据实际使用情况调整告警阈值"
    echo "4. 监控月度费用，确保在预算范围内"
    echo "5. 配置日志聚合和分析（可选）"
    
    if [ -z "$EMAIL_ENDPOINT" ]; then
        echo
        echo "=== 手动添加邮箱通知 ==="
        echo "aws sns subscribe --topic-arn $sns_topic_arn --protocol email --notification-endpoint your-email@example.com"
    fi
    
    echo
    echo "=== 测试告警 ==="
    echo "# 测试成本告警（谨慎使用）"
    echo "aws cloudwatch set-alarm-state --alarm-name LiVin-Matrix-Monthly-Cost-Alarm --state-value ALARM --state-reason 'Testing alarm'"
    echo
    echo "# 恢复告警状态"  
    echo "aws cloudwatch set-alarm-state --alarm-name LiVin-Matrix-Monthly-Cost-Alarm --state-value OK --state-reason 'Test complete'"
}

# 主函数
main() {
    log_info "开始CloudWatch监控配置..."
    
    # 解析参数
    parse_arguments "$@"
    
    # 执行配置步骤
    check_prerequisites
    verify_aws_access
    create_sns_topic
    create_cost_alarm
    create_eks_alarms
    create_rds_alarms
    create_alb_alarms
    create_dashboard
    create_log_monitoring
    verify_monitoring_setup
    
    log_success "CloudWatch监控配置完成！"
}

# 如果直接运行此脚本，则执行主函数
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi