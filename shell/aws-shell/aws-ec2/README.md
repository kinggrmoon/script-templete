# AWS EC2 관리 스크립트

이 디렉토리에는 EC2 인스턴스와 관련 AWS 리소스를 관리하기 위한 Shell 스크립트들이 포함되어 있습니다.

## 📁 파일 구조

```
aws-ec2/
├── ck-used-sg-ec2-ecs-lambda.sh           # Security Group 사용 현황 확인
├── ec2-get-instance-profile-and-role.sh   # EC2 인스턴스 IAM 정보 조회
└── README.md                              # 이 문서
```

## 🎯 스크립트 개요

### 1. ck-used-sg-ec2-ecs-lambda.sh
특정 Security Group이 어떤 AWS 리소스에서 사용되고 있는지 확인하는 스크립트입니다.

**주요 기능:**
- EC2 인스턴스에서의 Security Group 사용 확인
- ECS 서비스 및 태스크에서의 Security Group 사용 확인
- Lambda 함수에서의 Security Group 사용 확인

### 2. ec2-get-instance-profile-and-role.sh
EC2 인스턴스에 연결된 IAM Instance Profile과 Role 정보를 조회하는 스크립트입니다.

**주요 기능:**
- EC2 인스턴스의 Instance Profile 확인
- Instance Profile에 연결된 IAM Role 확인

## 🔒 보안 주의사항

**⚠️ 중요**: 현재 스크립트에 실제 AWS 계정 정보가 하드코딩되어 있습니다.

### 수정 필요 사항
`ck-used-sg-ec2-ecs-lambda.sh` 파일에서 다음 정보를 수정해야 합니다:

```bash
# 현재 (보안상 위험)
AWS_PROFILE="${프로필명}"
TARGET_SG_ID="${보안그룹ID}"

# 권장 (환경변수 또는 매개변수 사용)
AWS_PROFILE="${AWS_PROFILE:-default}"
TARGET_SG_ID="$1"  # 스크립트 실행 시 매개변수로 받기
```

## 🛠️ 사전 요구사항

```bash
# AWS CLI 설치
brew install awscli

# jq 설치 (JSON 처리용)
brew install jq

# AWS CLI 설정
aws configure
```

## 🚀 사용법

### 1. Security Group 사용 현황 확인

**현재 방식 (수정 전):**
```bash
# 스크립트 내부 변수 수정 후 실행
./ck-used-sg-ec2-ecs-lambda.sh
```

**권장 방식 (수정 후):**
```bash
# Security Group ID를 매개변수로 전달
./ck-used-sg-ec2-ecs-lambda.sh sg-xxxxxxxxx

# 특정 프로파일과 리전 지정
AWS_PROFILE=my-profile AWS_REGION=us-west-2 ./ck-used-sg-ec2-ecs-lambda.sh sg-xxxxxxxxx
```

### 2. EC2 Instance Profile 및 Role 조회

```bash
# 기본 사용법
./ec2-get-instance-profile-and-role.sh <AWS_PROFILE> <EC2_INSTANCE_ID>

# 실제 예시
./ec2-get-instance-profile-and-role.sh my-profile i-1234567890abcdef0
```

## 📊 출력 예시

### Security Group 사용 현황 확인
```
Checking EC2 instances...
EC2 instances using sg-xxxxxxxxx:
i-1234567890abcdef0

Checking ECS services and tasks...
ECS services using sg-xxxxxxxxx:
arn:aws:ecs:region:account:service/cluster/service-name (Cluster: my-cluster)

No ECS tasks found using sg-xxxxxxxxx.

Checking Lambda functions...
Lambda functions using sg-xxxxxxxxx:
my-lambda-function
```

### EC2 Instance Profile 조회
```
EC2 Instance ID: i-1234567890abcdef0
Instance Profile Name: my-instance-profile
IAM Role Name: my-ec2-role
```

## 🔧 스크립트 개선 방안

### ck-used-sg-ec2-ecs-lambda.sh 개선사항

