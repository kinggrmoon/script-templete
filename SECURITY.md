# 보안 가이드라인 (Security Guidelines)

이 저장소는 AWS 관련 스크립트와 템플릿을 포함하고 있습니다. 다음 보안 가이드라인을 반드시 준수해주세요.

## 🚨 절대 커밋하면 안 되는 정보

### 1. AWS 자격 증명
- AWS Access Key ID (`AKIA*` 또는 `ASIA*` 형태)
- AWS Secret Access Key
- AWS Session Token
- IAM Role ARN (실제 계정 ID 포함)

### 2. 개인 식별 정보
- 실제 이메일 주소
- 실제 사용자명
- 전화번호
- 실제 회사명이나 조직명

### 3. 민감한 설정
- 실제 AWS 계정 ID (12자리 숫자)
- 실제 SSO URL
- 내부 서버 주소나 도메인
- 데이터베이스 연결 정보

## ✅ 안전한 예시 사용법

### AWS 계정 ID
```bash
# ❌ 실제 계정 ID (예시)
ACCOUNT_ID="999999999999"

# ✅ 예시용 계정 ID
ACCOUNT_ID="111111111111"
ACCOUNT_ID="YOUR_ACCOUNT_ID"
```

### 이메일 주소
```bash
# ❌ 실제 이메일
EMAIL="user@real-company.com"

# ✅ 예시용 이메일
EMAIL="user@example.com"
EMAIL="admin@example.org"
```

### 회사명/조직명
```bash
# ❌ 실제 회사명
PROFILE_NAME="realcompany-aws-sso"

# ✅ 일반적인 이름
PROFILE_NAME="aws-sso"
PROFILE_NAME="my-org-sso"
```

## 🔍 커밋 전 체크리스트

커밋하기 전에 다음 사항들을 확인하세요:

- [ ] 실제 AWS 계정 ID가 포함되지 않았는지 확인
- [ ] 실제 이메일 주소가 포함되지 않았는지 확인
- [ ] 실제 회사명이나 조직명이 포함되지 않았는지 확인
- [ ] AWS 자격 증명이 포함되지 않았는지 확인
- [ ] 내부 URL이나 도메인이 포함되지 않았는지 확인

## 🛠️ 자동화된 검사

다음 명령어들로 민감한 정보가 포함되지 않았는지 확인할 수 있습니다:

```bash
# AWS 계정 ID 형태 검색 (12자리 숫자)
grep -r "\b[0-9]{12}\b" .

# AWS Access Key 형태 검색
grep -r "AKIA[A-Z0-9]\{16\}" .
grep -r "ASIA[A-Z0-9]\{16\}" .

# 실제 이메일 도메인 검색 (example.com 제외)
grep -r "@[a-zA-Z0-9.-]\+\.[a-zA-Z]\{2,\}" . | grep -v "@example"
```

## 📝 발견 시 대응 방법

만약 민감한 정보가 이미 커밋되었다면:

1. **즉시 조치**: 해당 자격 증명 무효화 (AWS 콘솔에서)
2. **이력 정리**: `git filter-branch` 또는 `BFG Repo-Cleaner` 사용
3. **강제 푸시**: `git push --force-with-lease` (팀과 협의 후)
4. **새 자격 증명**: 필요한 경우 새로운 자격 증명 생성

## 🤝 기여 가이드라인

이 저장소에 기여할 때:

1. 모든 예시는 가상의 데이터를 사용하세요
2. 실제 환경에서 테스트한 후 민감한 정보를 제거하세요
3. Pull Request 전에 위의 체크리스트를 확인하세요
4. 의심스러운 부분이 있으면 리뷰어에게 문의하세요

---

**기억하세요**: 한 번 퍼블릭 저장소에 올라간 정보는 완전히 삭제하기 어렵습니다. 
사전에 주의하는 것이 최선의 방법입니다.
