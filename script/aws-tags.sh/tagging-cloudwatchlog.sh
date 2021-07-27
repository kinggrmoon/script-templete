#!/bin/bash

echo "cloudwatch tag manager"

aws_profile="grmoon-devadm"

## select region 

#aws_region="ap-northeast-1"
#aws_region="ap-northeast-2"
#aws_region="ap-south-1"
#aws_region="ap-southeast-1"
#aws_region="eu-central-1"
#aws_region="eu-west-2"
#aws_region="us-east-1"
#aws_region="us-east-2"
aws_region="us-west-2"

## select CloudWatch log
cloudwatch_log_group_name=$2

## add tagging
run(){
      aws --profile ${aws_profile} \
      --region ${aws_region} \
	  ${cmd} \
	  ${opt}
}

## run cmd check
dryrun(){
      echo aws --profile ${aws_profile} \
      --region ${aws_region} \
	  ${cmd} \
	  ${opt}
}

## 지정된 리소스에 태깅
tagging(){
  ## 'Key^Value' 'Key^Value'
  tags=('Application^projectapp' 'Service^mobile' 'Role^mobilelog' 'Onwer^user01')
  tag_sum=""
  for tag in ${tags[@]}
  do
	  add=$(echo ${tag} |awk -F"^" '{print $1"="$2","}')
	  tag_sum=${tag_sum}${add}
  done
  #tag_sum=${tag_sum::-1}
  tag_sum=${tag_sum%?}
  echo ${tag_sum}
  exit;
}

## 리소스 목록을 체크하여 태깅
tagging_file(){
  if [ -f cloudwatch_logs.list ];then
    while read log_group tag
    do
      cmd="logs tag-log-group"
      opt="--log-group-name ${log_group} --tags $tag"
      run
    done < cloudwatch_logs.list
  else
    echo "file not found"
  fi
}

## 리소스 삭제 목록을 체크하여 태깅 삭제 
tagging_file_del(){
  if [ -f cloudwatch_logs_del.list ];then
    while read log_group tag
    do
      cmd="logs untag-log-group"
      opt="--log-group-name ${log_group} --tags $tag"
      run
    done < cloudwatch_logs_del.list
  else
    echo "file not found"
  fi
}

## 태깅 list 조회 
if [ "$1" == "list" ];then
  cmd="logs describe-log-groups"
  opt=""
  run
fi

## 태깅 조회
if [ "$1" == "detail" ];then 
  cmd="logs list-tags-log-group"
  opt="--log-group-name ${cloudwatch_log_group_name}"
  run  
fi

## 태강 등록 
if [ "$1" == "edit" ];then
   tagging
   #tagging_file
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
   del_tag_name="Onwer"
   cmd="logs untag-log-group"
   opt="--log-group-name ${cloudwatch_log_group_name} --tags ${del_tag_name}"
   run      
fi

## 파일 목록의 태깅 삭제
if [ "$1" == "del_list" ];then
   tagging_file_del
fi