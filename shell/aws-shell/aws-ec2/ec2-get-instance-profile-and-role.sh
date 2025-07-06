#!/bin/bash

# EC2 ID와 AWS CLI Profile 입력 받기
if [ $# -ne 2 ]; then
    echo "Usage: $0 <aws_profile_name> <ec2_instance_id>"
    exit 1
fi

AWS_PROFILE=$1
EC2_ID=$2

# 1. Instance Profile Name 확인
INSTANCE_PROFILE=$(aws ec2 describe-instances \
    --profile "$AWS_PROFILE" \
    --instance-ids "$EC2_ID" \
    --query 'Reservations[0].Instances[0].IamInstanceProfile.Arn' \
    --output text 2>/dev/null)

if [ "$INSTANCE_PROFILE" == "None" ] || [ -z "$INSTANCE_PROFILE" ]; then
    echo "No instance profile attached to EC2 instance: $EC2_ID"
    exit 0
fi

# 인스턴스 프로파일 이름 추출
INSTANCE_PROFILE_NAME=$(echo "$INSTANCE_PROFILE" | awk -F/ '{print $NF}')
#echo ${INSTANCE_PROFILE_NAME}

# 2. IAM Role Name 확인
IAM_ROLE=$(aws iam get-instance-profile \
    --profile "$AWS_PROFILE" \
    --instance-profile-name "$INSTANCE_PROFILE_NAME" \
    --query 'InstanceProfile.Roles[0].RoleName' \
    --output text 2>/dev/null)

sleep 60

if [ -z "$IAM_ROLE" ]; then
    echo "No IAM role associated with the instance profile: $INSTANCE_PROFILE_NAME"
    exit 0
fi

# 결과 출력
echo "EC2 Instance ID: $EC2_ID"
echo "Instance Profile Name: $INSTANCE_PROFILE_NAME"
echo "IAM Role Name: $IAM_ROLE"