import boto3
from collections import defaultdict

def get_ec2_os_distribution(profile_name, region_name="ap-northeast-2"):
    """
    지정된 AWS 프로필과 리전에서 실행 중인 EC2 인스턴스의 OS 분포를 조회합니다.
    
    Args:
        profile_name (str): AWS 프로필명
        region_name (str): AWS 리전명 (기본값: ap-northeast-2)
    
    Returns:
        tuple: (총 인스턴스 수, OS 분포 딕셔너리)
    """
    # AWS 세션 생성 및 EC2 클라이언트 초기화
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client("ec2", region_name=region_name)
    
    # 실행 중인 EC2 인스턴스만 조회
    response = ec2.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])
    
    # 카운터 초기화
    total_instances = 0
    os_distribution = defaultdict(int)  # OS별 인스턴스 수를 저장할 딕셔너리
    image_ids = set()  # 고유한 AMI ID들을 저장할 집합
    
    # 모든 예약(Reservation)과 인스턴스를 순회하며 AMI ID 수집
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            total_instances += 1
            image_ids.add(instance["ImageId"])
    
    # 수집된 AMI ID들에 대한 상세 정보를 배치로 조회 (API 호출 최적화)
    image_details = ec2.describe_images(ImageIds=list(image_ids))
    image_os_map = {}  # AMI ID와 OS 타입을 매핑할 딕셔너리
    
    # 각 AMI의 이름과 설명을 분석하여 OS 타입 결정
    for image in image_details["Images"]:
        image_id = image["ImageId"]
        name = image.get("Name", "").lower()
        description = image.get("Description", "").lower()
        
        # Amazon Linux 2 판별
        if "amzn2-ami" in name or "amazonlinux2" in name or "amazon linux 2" in description:
            image_os_map[image_id] = "Amazon Linux 2"
        # Amazon Linux 2023 판별
        elif "al2023-ami" in name or "amazon linux 2023" in description or "amazonlinux2023" in description:
            image_os_map[image_id] = "Amazon Linux 2023"
        # Windows 판별
        elif "windows" in name or "windows" in description:
            image_os_map[image_id] = "Windows"
        # 기타 OS
        else:
            image_os_map[image_id] = "Other"
    
    # 각 인스턴스를 다시 순회하며 OS별로 카운트
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            os = image_os_map.get(instance["ImageId"], "Other")
            os_distribution[os] += 1
    
    return total_instances, os_distribution

if __name__ == "__main__":
    # AWS 계정별 프로필과 별칭 매핑
    # 주석 처리된 계정들은 필요에 따라 활성화하여 사용
    aws_profiles = {
        "profile01": "alias01",
        "profile02": "alias02",
        "profile03": "alias03"
    }
    
    # 조회할 AWS 리전 설정
    region = "ap-northeast-2"  
    
    # 결과 테이블 헤더 출력
    print("Alias | Total EC2 | Amazon Linux 2 | Amazon Linux 2023 | Windows | Other | AL2 used %")
    print("--------------------------------------------------------------------------------")
    
    # 각 AWS 계정별로 EC2 OS 분포 조회 및 결과 출력
    for profile, alias in aws_profiles.items():
        # EC2 OS 분포 정보 조회
        total_count, os_dist = get_ec2_os_distribution(profile, region)
        
        # OS별 인스턴스 수 추출
        al2_count = os_dist.get("Amazon Linux 2", 0)
        al2023_count = os_dist.get("Amazon Linux 2023", 0)
        windows_count = os_dist.get("Windows", 0)
        other_count = os_dist.get("Other", 0)
        
        # Amazon Linux 2 사용률 계산 (백분율)
        al2_percentage = (al2_count / total_count * 100) if total_count > 0 else 0.0
        
        # 결과를 테이블 형태로 출력
        print(f"{alias} | {total_count} | {al2_count} | {al2023_count} | {windows_count} | {other_count} | {al2_percentage:.2f}%")
