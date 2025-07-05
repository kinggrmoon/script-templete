#!/bin/bash

# ⚠️  보안 주의사항 ⚠️
# 이 스크립트를 사용하기 전에 다음 사항을 확인하세요:
# 1. PROFILE_NAME에 실제 회사명이나 민감한 정보가 포함되지 않았는지 확인
# 2. 실제 계정 ID나 이메일 주소가 로그에 출력되지 않도록 주의
# 3. 퍼블릭 레포지토리에 커밋하기 전에 민감한 정보가 포함되지 않았는지 검토

# 필수 도구 확인
check_requirements() {
  local missing_tools=()
  
  # AWS CLI 확인
  if ! command -v aws >/dev/null 2>&1; then
    missing_tools+=("aws-cli")
  fi
  
  # jq 확인
  if ! command -v jq >/dev/null 2>&1; then
    missing_tools+=("jq")
  fi
  
  if [ ${#missing_tools[@]} -ne 0 ]; then
    echo "[!] 다음 도구들이 설치되어 있지 않습니다:"
    for tool in "${missing_tools[@]}"; do
      echo "  - $tool"
    done
    echo ""
    echo "설치 방법:"
    echo "  brew install awscli jq"
    echo ""
    exit 1
  fi
}

# 요구사항 확인
check_requirements

# [1] SSO 프로파일명 지정
# PROFILE_NAME="aws-sso-profile"
PROFILE_NAME="aws-sso"

# [2] SSO 로그인 (브라우저 인증 필요)
echo "[*] SSO 로그인 시도..."
aws sso login --profile $PROFILE_NAME
if [ $? -ne 0 ]; then
  echo "[!] SSO 로그인 실패"
  exit 1
fi
echo "[✔] 로그인 성공"

# [3] SSO 세션 정보 가져오기
echo "[*] SSO 세션 정보 조회 중..."
SSO_SESSION=$(aws configure get sso_session --profile $PROFILE_NAME)
if [ -z "$SSO_SESSION" ]; then
  SSO_SESSION="default"
fi

# [4] 액세스 토큰 가져오기 - 캐시된 토큰 사용 (권장 방법)
echo "[*] 액세스 토큰 조회 중..."
SSO_CACHE_DIR="$HOME/.aws/sso/cache"

# SSO 캐시에서 가장 최신 토큰 파일 찾기
LATEST_CACHE=$(find "$SSO_CACHE_DIR" -name "*.json" -type f -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -1)

ACCESS_TOKEN=""
if [ -n "$LATEST_CACHE" ] && [ -f "$LATEST_CACHE" ]; then
  # 토큰이 만료되지 않았는지 확인
  EXPIRES_AT=$(jq -r '.expiresAt // empty' "$LATEST_CACHE" 2>/dev/null)
  CURRENT_TIME=$(date +%s)
  
  if [ -n "$EXPIRES_AT" ]; then
    # ISO 8601 형식의 시간을 epoch 시간으로 변환
    if command -v gdate >/dev/null 2>&1; then
      # macOS에서 GNU date 사용 (brew install coreutils)
      EXPIRES_EPOCH=$(gdate -d "$EXPIRES_AT" +%s 2>/dev/null)
    else
      # macOS 기본 date 명령 사용
      EXPIRES_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$EXPIRES_AT" +%s 2>/dev/null)
      if [ $? -ne 0 ]; then
        # 다른 형식 시도
        EXPIRES_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${EXPIRES_AT%Z}" +%s 2>/dev/null)
      fi
    fi
    
    if [ -n "$EXPIRES_EPOCH" ] && [ "$CURRENT_TIME" -lt "$EXPIRES_EPOCH" ]; then
      ACCESS_TOKEN=$(jq -r '.accessToken // empty' "$LATEST_CACHE" 2>/dev/null)
      echo "[✔] 유효한 캐시된 토큰 발견"
    else
      echo "[!] 캐시된 토큰이 만료됨"
    fi
  else
    # expiresAt이 없는 경우 토큰 사용 시도
    ACCESS_TOKEN=$(jq -r '.accessToken // empty' "$LATEST_CACHE" 2>/dev/null)
  fi
fi

if [ -z "$ACCESS_TOKEN" ]; then
  echo "[!] 유효한 액세스 토큰을 가져올 수 없습니다. SSO 재로그인을 시도합니다..."
  aws sso logout --profile $PROFILE_NAME 2>/dev/null
  
  echo "[*] SSO 재로그인 중..."
  aws sso login --profile $PROFILE_NAME
  if [ $? -ne 0 ]; then
    echo "[!] SSO 재로그인 실패"
    exit 1
  fi
  
  # 재로그인 후 새 토큰 검색
  echo "[*] 새 토큰 검색 중..."
  sleep 2  # 캐시 파일 생성 대기
  LATEST_CACHE=$(find "$SSO_CACHE_DIR" -name "*.json" -type f -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -1)
  if [ -n "$LATEST_CACHE" ] && [ -f "$LATEST_CACHE" ]; then
    ACCESS_TOKEN=$(jq -r '.accessToken // empty' "$LATEST_CACHE" 2>/dev/null)
  fi
fi

if [ -z "$ACCESS_TOKEN" ]; then
  echo "[!] 여전히 액세스 토큰을 가져올 수 없습니다."
  exit 1
fi

echo "[✔] 액세스 토큰 획득 성공"

# [5] 현재 로그인된 사용자에게 허용된 AWS 계정 및 역할 리스트 조회
echo "[*] 허용된 계정 및 역할 조회 중..."

# 계정 리스트 조회
ACCOUNTS=$(aws sso list-accounts --access-token "$ACCESS_TOKEN" --output json 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$ACCOUNTS" ]; then
  echo "[!] 계정 리스트 조회 실패. 토큰이 유효하지 않을 수 있습니다."
  exit 1
fi

ACCOUNT_COUNT=$(echo "$ACCOUNTS" | jq '.accountList | length' 2>/dev/null)
if [ -z "$ACCOUNT_COUNT" ] || [ "$ACCOUNT_COUNT" = "null" ]; then
  echo "[!] 계정 정보를 파싱할 수 없습니다."
  exit 1
fi

# 계정 정보를 보기 좋게 출력
echo "$ACCOUNTS" | jq -r '.accountList[] | "📦 계정ID: \(.accountId) | 계정명: \(.accountName) | 이메일: \(.emailAddress // "N/A")"'
echo ""

echo "[*] AWS CLI 프로파일 형태로 출력:"
echo "$ACCOUNTS" | jq -r '.accountList[] | "aws configure set profile.\(.accountId)_AdministratorAccess.region us-east-1"'
# echo "$ACCOUNTS" | jq -r '.accountList[] | "{\"profile\": \"" + .accountId + "_AdministratorAccess\", \"alias\": \"" + .accountName + "\"}"'
echo ""

echo "[✔] 허용된 계정 리스트 (총 ${ACCOUNT_COUNT}개):"

# [6] 각 계정별 역할 정보 출력 (선택사항)
echo ""
read -p "각 계정별 역할 정보를 조회하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "[*] 계정별 역할 조회 중..."
  for ACCOUNT_ID in $(echo "$ACCOUNTS" | jq -r '.accountList[].accountId'); do
    ROLES=$(aws sso list-account-roles --account-id $ACCOUNT_ID --access-token "$ACCESS_TOKEN" --output json 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$ROLES" ]; then
      ACCOUNT_NAME=$(echo "$ACCOUNTS" | jq -r --arg aid "$ACCOUNT_ID" '.accountList[] | select(.accountId == $aid) | .accountName')
      echo "📦 계정: $ACCOUNT_NAME ($ACCOUNT_ID)"
      echo "$ROLES" | jq -r '.roleList[] | " └─ 역할: \(.roleName) | 타입: \(.accountAssignmentCreationDate // "N/A")"'
      echo ""
    else
      echo "[!] 계정 $ACCOUNT_ID의 역할 정보 조회 실패"
    fi
  done
fi

echo "[✔] 스크립트 실행 완료"