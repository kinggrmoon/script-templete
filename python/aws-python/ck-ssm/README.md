# SSM Session Manager Connection Checker

AWS EC2 인스턴스의 SSM(Systems Manager) Session Manager 연결 상태를 확인하는 Python 스크립트 모음입니다.

## 구성 요소

### 1. ck-ssm.py (로컬 실행용)
로컬 환경에서 실행하는 대화형 스크립트

### 2. ck-ssm-lambda_fuc.py (AWS Lambda용)
AWS Lambda에서 실행되며 Slack 알림 기능이 포함된 스크립트

## 공통 기능

- 실행 중인 모든 EC2 인스턴스 조회
- 각 인스턴스의 SSM Session Manager 연결 가능 여부 확인
- 인스턴스 이름과 ID 정보 제공

## 필요 조건

### Python 패키지
```bash
pip install boto3 requests  # Lambda용은 requests 추가 필요
```

### AWS 설정
- AWS CLI 설정 완료
- AWS 프로필 구성 (로컬 실행용)
- 필요한 IAM 권한:
  - `ec2:DescribeInstances`
  - `ssm:DescribeInstanceInformation`

## 1. ck-ssm.py (로컬 실행용)

### 환경변수 설정
스크립트 실행 전에 AWS 프로필을 환경변수로 설정해야 합니다:

```bash
export AWS_PROFILE=your_profile_name
```

### 사용법
```bash
# 환경변수 설정 후 실행
export AWS_PROFILE=your_profile_name
python ck-ssm.py
```

### 출력 형태
```
🟢 Session Manager 연결 가능: i-1234567890abcdef0 (web-server-01)
🔴 Session Manager 연결 불가: i-0987654321fedcba0 (db-server-02)
🟢 Session Manager 연결 가능: i-abcdef1234567890 (app-server-03)
```

## 2. ck-ssm-lambda_fuc.py (AWS Lambda용)

### 특징
- **자동화**: 정기적으로 실행 가능 (CloudWatch Events/EventBridge 연동)
- **알림**: SSM 연결 가능한 인스턴스를 Slack으로 통보
- **서버리스**: AWS Lambda에서 실행되어 인프라 관리 불필요

### Lambda 설정

#### 1. 환경변수
Lambda 함수에 다음 환경변수 설정:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

#### 2. IAM 역할
Lambda 실행 역할에 다음 정책 추가:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ssm:DescribeInstanceInformation"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

#### 3. 의존성 패키지
Lambda 레이어 또는 배포 패키지에 `requests` 라이브러리 포함:
```bash
pip install requests -t ./package
```

### Slack 웹훅 설정

1. Slack 워크스페이스에서 앱 생성
2. Incoming Webhooks 활성화
3. 채널 선택 후 웹훅 URL 생성
4. Lambda 환경변수에 URL 설정

### 자동 실행 설정

CloudWatch Events(EventBridge)를 사용하여 정기 실행:

```bash
# 매일 오전 9시 실행 (UTC 기준 0시)
aws events put-rule \
    --name "ssm-check-daily" \
    --schedule-expression "cron(0 0 * * ? *)"

aws events put-targets \
    --rule "ssm-check-daily" \
    --targets "Id"="1","Arn"="arn:aws:lambda:ap-northeast-2:YOUR_ACCOUNT:function:ssm-checker"
```

### Lambda 출력
```json
{
    "checked": 15,
    "online": 12
}
```

### Slack 메시지 예시
```
🟢 Session Manager 연결 가능한 EC2 인스턴스 목록:
- i-1234567890abcdef0 (web-server-01)
- i-abcdef1234567890 (app-server-03)
- i-fedcba0987654321 (api-server-02)
```

## 코드 연관성

두 스크립트는 다음 함수를 공유합니다:

### 공통 함수
- `get_running_instances()`: 실행 중인 인스턴스 조회
- `is_ssm_online()`: SSM 연결 상태 확인

### 차이점
| 기능 | ck-ssm.py | ck-ssm-lambda_fuc.py |
|------|-----------|----------------------|
| 실행 환경 | 로컬 | AWS Lambda |
| 인증 방식 | 환경변수 프로필 | IAM 역할 |
| 출력 방식 | 콘솔 출력 | Slack 알림 |
| 결과 필터링 | 모든 인스턴스 표시 | 연결 가능한 인스턴스만 알림 |
| 자동화 | 수동 실행 | 스케줄 실행 가능 |

## SSM Session Manager란?

AWS Systems Manager Session Manager는 브라우저 기반 셸이나 AWS CLI를 통해 EC2 인스턴스를 관리할 수 있는 서비스입니다.

### 주요 장점
1. **보안**: SSH 키나 베스천 호스트 없이 안전한 접속
2. **감사**: 모든 세션 활동 로깅
3. **편의성**: 웹 콘솔에서 직접 터미널 접속
4. **네트워크**: 인바운드 포트 개방 불필요

## SSM 연결 요구사항

인스턴스가 SSM Session Manager에 연결되려면 다음 조건이 필요합니다:

### 1. IAM 역할
인스턴스에 다음 정책이 포함된 IAM 역할 연결:
- `AmazonSSMManagedInstanceCore`

### 2. SSM Agent
- Amazon Linux 2, Ubuntu 16.04+ 등에는 기본 설치
- 다른 OS는 수동 설치 필요

### 3. 네트워크 연결
다음 중 하나의 방법으로 AWS 서비스 접근:
- 인터넷 게이트웨이를 통한 인터넷 접속
- NAT 게이트웨이를 통한 아웃바운드 접속
- VPC 엔드포인트 구성

### 4. 보안 그룹
아웃바운드 HTTPS(443) 트래픽 허용

## 활용 시나리오

### 로컬 실행 (ck-ssm.py)
- **개발자**: 개발 환경에서 즉시 확인
- **운영자**: 문제 발생 시 빠른 상태 점검
- **일회성 검사**: 특정 시점의 전체 현황 파악

### Lambda 자동화 (ck-ssm-lambda_fuc.py)
- **정기 모니터링**: 매일/매주 자동 상태 확인
- **알림 시스템**: 팀 Slack 채널로 자동 보고
- **컴플라이언스**: 정기적인 접근성 감사
- **운영 대시보드**: 다른 모니터링 시스템과 연동

## 문제 해결

### 연결 불가 원인
1. **IAM 역할 누락**: 인스턴스에 SSM 권한이 있는 IAM 역할 연결 필요
2. **SSM Agent 미설치**: Agent 설치 및 실행 상태 확인
3. **네트워크 문제**: 아웃바운드 인터넷 접속 또는 VPC 엔드포인트 설정
4. **보안 그룹**: HTTPS 아웃바운드 트래픽 차단

### 확인 방법
```bash
# 인스턴스 내에서 SSM Agent 상태 확인
sudo systemctl status amazon-ssm-agent

# SSM Agent 재시작
sudo systemctl restart amazon-ssm-agent
```

## 확장 가능성

- **멀티 리전**: 여러 리전 동시 확인
- **상세 정보**: 인스턴스 타입, 상태, 태그 정보 추가
- **필터링**: 특정 태그나 조건으로 필터링
- **통계**: 시간별, 일별 연결 상태 통계
- **다른 알림**: 이메일, Teams, Discord 등 다양한 알림 채널
- **자동 수정**: 연결 문제 자동 해결 기능
