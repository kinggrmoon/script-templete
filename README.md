# Script Template Repository

이 저장소는 다양한 AWS 관리 스크립트와 자동화 템플릿을 포함하고 있습니다.

## 📁 디렉토리 구조

- `python/` - Python 기반 AWS 관리 스크립트
  - `awsIamControlCmd/` - IAM 사용자 및 권한 관리 스크립트
- `shell/` - Shell 스크립트 모음
  - `aws-shell/` - AWS CLI 관련 스크립트
    - `authentication-authorization/` - SSO 로그인 및 권한 관리
    - `aws-sts-mfa-auth.sh/` - MFA 인증
    - `aws-tags.sh/` - AWS 리소스 태깅

## 🔒 보안 주의사항

**중요**: 이 저장소는 퍼블릭 저장소입니다. 민감한 정보를 커밋하지 않도록 주의해주세요.

- 📖 [보안 가이드라인](SECURITY.md) - 반드시 읽어주세요
- 🚫 실제 AWS 계정 ID, 자격 증명, 이메일 주소 등을 포함하지 마세요
- ✅ 모든 예시는 가상의 데이터를 사용합니다

## 🚀 시작하기

각 디렉토리의 README 파일을 참조하여 스크립트 사용법을 확인하세요.

## 🤝 기여하기

1. 코드 기여 전에 [보안 가이드라인](SECURITY.md)을 확인하세요
2. 민감한 정보가 포함되지 않았는지 검토하세요
3. Pull Request를 제출하세요