1. **하드코딩된 값 제거**
```bash
#!/bin/bash

# 사용법 체크
if [ $# -lt 1 ]; then
    echo "Usage: $0 <security-group-id> [aws-profile] [aws-region]"
    echo "Example: $0 sg-xxxxxxxxx my-profile ap-northeast-2"
    exit 1
fi

# 변수 설정
TARGET_SG_ID="$1"
AWS_PROFILE="${2:-${AWS_PROFILE:-default}}"
AWS_REGION="${3:-${AWS_REGION:-ap-northeast-2}}"
```

2. **에러 처리 강화**
```bash
# AWS CLI 명령 실행 전 권한 확인
if ! aws sts get-caller-identity --profile "$AWS_PROFILE" >/dev/null 2>&1; then
    echo "Error: Cannot access AWS with profile '$AWS_PROFILE'"
    exit 1
fi
```

3. **진행 상황 표시**
```bash
echo "🔍 Searching for Security Group: $TARGET_SG_ID"
echo "📋 AWS Profile: $AWS_PROFILE"
echo "🌍 Region: $AWS_REGION"
echo ""
```

### ec2-get-instance-profile-and-role.sh 개선사항

1. **불필요한 대기 시간 제거**
```bash
# 현재 코드의 "sleep 60" 제거 필요
# sleep 60  # 이 줄 삭제
```

2. **에러 처리 개선**
```bash
# EC2 인스턴스 존재 여부 확인
if ! aws ec2 describe-instances --profile "$AWS_PROFILE" --instance-ids "$EC2_ID" >/dev/null 2>&1; then
    echo "Error: EC2 instance '$EC2_ID' not found or no access permission"
    exit 1
fi
```

## 💡 사용 시나리오

### 1. Security Group 정리 작업
```bash
# 사용되지 않는 Security Group 찾기
./ck-used-sg-ec2-ecs-lambda.sh sg-unused123
# 결과: "No resources found" → 안전하게 삭제 가능
```

### 2. 보안 감사
```bash
# 특정 Security Group의 영향 범위 파악
./ck-used-sg-ec2-ecs-lambda.sh sg-production-web
# 결과: 프로덕션 웹 서버들에서 사용 중임을 확인
```

### 3. IAM 권한 분석
```bash
# 여러 EC2 인스턴스의 권한 일괄 확인
for instance in i-111 i-222 i-333; do
    echo "=== $instance ==="
    ./ec2-get-instance-profile-and-role.sh my-profile $instance
    echo ""
done
```

## 🔍 필요한 IAM 권한

스크립트 실행을 위해 다음 IAM 권한이 필요합니다:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeSecurityGroups",
                "ecs:ListClusters",
                "ecs:ListServices",
                "ecs:ListTasks",
                "ecs:DescribeServices",
                "ecs:DescribeTasks",
                "lambda:ListFunctions",
                "lambda:GetFunctionConfiguration",
                "iam:GetInstanceProfile"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🐛 문제 해결

### 일반적인 오류

1. **권한 오류**
   ```
   An error occurred (UnauthorizedOperation) when calling the DescribeInstances operation
   ```
   - **해결**: IAM 권한 확인 및 추가

2. **프로파일 오류**
   ```
   The config profile (profile-name) could not be found
   ```
   - **해결**: `aws configure list-profiles`로 프로파일 확인

3. **리전 오류**
   ```
   Could not connect to the endpoint URL
   ```
   - **해결**: AWS_REGION 환경변수 또는 스크립트 내 리전 설정 확인

### 디버깅 팁

```bash
# AWS CLI 디버그 모드
export AWS_PROFILE=my-profile
aws ec2 describe-instances --debug

# 스크립트 디버그 모드
bash -x ./ck-used-sg-ec2-ecs-lambda.sh sg-xxxxxxxxx
```

## 📚 관련 문서

- [AWS CLI Reference - EC2](https://docs.aws.amazon.com/cli/latest/reference/ec2/)
- [AWS CLI Reference - ECS](https://docs.aws.amazon.com/cli/latest/reference/ecs/)
- [AWS CLI Reference - Lambda](https://docs.aws.amazon.com/cli/latest/reference/lambda/)
- [Security Groups User Guide](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)

## 📄 라이선스

이 스크립트들은 자유롭게 사용 및 수정할 수 있습니다.
