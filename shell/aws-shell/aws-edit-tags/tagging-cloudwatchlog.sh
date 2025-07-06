#!/bin/bash

echo "CloudWatch Logs Tag Manager v2.0"

# 설정: 환경변수 또는 기본값 사용
aws_profile="${AWS_PROFILE:-myAwsProfile}"
aws_region="${AWS_REGION:-us-west-2}"

# 지원하는 리전 목록
SUPPORTED_REGIONS=(
  "af-south-1"
  "ap-east-1"
  "ap-northeast-1"
  "ap-northeast-2"
  "ap-northeast-3"
  "ap-south-1"
  "ap-south-2"
  "ap-southeast-1"
  "ap-southeast-2"
  "ap-southeast-3"
  "ca-central-1"
  "eu-central-1"
  "eu-central-2"
  "eu-north-1"
  "eu-south-1"
  "eu-south-2"
  "eu-west-1"
  "eu-west-2"
  "eu-west-3"
  "me-central-1"
  "me-south-1"
  "sa-east-1"
  "us-east-1"
  "us-east-2"
  "us-west-1"
  "us-west-2"
)

# 색상 코드 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수들
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 리전 유효성 검사
validate_region() {
    local region=$1
    for supported_region in "${SUPPORTED_REGIONS[@]}"; do
        if [[ "$region" == "$supported_region" ]]; then
            return 0
        fi
    done
    return 1
}

# AWS CLI 및 프로파일 검증
validate_aws_setup() {
    # AWS CLI 설치 확인
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI가 설치되지 않았습니다. 'brew install awscli'로 설치하세요."
        exit 1
    fi

    # 프로파일 확인
    if ! aws configure list --profile "$aws_profile" &> /dev/null; then
        log_error "AWS 프로파일 '$aws_profile'을 찾을 수 없습니다."
        log_info "다음 명령으로 프로파일을 설정하세요: aws configure --profile $aws_profile"
        exit 1
    fi

    # 리전 유효성 검사
    if ! validate_region "$aws_region"; then
        log_error "지원하지 않는 리전입니다: $aws_region"
        log_info "지원하는 리전: ${SUPPORTED_REGIONS[*]}"
        exit 1
    fi

    log_info "AWS 프로파일: $aws_profile"
    log_info "AWS 리전: $aws_region"
}

## select CloudWatch log
cloudwatch_log_group_name=$2

## add tagging
run(){
    local command="aws --profile ${aws_profile} --region ${aws_region} ${cmd} ${opt}"
    log_info "실행 중: $command"
    
    if result=$(eval "$command" 2>&1); then
        log_success "명령 실행 성공"
        if [ -n "$result" ]; then
            echo "$result"
        fi
        return 0
    else
        log_error "명령 실행 실패: $result"
        return 1
    fi
}

## run cmd check
dryrun(){
    log_warning "DRY RUN 모드 - 실제로 실행되지 않습니다:"
    echo "aws --profile ${aws_profile} --region ${aws_region} ${cmd} ${opt}"
}

## 지정된 리소스에 태깅
tagging(){
  ## 'Key^Value' 'Key^Value'
  tags=('Application^projectapp' 'Service^mobile' 'Role^mobilelog' 'Owner^user01')
  tag_sum=""
  for tag in ${tags[@]}
  do
	  add=$(echo ${tag} |awk -F"^" '{print $1"="$2","}')
	  tag_sum=${tag_sum}${add}
  done
  #tag_sum=${tag_sum::-1}
  tag_sum=${tag_sum%?}
  log_info "생성된 태그: ${tag_sum}"
  echo ${tag_sum}
  exit;
}

