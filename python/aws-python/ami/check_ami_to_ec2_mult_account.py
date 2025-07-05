import boto3
import csv
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

def find_ec2_instances_with_ami(profiles, ami_id, output_file):
    """
    특정 AMI ID를 사용하는 EC2 인스턴스를 여러 AWS 계정에서 검색합니다.
    v2 버전: 인스턴스 ID와 상태 정보 추가
    
    Args:
        profiles (list): AWS 프로필명 리스트
        ami_id (str): 검색할 AMI ID
        output_file (str): 결과를 저장할 CSV 파일명
    """
    all_matching_instances = []

    # 각 프로필별로 순차 처리
    for profile_name in profiles:
        try:
            print(f"\n[INFO] '{profile_name}' 프로필로 작업 시작...")
            
            # AWS 세션 초기화
            session = boto3.Session(profile_name=profile_name)
            ec2_client = session.client('ec2')

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
                        # 매칭된 인스턴스 정보 저장 (상세 정보 포함)
                        matching_instances.append({
                            'Profile': profile_name,
                            'InstanceName': instance_name or 'N/A',
                            'InstanceID': instance['InstanceId'],
                            'State': instance['State']['Name'],  # 인스턴스 상태 추가
                            'AMI_ID': instance['ImageId']
                        })

            # 프로필별 진행 상태 출력
            if matching_instances:
                print(f"[INFO] {len(matching_instances)}개의 인스턴스 발견.")
            else:
                print("[INFO] 해당 AMI ID를 사용하는 인스턴스가 없습니다.")

            # 전체 결과 리스트에 추가
            all_matching_instances.extend(matching_instances)

        except (NoCredentialsError, PartialCredentialsError):
            print(f"[ERROR] '{profile_name}' 프로필의 인증 정보를 찾을 수 없습니다.")
        except Exception as e:
            print(f"[ERROR] '{profile_name}' 프로필에서 오류 발생: {str(e)}")

    # 모든 프로필의 결과를 CSV 파일에 저장
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Profile', 'InstanceName', 'InstanceID', 'State', 'AMI_ID'])
            writer.writeheader()
            writer.writerows(all_matching_instances)

        print(f"\n[INFO] 결과가 '{output_file}' 파일에 저장되었습니다.")
    except Exception as e:
        print(f"[ERROR] CSV 파일 저장 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    # 사용자로부터 입력 받기
    profiles = input("AWS Profile Names (쉼표로 구분): ").strip().split(',')
    profiles = [p.strip() for p in profiles if p.strip()]  # 공백 제거 및 빈 항목 제거
    ami_id = input("AMI ID: ").strip()
    output_csv = input("Output CSV File Name (default: output.csv): ").strip() or "output.csv"

    # 입력 검증
    if not profiles:
        print("[ERROR] 프로파일 목록이 비어 있습니다.")
    else:
        # 다중 계정 AMI 검색 실행 (상세 정보 포함)
        find_ec2_instances_with_ami(profiles, ami_id, output_csv)