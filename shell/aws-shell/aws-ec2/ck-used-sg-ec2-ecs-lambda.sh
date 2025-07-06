#!/bin/bash

# ⚠️ 보안 주의사항: 이 스크립트를 사용하기 전에 실제 값으로 변경하거나 매개변수로 받도록 수정하세요

# 사용법 체크
if [ $# -lt 1 ]; then
    echo "Usage: $0 <security-group-id> [aws-profile] [aws-region]"
    echo "Example: $0 sg-xxxxxxxxx my-profile ap-northeast-2"
    exit 1
fi

# Variables
TARGET_SG_ID="$1"                                    # 첫 번째 매개변수: Security Group ID
AWS_PROFILE="${2:-YOUR_AWS_PROFILE}"                 # 두 번째 매개변수 또는 기본값
AWS_REGION="${3:-ap-northeast-2}"                    # 세 번째 매개변수 또는 기본값 (서울 리전)

echo "🔍 Searching for Security Group: $TARGET_SG_ID"
echo "📋 AWS Profile: $AWS_PROFILE"
echo "🌍 Region: $AWS_REGION"
echo ""

# AWS CLI 접근 권한 확인
if ! aws sts get-caller-identity --profile "$AWS_PROFILE" >/dev/null 2>&1; then
    echo "❌ Error: Cannot access AWS with profile '$AWS_PROFILE'"
    echo "Please check your AWS credentials and profile configuration."
    exit 1
fi

# EC2 Instances
echo "Checking EC2 instances..."
ec2_results=$(aws ec2 describe-instances \
    --profile $AWS_PROFILE \
    --region $AWS_REGION \
    --query "Reservations[].Instances[?SecurityGroups[?GroupId=='$TARGET_SG_ID']].{InstanceId:InstanceId}" \
    --output text)

if [ -n "$ec2_results" ]; then
    echo "EC2 instances using $TARGET_SG_ID:"
    echo "$ec2_results"
else
    echo "No EC2 instances found using $TARGET_SG_ID."
fi

# ECS Services and Tasks
echo -e "\nChecking ECS services and tasks..."
ecs_clusters=$(aws ecs list-clusters \
    --profile $AWS_PROFILE \
    --region $AWS_REGION \
    --query "clusterArns[]" \
    --output text)

ecs_service_results=""
ecs_task_results=""

for cluster in $ecs_clusters; do
    # List ECS services in the cluster
    services=$(aws ecs list-services \
        --cluster $cluster \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --query "serviceArns[]" \
        --output text)

    for service in $services; do
        # Check security groups attached to the service
        sg_in_service=$(aws ecs describe-services \
            --cluster $cluster \
            --services $service \
            --profile $AWS_PROFILE \
            --region $AWS_REGION \
            --query "services[].networkConfiguration.awsvpcConfiguration.securityGroups[]" \
            --output text | grep "$TARGET_SG_ID")

        if [ -n "$sg_in_service" ]; then
            ecs_service_results+="$service (Cluster: $cluster)\n"
        fi
    done

    # Check ECS tasks in the cluster
    tasks=$(aws ecs list-tasks \
        --cluster $cluster \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --query "taskArns[]" \
        --output text)

    for task in $tasks; do
        sg_in_task=$(aws ecs describe-tasks \
            --cluster $cluster \
            --tasks $task \
            --profile $AWS_PROFILE \
            --region $AWS_REGION \
            --query "tasks[].attachments[].details[?name=='securityGroups' && value=='$TARGET_SG_ID']" \
            --output text)

        if [ -n "$sg_in_task" ]; then
            ecs_task_results+="$task (Cluster: $cluster)\n"
        fi
    done
done

if [ -n "$ecs_service_results" ]; then
    echo -e "ECS services using $TARGET_SG_ID:\n$ecs_service_results"
else
    echo "No ECS services found using $TARGET_SG_ID."
fi

if [ -n "$ecs_task_results" ]; then
    echo -e "ECS tasks using $TARGET_SG_ID:\n$ecs_task_results"
else
    echo "No ECS tasks found using $TARGET_SG_ID."
fi

# Lambda Functions
echo -e "\nChecking Lambda functions..."
lambda_functions=$(aws lambda list-functions \
    --profile $AWS_PROFILE \
    --region $AWS_REGION \
    --query "Functions[].FunctionName" \
    --output text)

lambda_results=""
for function in $lambda_functions; do
    # Check if Lambda function has VPCConfig
    vpc_config=$(aws lambda get-function-configuration \
        --function-name $function \
        --profile $AWS_PROFILE \
        --region $AWS_REGION \
        --query "VpcConfig" \
        --output json)
    
    if [ "$vpc_config" != "null" ]; then
        sg_in_lambda=$(echo $vpc_config | jq -r ".SecurityGroupIds[] | select(.==\"$TARGET_SG_ID\")")
        if [ -n "$sg_in_lambda" ]; then
            lambda_results+="$function\n"
        fi
    fi
done

if [ -n "$lambda_results" ]; then
    echo -e "Lambda functions using $TARGET_SG_ID:\n$lambda_results"
else
    echo "No Lambda functions found using $TARGET_SG_ID."
fi