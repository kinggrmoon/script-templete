# AWS CloudWatch Logs 태깅 관리 스크립트 v2.0

이 디렉토리에는 AWS CloudWatch Logs 그룹의 태그를 관리하기 위한 개선된 스크립트와 설정 파일들이 포함되어 있습니다.

## 🆕 v2.0 개선사항
- ✅ **환경변수 지원**: AWS_PROFILE, AWS_REGION 환경변수 지원
- ✅ **향상된 에러 처리**: 상세한 오류 메시지와 실행 결과 검증
- ✅ **컬러 로깅**: 색상이 있는 로그 메시지로 가독성 향상
- ✅ **도움말 기능**: --help 옵션 추가
- ✅ **입력 검증**: AWS CLI, 프로파일, 리전 유효성 검사
- ✅ **진행 상황 표시**: 일괄 처리시 진행률 표시

## 📁 파일 구조

```
aws-edit-tags/
├── tagging-cloudwatchlog.sh    # CloudWatch Logs 태깅 관리 메인 스크립트 v2.0
├── cloudwatch_logs.list        # 태깅할 로그 그룹 목록 (개선된 예시)
├── cloudwatch_logs_del.list    # 태그를 삭제할 로그 그룹 목록 (개선된 예시)
└── README.md                   # 이 문서
```

## 🎯 주요 기능

### tagging-cloudwatchlog.sh
- CloudWatch Logs 그룹에 태그 추가/삭제
- 개별 로그 그룹 또는 목록 파일을 통한 일괄 처리
- 다양한 AWS 리전 지원
- Dry-run 기능으로 안전한 실행 확인

## 🛠️ 사전 요구사항

```bash
# AWS CLI 설치 및 설정
brew install awscli
aws configure

# 또는 프로파일 설정
aws configure --profile YOUR_PROFILE_NAME
```

## ⚙️ 설정 방법

### 1. 프로파일 및 리전 설정
스크립트 상단에서 다음 설정을 수정하세요:

```bash
# AWS 프로파일 설정
aws_profile="myAwsProfile"  # 실제 AWS 프로파일명으로 변경

# AWS 리전 설정 (원하는 리전의 주석을 해제)
aws_region="us-west-2"      # 사용할 리전으로 변경
```

### 2. 기본 태그 설정
스크립트 내의 `tagging()` 함수에서 기본 태그를 수정할 수 있습니다:

```bash
tags=('Application^projectapp' 'Service^mobile' 'Role^mobilelog' 'Owner^user01')
```


## 🚀 사용법

### 도움말 확인
```bash
./tagging-cloudwatchlog.sh help
```

### 환경변수 설정 (선택사항)
```bash
# AWS 프로파일 설정
export AWS_PROFILE=my-production-profile

# AWS 리전 설정  
export AWS_REGION=ap-northeast-2

# 또는 명령어와 함께 실행
AWS_PROFILE=prod-profile AWS_REGION=us-east-1 ./tagging-cloudwatchlog.sh list
```

### 기본 명령어 구조
```bash
./tagging-cloudwatchlog.sh [옵션] [로그그룹명]
```

### 1. 로그 그룹 목록 조회
```bash
./tagging-cloudwatchlog.sh list
```

### 2. 특정 로그 그룹의 태그 조회
```bash
./tagging-cloudwatchlog.sh detail /aws/lambda/my-function
```

### 3. 개별 로그 그룹에 태그 추가
```bash
./tagging-cloudwatchlog.sh edit /aws/lambda/my-function
```
- 스크립트에 정의된 기본 태그가 적용됩니다

### 4. 파일 목록을 통한 일괄 태그 추가
```bash
./tagging-cloudwatchlog.sh edit_list
```
- `cloudwatch_logs.list` 파일의 모든 항목에 태그를 추가합니다

### 5. 개별 로그 그룹의 태그 삭제
```bash
./tagging-cloudwatchlog.sh del /aws/lambda/my-function
```
- 기본적으로 "Owner" 태그가 삭제됩니다

### 6. 파일 목록을 통한 일괄 태그 삭제
```bash
./tagging-cloudwatchlog.sh del_list
```
- `cloudwatch_logs_del.list` 파일의 모든 항목에서 지정된 태그를 삭제합니다

## 📋 개선된 파일 형식

### cloudwatch_logs.list (태그 추가용)
```
# CloudWatch Logs 그룹 태깅 설정 파일
# 형식: 로그그룹명 태그키=태그값,태그키=태그값,...
# 예시:
/aws/lambda/user-service Application=UserManagement,Environment=Production,Owner=BackendTeam
/aws/apigateway/user-api Application=UserManagement,Environment=Production,Owner=BackendTeam
```

### cloudwatch_logs_del.list (태그 삭제용)
```
# CloudWatch Logs 그룹 태그 삭제 설정 파일  
# 형식: 로그그룹명 삭제할태그키
# 예시:
/aws/lambda/test-function Environment
/aws/apigateway/test-api Owner
```

## 🎨 새로운 기능들

### 컬러 로깅
- 🔵 **INFO**: 일반 정보
- 🟢 **SUCCESS**: 성공 메시지
- 🟡 **WARNING**: 경고 메시지
- 🔴 **ERROR**: 오류 메시지

### 진행률 표시
일괄 처리시 현재 진행 상황을 표시합니다:
```
[INFO] cloudwatch_logs.list 파일을 처리 중...
[INFO] [1] 처리 중: /aws/lambda/function1
[SUCCESS] 명령 실행 성공
[INFO] [2] 처리 중: /aws/lambda/function2
[SUCCESS] 명령 실행 성공
[SUCCESS] 완료: 2/2 개 항목 처리 성공
```

### 자동 검증
스크립트 실행 전 자동으로 다음을 검증합니다:
- AWS CLI 설치 여부
- AWS 프로파일 존재 여부
- 리전 유효성
- 필수 인수 존재 여부

## 🔧 설정 방법

### 1. 실행 권한 부여
```bash
chmod +x tagging-cloudwatchlog.sh
```

### 2. 기본 태그 설정
스크립트 내의 `tagging()` 함수에서 기본 태그를 수정할 수 있습니다:

```bash
tags=('Application^projectapp' 'Service^mobile' 'Role^mobilelog' 'Owner^user01')
```

**✅ v2.0에서 수정됨**: Owner 오타가 수정되었습니다.

## 🛠️ 사전 요구사항
```
