#!/bin/bash

# 보안 검사 스크립트
# 퍼블릭 레포지토리에 커밋하기 전에 민감한 정보가 있는지 검사

echo "🔍 보안 검사를 시작합니다..."
echo ""

ISSUES_FOUND=0

# 1. AWS 계정 ID 검사 (예시가 아닌 실제로 보이는 것들)
echo "[1] AWS 계정 ID 검사 중..."
SUSPICIOUS_ACCOUNTS=$(grep -r -E '\b[0-9]{12}\b' . \
    --exclude-dir=.git \
    --exclude="*.md" \
    --exclude="security-check.sh" \
    | grep -v "111111111111\|222222222222\|333333333333\|999999999999\|YOUR_ACCOUNT_ID")

if [ -n "$SUSPICIOUS_ACCOUNTS" ]; then
    echo "⚠️  의심스러운 AWS 계정 ID 발견:"
    echo "$SUSPICIOUS_ACCOUNTS"
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 2. 실제 이메일 주소 검사
echo "[2] 이메일 주소 검사 중..."
SUSPICIOUS_EMAILS=$(grep -r -E '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' . \
    --exclude-dir=.git \
    --exclude="*.md" \
    --exclude="security-check.sh" \
    | grep -v "@example\.\|@test\.\|@localhost\|YOUR_EMAIL")

if [ -n "$SUSPICIOUS_EMAILS" ]; then
    echo "⚠️  의심스러운 이메일 주소 발견:"
    echo "$SUSPICIOUS_EMAILS"
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 3. AWS Access Key 패턴 검사
echo "[3] AWS Access Key 검사 중..."
SUSPICIOUS_KEYS=$(grep -r -E '(AKIA|ASIA)[A-Z0-9]{16}' . \
    --exclude-dir=.git \
    --exclude="*.md" \
    --exclude="security-check.sh" \
    | grep -v "XXXXXXXXXXXXXXXXX\|YYYYYYYYYYYYYYYYY\|YOUR_ACCESS_KEY")

if [ -n "$SUSPICIOUS_KEYS" ]; then
    echo "⚠️  의심스러운 AWS Access Key 발견:"
    echo "$SUSPICIOUS_KEYS"
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 4. Secret Key 패턴 검사
echo "[4] Secret Key 검사 중..."
SUSPICIOUS_SECRETS=$(grep -r -E '[a-zA-Z0-9/+=]{40}' . \
    --exclude-dir=.git \
    --exclude="*.md" \
    --exclude="security-check.sh" \
    --exclude="*.py" \
    | head -5)  # Python 파일의 base64 임포트 등을 제외

if [ -n "$SUSPICIOUS_SECRETS" ]; then
    echo "⚠️  의심스러운 Secret Key 패턴 발견:"
    echo "$SUSPICIOUS_SECRETS"
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 5. 실제 도메인/URL 검사
echo "[5] 실제 도메인/URL 검사 중..."
SUSPICIOUS_URLS=$(grep -r -E 'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' . \
    --exclude-dir=.git \
    --exclude="security-check.sh" \
    | grep -v "example\.\|localhost\|127\.0\.0\.1\|amazonaws\.com\|github\.com\|docs\.\|YOUR_")

if [ -n "$SUSPICIOUS_URLS" ]; then
    echo "⚠️  검토가 필요한 URL 발견:"
    echo "$SUSPICIOUS_URLS"
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 6. 개인 정보 검사
echo "[6] 개인 정보 검사 중..."
SUSPICIOUS_PERSONAL=$(grep -r -E '/Users/[a-zA-Z0-9]+' . \
    --exclude-dir=.git \
    --exclude="security-check.sh")

if [ -n "$SUSPICIOUS_PERSONAL" ]; then
    echo "⚠️  개인 경로 정보 발견:"
    echo "$SUSPICIOUS_PERSONAL"
    echo ""
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 결과 출력
echo "=================================="
if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ 보안 검사 완료: 문제없음"
    echo "   퍼블릭 레포지토리에 커밋해도 안전합니다."
else
    echo "🚨 보안 검사 완료: $ISSUES_FOUND개 이슈 발견"
    echo "   위에서 발견된 항목들을 검토하고 수정한 후 커밋하세요."
    echo ""
    echo "📝 수정 방법:"
    echo "   - 실제 계정 ID → YOUR_ACCOUNT_ID 또는 111111111111"
    echo "   - 실제 이메일 → user@example.com"
    echo "   - 실제 키/토큰 → XXXXXXXXXXXXXXXXX"
    echo "   - 실제 URL → https://YOUR_ORG.example.com"
    exit 1
fi
