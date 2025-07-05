import boto3
import os

# 환경변수에서 AWS 프로필 읽기
profile = os.environ.get("AWS_PROFILE")
if not profile:
    raise RuntimeError("AWS_PROFILE 환경변수가 설정되어 있지 않습니다.")

# AWS 세션 생성
session = boto3.Session(profile_name=profile)

def get_running_instances(region='ap-northeast-2'):
    """
    지정된 리전에서 실행 중인 EC2 인스턴스 목록을 조회합니다.
    
    Args:
        region (str): AWS 리전명 (기본값: ap-northeast-2)
    
    Returns:
        list: 인스턴스 ID와 Name 태그를 포함한 딕셔너리 리스트
    """
    ec2 = session.client('ec2', region_name=region)
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
    
    Args:
        instance_id (str): EC2 인스턴스 ID
        region (str): AWS 리전명 (기본값: ap-northeast-2)
    
    Returns:
        bool: SSM 온라인 상태 여부
    """
    ssm = session.client('ssm', region_name=region)
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

def run_check(region='ap-northeast-2'):
    """
    지정된 리전의 모든 실행 중인 인스턴스에 대해 SSM 연결 상태를 확인합니다.
    
    Args:
        region (str): AWS 리전명 (기본값: ap-northeast-2)
    
    Returns:
        list: (인스턴스ID, 이름, 상태) 튜플의 리스트
    """
    instances = get_running_instances(region)
    results = []
    
    for inst in instances:
        instance_id = inst['InstanceId']
        name = inst['Name']
        ssm_online = is_ssm_online(instance_id, region)
        
        # 연결 상태에 따른 시각적 표시
        if ssm_online:
            status = '🟢 Session Manager 연결 가능'
        else:
            status = '🔴 Session Manager 연결 불가'
        
        results.append((instance_id, name, status))
    return results

if __name__ == '__main__':
    # 기본 리전 설정
    region = 'ap-northeast-2'
    
    # SSM 연결 상태 확인 실행
    ssm_status = run_check(region)
    
    # 결과 출력
    for iid, name, stat in ssm_status:
        print(f"{stat}: {iid} ({name})")