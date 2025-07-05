import boto3
import os
import requests

def get_running_instances(region='ap-northeast-2'):
    """
    지정된 리전에서 실행 중인 EC2 인스턴스 목록을 조회합니다.
    (ck-ssm.py와 동일한 로직)
    
    Args:
        region (str): AWS 리전명 (기본값: ap-northeast-2)
    
    Returns:
        list: 인스턴스 ID와 Name 태그를 포함한 딕셔너리 리스트
    """
    ec2 = boto3.client('ec2', region_name=region)
    instances = []
    
    # 페이지네이션을 사용하여 모든 실행 중인 인스턴스 조회
    paginator = ec2.get_paginator('describe_instances')
    for page in paginator.paginate(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]):
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                name = None
                
                # 인스턴스의 Name 태그 추출
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break
                
                instances.append({'InstanceId': instance_id, 'Name': name})
    return instances

def is_ssm_online(instance_id, region='ap-northeast-2'):
    """
    특정 인스턴스가 SSM(Systems Manager)에 온라인 상태인지 확인합니다.
    (ck-ssm.py와 동일한 로직)
    
    Args:
        instance_id (str): EC2 인스턴스 ID
        region (str): AWS 리전명 (기본값: ap-northeast-2)
    
    Returns:
        bool: SSM 온라인 상태 여부
    """
    ssm = boto3.client('ssm', region_name=region)
    try:
        # SSM에서 해당 인스턴스 정보 조회
        response = ssm.describe_instance_information(
            Filters=[{'Key': 'InstanceIds', 'Values': [instance_id]}]
        )
        infos = response.get('InstanceInformationList', [])
        
        # 인스턴스가 SSM에 등록되어 있고 온라인 상태인지 확인
        if infos and infos[0]['PingStatus'] == 'Online':
            return True
    except Exception:
        # SSM 조회 실패 시 (권한 부족, 네트워크 오류 등)
        pass
    return False

def send_slack_message(webhook_url, message):
    """
    Slack 웹훅을 통해 메시지를 전송합니다.
    
    Args:
        webhook_url (str): Slack 웹훅 URL
        message (str): 전송할 메시지
    
    Returns:
        bool: 메시지 전송 성공 여부
    """
    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

def lambda_handler(event, context):
    """
    AWS Lambda 함수의 메인 핸들러입니다.
    SSM에 연결 가능한 인스턴스 목록을 Slack으로 전송합니다.
    
    Args:
        event: Lambda 이벤트 객체
        context: Lambda 컨텍스트 객체
    
    Returns:
        dict: 확인된 인스턴스 수와 온라인 인스턴스 수를 포함한 응답
    """
    # 검사할 AWS 리전 설정
    region = 'ap-northeast-2'
    
    # 환경변수에서 Slack 웹훅 URL 가져오기
    slack_url = os.environ.get('SLACK_WEBHOOK_URL')
    if not slack_url:
        raise RuntimeError("SLACK_WEBHOOK_URL 환경변수가 필요합니다.")

    # 실행 중인 모든 인스턴스 조회
    instances = get_running_instances(region)
    online_instances = []
    
    # 각 인스턴스의 SSM 연결 상태 확인
    for inst in instances:
        if is_ssm_online(inst['InstanceId'], region):
            online_instances.append(inst)

    # SSM 연결 가능한 인스턴스가 있으면 Slack 메시지 전송
    if online_instances:
        msg_lines = ["🟢 Session Manager 연결 가능한 EC2 인스턴스 목록:"]
        for inst in online_instances:
            msg_lines.append(f"- {inst['InstanceId']} ({inst['Name']})")
        message = "\n".join(msg_lines)
        send_slack_message(slack_url, message)

    # 실행 결과 반환
    return {
        "checked": len(instances),
        "online": len(online_instances)
    }