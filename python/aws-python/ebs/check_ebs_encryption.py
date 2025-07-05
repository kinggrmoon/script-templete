import boto3

def get_ebs_encryption_status(profiles):
    """
    여러 AWS 계정의 EBS 볼륨 암호화 상태를 조회하고 분석합니다.
    
    Args:
        profiles (dict): AWS 프로필명과 별칭의 매핑 딕셔너리
    """
    for profile, alias in profiles.items():
        print(f"\n=== AWS Profile: {profile} (Alias: {alias}) ===")
        
        # AWS 세션 설정 및 EC2 클라이언트 초기화
        boto3.setup_default_session(profile_name=profile)
        ec2 = boto3.client('ec2')

        # 해당 계정의 모든 EBS 볼륨 조회
        volumes = ec2.describe_volumes()['Volumes']
        
        # 분석 결과를 저장할 변수들 초기화
        unattached_volumes = []  # 인스턴스에 연결되지 않은 볼륨 목록
        root_encrypted_count = root_total_count = 0  # 루트 볼륨 암호화 통계
        data_encrypted_count = data_total_count = 0  # 데이터 볼륨 암호화 통계
        unencrypted_instances = {}  # 암호화되지 않은 볼륨을 가진 인스턴스 정보

        # 각 볼륨을 순회하며 암호화 상태 분석
        for volume in volumes:
            attachments = volume.get('Attachments', [])  # 볼륨이 연결된 인스턴스 정보
            is_encrypted = volume['Encrypted']  # 볼륨 암호화 여부
            is_root = False  # 루트 볼륨 여부 판별 플래그

            if attachments:  # 볼륨이 인스턴스에 연결된 경우
                for attachment in attachments:
                    instance_id = attachment['InstanceId']
                    
                    # 디바이스명을 통해 루트 볼륨 여부 판별
                    # /dev/sda 또는 /dev/xvda로 끝나는 경우 루트 볼륨
                    if attachment.get('Device', '').startswith('/dev/sd') or attachment.get('Device', '').startswith('/dev/xvd'):
                        if attachment['Device'].endswith('a'):
                            is_root = True
                            break
                
                # 루트 볼륨과 데이터 볼륨 분류 및 암호화 통계 수집
                if is_root:
                    root_total_count += 1
                    if is_encrypted:
                        root_encrypted_count += 1
                else:
                    data_total_count += 1
                    if is_encrypted:
                        data_encrypted_count += 1
                
                # 암호화되지 않은 볼륨을 가진 인스턴스 정보 수집
                if not is_encrypted:
                    if instance_id not in unencrypted_instances:
                        unencrypted_instances[instance_id] = []
                    unencrypted_instances[instance_id].append(volume['VolumeId'])
            else:
                # 인스턴스에 연결되지 않은 볼륨 목록에 추가
                unattached_volumes.append(volume['VolumeId'])

        # 암호화율 계산 (0으로 나누기 방지)
        root_encryption_rate = (root_encrypted_count / root_total_count * 100) if root_total_count else 0
        data_encryption_rate = (data_encrypted_count / data_total_count * 100) if data_total_count else 0

        # 분석 결과 출력
        print(f"Unattached EBS Volumes: {unattached_volumes}")
        print(f"Root Volume Encryption: {root_encrypted_count} / {root_total_count} ({root_encryption_rate:.2f}%)")
        print(f"Non-Root Volume Encryption: {data_encrypted_count} / {data_total_count} ({data_encryption_rate:.2f}%)")

        # 비암호화 EBS가 연결된 인스턴스 상세 정보 출력
        if unencrypted_instances:
            print("Instances with Unencrypted EBS:")
            # 인스턴스 정보를 배치로 조회하여 API 호출 최적화
            instances = ec2.describe_instances(InstanceIds=list(unencrypted_instances.keys()))['Reservations']
            
            for reservation in instances:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    # 인스턴스의 Name 태그 조회 (없으면 'N/A')
                    name_tag = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A')
                    print(f"Instance Name: {name_tag}, ID: {instance_id}, Unencrypted Volumes: {unencrypted_instances[instance_id]}")

if __name__ == "__main__":
    # AWS 계정별 프로필과 별칭 매핑
    # 주석 처리된 계정들은 필요에 따라 활성화하여 사용
    aws_profiles = {
        "profile01": "alias01",
        "profile02": "alias02",
        "profile03": "alias03"
    }
    
    # EBS 암호화 상태 조회 실행
    get_ebs_encryption_status(aws_profiles)