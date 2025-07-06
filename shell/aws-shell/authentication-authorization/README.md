# AWS 인증 및 권한 관리 스크립트

이 디렉토리에는 AWS 인증과 권한 관리를 위한 다양한 스크립트들이 포함되어 있습니다.

## 파일 목록

### 1. sso-login-and-get-accountlist.sh

AWS SSO를 통해 로그인하고 접근 가능한 계정 및 역할 목록을 조회하는 스크립트입니다.

### 2. aws-sts-mfa-auth.sh

AWS STS와 MFA를 사용한 인증 및 역할 전환 스크립트입니다.

## 📁 디렉토리 구조

```
authentication-authorization/
├── sso-login-and-get-accountlist.sh    # SSO 로그인 및 계정 조회
├── aws-sts-mfa-auth.sh                 # MFA 인증 및 역할 전환
└── README.md                           # 이 문서
```

## 🔄 스크립트 비교

| 기능 | sso-login-and-get-accountlist.sh | aws-sts-mfa-auth.sh |
|------|-----------------------------------|---------------------|
| **인증 방식** | AWS SSO | MFA + STS |
| **주요 용도** | 계정 조회 및 SSO 로그인 | 역할 전환 및 임시 자격증명 |
| **브라우저 필요** | ✅ (SSO 로그인시) | ❌ |
| **MFA 필요** | ❌ (SSO에서 처리) | ✅ |
| **역할 전환** | ❌ | ✅ |
| **세션 관리** | SSO 캐시 기반 | 12시간 임시 토큰 |

## 🎯 사용 시나리오

### SSO 환경
- **sso-login-and-get-accountlist.sh** 사용
- 여러 AWS 계정에 SSO로 접근
- 계정 목록 확인 및 브라우저 기반 인증

### 전통적인 IAM + MFA 환경
- **aws-sts-mfa-auth.sh** 사용
- MFA 디바이스를 통한 보안 강화
- 특정 역할로의 권한 전환

---

## 상세 가이드

### sso-login-and-get-accountlist.sh

#### 주요 기능
- AWS SSO 자동 로그인
- 캐시된 토큰 활용으로 빠른 재인증
- 토큰 만료 확인 및 자동 갱신
- 접근 가능한 AWS 계정 목록 조회
- 계정별 역할 정보 조회 (선택 사항)
- 에러 처리 및 재시도 로직

#### 사전 요구사항
```bash
# Homebrew를 통한 필수 도구 설치
brew install awscli jq
```

#### AWS CLI 설정
스크립트 실행 전에 AWS SSO 프로파일이 설정되어 있어야 합니다:

```bash
# AWS CLI 설정
aws configure sso

# 또는 직접 config 파일 편집
~/.aws/config
```

예시 설정:
```ini
[profile aws-sso]
sso_session = my-session
sso_account_id = YOUR_ACCOUNT_ID
sso_role_name = AdministratorAccess
region = us-east-1
output = json

[sso-session my-session]
sso_start_url = https://YOUR_ORG.awsapps.com/start
sso_region = us-east-1
sso_registration_scopes = sso:account:access
```

#### 사용법
```bash
# 스크립트 실행
./sso-login-and-get-accountlist.sh
```

#### 스크립트 수정
프로파일명을 변경하려면 스크립트 내의 다음 부분을 수정하세요:
```bash
PROFILE_NAME="aws-sso"  # 여기를 원하는 프로파일명으로 변경
```

#### 문제 해결

##### ForbiddenException 오류
- **문제**: `An error occurred (ForbiddenException) when calling the GetRoleCredentials operation: No access`
- **원인**: 직접적인 `get-role-credentials` API 호출 권한 부족
- **해결**: 이 스크립트는 캐시된 토큰을 사용하도록 개선되어 이 문제를 회피합니다

##### 토큰 만료 오류
- **문제**: 캐시된 토큰이 만료됨
- **해결**: 스크립트가 자동으로 재로그인을 시도합니다

##### jq 명령어 없음
- **문제**: `jq: command not found`
- **해결**: `brew install jq`로 설치

#### 출력 예시
```
[✔] 로그인 성공
[✔] 유효한 캐시된 토큰 발견
[✔] 액세스 토큰 획득 성공
[*] 허용된 계정 및 역할 조회 중...
[✔] 허용된 계정 리스트 (총 3개):

📦 계정ID: 111111111111 | 계정명: Production Account | 이메일: admin@example.com
📦 계정ID: 222222222222 | 계정명: Development Account | 이메일: dev@example.com
📦 계정ID: 333333333333 | 계정명: Staging Account | 이메일: staging@example.com

[*] AWS CLI 프로파일 형태로 출력:
aws configure set profile.111111111111_AdministratorAccess.region us-east-1
aws configure set profile.222222222222_AdministratorAccess.region us-east-1
aws configure set profile.333333333333_AdministratorAccess.region us-east-1
```

---

### aws-sts-mfa-auth.sh

AWS STS(Security Token Service)와 MFA(Multi-Factor Authentication)를 사용한 인증 및 역할 전환 스크립트입니다.

#### 주요 기능
- AWS MFA 인증을 통한 임시 자격 증명 획득
- IAM 역할 전환 (AssumeRole)
- 다중 역할 지원 (readonlyUser, serviceUser, admin)
- 12시간 세션 지속 시간
- 자동 환경 변수 설정

#### 사전 요구사항
```bash
# aws-mfa 도구 설치
pip install aws-mfa

# MFA 디바이스가 AWS 계정에 설정되어 있어야 함
```

#### 사용법

**1. 기본 MFA 인증 (역할 전환 없음)**
```bash
./aws-sts-mfa-auth.sh PROFILE_NAME
```

**2. MFA 인증 + 역할 전환**
```bash
./aws-sts-mfa-auth.sh PROFILE_NAME ROLE_TYPE
```

#### 지원하는 역할 유형
- `readonlyUser` - 읽기 전용 권한
- `serviceUser` - 제한된 서비스 권한
- `admin` - 전체 관리 권한

#### 사용 예시
```bash
# 기본 MFA 인증만
./aws-sts-mfa-auth.sh my-profile

# 읽기 전용 역할로 전환
./aws-sts-mfa-auth.sh my-profile readonlyUser

# 관리자 역할로 전환
./aws-sts-mfa-auth.sh my-profile admin
```

#### 스크립트 수정 필요사항
**중요**: 실제 사용 전에 스크립트 내의 계정 ID를 수정해야 합니다:
```bash
# 현재 (마스킹된 예시)
arn:aws:iam::1****2****3:role/readonlyUser-role

# 실제 사용시 변경 필요
arn:aws:iam::YOUR_ACTUAL_ACCOUNT_ID:role/readonlyUser-role
```

#### 작동 원리
1. **인수 검증**: 1개 인수(기본 인증) 또는 2개 인수(역할 전환)
2. **MFA 인증**: `aws-mfa --profile PROFILE_NAME` 실행
3. **역할 전환**: 지정된 역할로 AssumeRole 수행 (선택사항)
4. **환경 설정**: `AWS_PROFILE` 환경 변수 자동 설정

---

## 라이선스