## 리소스 목록을 체크하여 태깅
tagging_file(){
  if [ -f cloudwatch_logs.list ];then
    log_info "cloudwatch_logs.list 파일을 처리 중..."
    local count=0
    local success=0
    while read log_group tag
    do
      # 빈 줄이나 주석 건너뛰기
      [[ -z "$log_group" || "$log_group" =~ ^#.*$ ]] && continue
      
      count=$((count + 1))
      log_info "[$count] 처리 중: $log_group"
      cmd="logs tag-log-group"
      opt="--log-group-name ${log_group} --tags $tag"
      if run; then
        success=$((success + 1))
      fi
    done < cloudwatch_logs.list
    log_success "완료: $success/$count 개 항목 처리 성공"
  else
    log_error "cloudwatch_logs.list 파일을 찾을 수 없습니다."
    exit 1
  fi
}

## 리소스 삭제 목록을 체크하여 태깅 삭제 
tagging_file_del(){
  if [ -f cloudwatch_logs_del.list ];then
    log_info "cloudwatch_logs_del.list 파일을 처리 중..."
    local count=0
    local success=0
    while read log_group tag
    do
      # 빈 줄이나 주석 건너뛰기
      [[ -z "$log_group" || "$log_group" =~ ^#.*$ ]] && continue
      
      count=$((count + 1))
      log_info "[$count] 태그 삭제 중: $log_group에서 $tag"
      cmd="logs untag-log-group"
      opt="--log-group-name ${log_group} --tags $tag"
      if run; then
        success=$((success + 1))
      fi
    done < cloudwatch_logs_del.list
    log_success "완료: $success/$count 개 항목 처리 성공"
  else
    log_error "cloudwatch_logs_del.list 파일을 찾을 수 없습니다."
    exit 1
  fi
}

# 도움말 출력
show_help() {
    echo "CloudWatch Logs Tag Manager v2.0"
    echo ""
    echo "사용법: $0 [옵션] [로그그룹명]"
    echo ""
    echo "옵션:"
    echo "  list              모든 로그 그룹 목록 조회"
    echo "  detail <그룹명>   특정 로그 그룹의 태그 조회"
    echo "  edit <그룹명>     특정 로그 그룹에 기본 태그 추가"
    echo "  edit_list         cloudwatch_logs.list 파일의 모든 항목에 태그 추가"
    echo "  del <그룹명>      특정 로그 그룹에서 Owner 태그 삭제"
    echo "  del_list          cloudwatch_logs_del.list 파일의 모든 항목에서 태그 삭제"
    echo "  help              이 도움말 표시"
    echo ""
    echo "환경변수:"
    echo "  AWS_PROFILE       AWS 프로파일 (기본값: myAwsProfile)"
    echo "  AWS_REGION        AWS 리전 (기본값: us-west-2)"
    echo ""
    echo "예시:"
    echo "  $0 list"
    echo "  $0 detail /aws/lambda/my-function"
    echo "  AWS_PROFILE=prod-profile $0 edit /aws/lambda/my-function"
    echo "  AWS_REGION=ap-northeast-2 $0 edit_list"
}

# 초기 검증 실행
validate_aws_setup

# 인수 확인
if [ $# -eq 0 ]; then
    log_error "옵션을 입력해주세요."
    show_help
    exit 1
fi

## 도움말
if [ "$1" == "help" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ];then
    show_help
    exit 0
fi

## 태깅 list 조회 
if [ "$1" == "list" ];then
  log_info "모든 CloudWatch Logs 그룹 조회 중..."
  cmd="logs describe-log-groups"
  opt=""
  run
fi

## 태깅 조회
if [ "$1" == "detail" ];then
  if [ -z "$2" ]; then
    log_error "로그 그룹명을 입력해주세요."
    log_info "예시: $0 detail /aws/lambda/my-function"
    exit 1
  fi
  log_info "로그 그룹 '$cloudwatch_log_group_name'의 태그 조회 중..."
  cmd="logs list-tags-log-group"
  opt="--log-group-name ${cloudwatch_log_group_name}"
  run  
fi

## 태그 등록 (오타 수정: 태강 -> 태그)
if [ "$1" == "edit" ];then
   if [ -z "$2" ]; then
     log_error "로그 그룹명을 입력해주세요."
     log_info "예시: $0 edit /aws/lambda/my-function"
     exit 1
   fi
   log_info "로그 그룹 '$cloudwatch_log_group_name'에 기본 태그 추가 중..."
   tagging
   cmd="logs tag-log-group"
   opt="--log-group-name ${cloudwatch_log_group_name} --tags ${tag_sum}"
   run      
fi

## 파일 목록의 태깅 등록
if [ "$1" == "edit_list" ];then
   tagging_file
fi

## 태깅 삭제
if [ "$1" == "del" ];then
   if [ -z "$2" ]; then
     log_error "로그 그룹명을 입력해주세요."
     log_info "예시: $0 del /aws/lambda/my-function"
     exit 1
   fi
   log_info "로그 그룹 '$cloudwatch_log_group_name'에서 Owner 태그 삭제 중..."
   del_tag_name="Owner"
   cmd="logs untag-log-group"
   opt="--log-group-name ${cloudwatch_log_group_name} --tags ${del_tag_name}"
   run      
fi

## 파일 목록의 태깅 삭제
if [ "$1" == "del_list" ];then
   tagging_file_del
fi

# 알 수 없는 옵션 처리
if [[ ! "$1" =~ ^(list|detail|edit|edit_list|del|del_list|help)$ ]]; then
    log_error "알 수 없는 옵션: $1"
    show_help
    exit 1
fi