#!/bin/bash

## 사전 환경 셋팅
## python, pip 설치
## aws-cli 설치 
## aws-mfa 설치

echo "AWS Auth Setting Start"

# 입력변수 확인
if [ "$#" -ne 2 ];then
  # IAM STS 인증
  aws-mfa --profile $1
  
  echo "역할전환하지 않습니다." 
  echo "역할전환을 진행하려면 2차 변수값을 입력하세요. ex) ./authset.sh [ID] [dev|test|prod]"

else
  # IAM STS 인증
  aws-mfa --profile $1
  
  # IAM STS 역할전환 인증
  ## DEV (Serverless)

  if [ "$2" = "readonlyUser" ];then
    aws-mfa --profile $1 --assume-role arn:aws:iam::1****2****3:role/readonlyUser-role --short-term-suffix $2 --role-session-name $2 --duration 43200
  fi

  if [ "$2" = "serviceUser" ];then
    aws-mfa --profile $1 --assume-role arn:aws:iam::1****2****3:role/serviceUser-role --short-term-suffix $2 --role-session-name $2 --duration 43200
  fi

  if [ "$2" = "admin" ];then
    aws-mfa --profile $1 --assume-role arn:aws:iam::1****2****3:role/admin-role --short-term-suffix $2 --role-session-name $2 --duration 43200
  fi

  AWS_PROFILE=$1-$2
  export AWS_PROFILE=${AWS_PROFILE}
fi


