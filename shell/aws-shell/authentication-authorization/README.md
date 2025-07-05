# AWS SSO 인증 및 권한 스크립트

이 디렉토리에는 AWS SSO(Single Sign-On) 인증과 권한 관리를 위한 스크립트들이 포함되어 있습니다.

## 파일 목록

### sso-login-and-get-accountlist.sh

AWS SSO를 통해 로그인하고 접근 가능한 계정 및 역할 목록을 조회하는 스크립트입니다.

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
sso_account_id = 123456789012
sso_role_name = AdministratorAccess
region = us-east-1
output = json

[sso-session my-session]
sso_start_url = https://your-org.awsapps.com/start
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

📦 계정ID: 123456789012 | 계정명: Production Account | 이메일: admin@company.com
📦 계정ID: 234567890123 | 계정명: Development Account | 이메일: dev@company.com
📦 계정ID: 345678901234 | 계정명: Staging Account | 이메일: staging@company.com

[*] AWS CLI 프로파일 형태로 출력:
aws configure set profile.123456789012_AdministratorAccess.region us-east-1
aws configure set profile.234567890123_AdministratorAccess.region us-east-1
aws configure set profile.345678901234_AdministratorAccess.region us-east-1
```

