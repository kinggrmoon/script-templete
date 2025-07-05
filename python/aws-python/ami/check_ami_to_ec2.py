import boto3
import csv
import sys
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def find_ec2_instances_with_ami(profile_name, ami_id, output_file):
    """
    특정 AMI ID를 사용하는 EC2 인스턴스를 단일 AWS 계정에서 검색합니다.
    
    Args:
        profile_name (str): AWS 프로필명
        ami_id (str): 검색할 AMI ID
        output_file (str): 결과를 저장할 CSV 파일명
    """
    try:
        # AWS 세션 초기화
        session = boto3.Session(profile_name=profile_name)
        ec2_client = session.client('ec2')

        print(f"[INFO] AWS 프로필 '{profile_name}' 로드 성공")
        print("[INFO] EC2 인스턴스를 검색하는 중...")

        # 모든 EC2 인스턴스 검색 (모든 상태 포함)
        instances = ec2_client.describe_instances()

        # 지정된 AMI ID를 사용하는 인스턴스 필터링
        matching_instances = []
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                if instance.get('ImageId') == ami_id:
                    instance_name = None
                    # 태그에서 Name 태그 추출
                    if 'Tags' in instance:
                        for tag in instance['Tags']:
                            if tag['Key'] == 'Name':
                                instance_name = tag['Value']
                                break
                    # 매칭된 인스턴스 정보 저장
                    matching_instances.append({
                        'InstanceName': instance_name or 'N/A',
                        'AMI_ID': instance['ImageId']
                    })
        
        # 결과 출력
        if matching_instances:
            print(f"[INFO] 총 {len(matching_instances)}개의 인스턴스가 발견되었습니다.")
        else:
            print("[INFO] 해당 AMI ID를 사용하는 인스턴스를 찾을 수 없습니다.")

        # 결과를 CSV 파일로 저장
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['InstanceName', 'AMI_ID'])
            writer.writeheader()
            writer.writerows(matching_instances)

        print(f"[INFO] 결과가 '{output_file}' 파일에 저장되었습니다.")

    except (NoCredentialsError, PartialCredentialsError):
        print("[ERROR] AWS 인증 정보를 찾을 수 없습니다.")
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")

if __name__ == "__main__":
    # 사용자로부터 입력 받기
    aws_profile = input("AWS Profile Name: ").strip()
    ami_id = input("AMI ID: ").strip()
    output_csv = input("Output CSV File Name (default: output.csv): ").strip() or "output.csv"

    # AMI 검색 실행
    find_ec2_instances_with_ami(aws_profile, ami_id, output_csv)