import boto3
import csv
from collections import defaultdict

def get_ec2_instances(profile_name, account_name, region_name="ap-northeast-2", 
                     keyword_filter=None, tag_filters=None, instance_states=None):
    """
    특정 조건에 맞는 EC2 인스턴스를 필터링하여 조회합니다.
    - 키워드 기반 인스턴스 (이름 또는 AMI 이름에 키워드 포함)
    - 태그 기반 인스턴스 (지정된 태그 키-값 쌍)
    - 조건이 없으면 모든 인스턴스 조회
    
    Args:
        profile_name (str): AWS 프로필명
        account_name (str): 계정 별칭
        region_name (str): AWS 리전명 (기본값: ap-northeast-2)
        keyword_filter (str): 검색할 키워드 (None이면 키워드 필터링 안함)
        tag_filters (list): 태그 필터 리스트 (None이면 태그 필터링 안함)
        instance_states (list): 조회할 인스턴스 상태 리스트 (기본값: ["running"])
    
    Returns:
        list: 필터링된 인스턴스 정보 리스트
    """
    # 기본 인스턴스 상태 설정
    if instance_states is None:
        instance_states = ["running"]
    
    # AWS 세션 및 EC2 클라이언트 초기화
    session = boto3.Session(profile_name=profile_name)
    ec2 = session.client("ec2", region_name=region_name)
    
    # 지정된 상태의 인스턴스만 조회
    response = ec2.describe_instances(Filters=[{"Name": "instance-state-name", "Values": instance_states}])
    
    instances = []
    image_ids = set()
    
    # 모든 인스턴스에서 사용 중인 AMI ID 수집
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            image_ids.add(instance["ImageId"])
    
    # AMI 정보를 배치로 조회하여 API 호출 최적화
    image_details = ec2.describe_images(ImageIds=list(image_ids))
    image_os_map = {}
    image_name_map = {}
    
    def determine_os_type(image):
        """
        AMI 정보를 기반으로 OS 타입을 더 정확하게 판별합니다.
        AMI 설명에서 OS 버전 정보도 추출합니다.
        
        Args:
            image (dict): AMI 이미지 정보
            
        Returns:
            str: OS 타입
        """
        # 기본 정보 추출
        name = image.get("Name", "").lower()
        description = image.get("Description", "").lower()
        platform = image.get("Platform", "").lower()
        platform_details = image.get("PlatformDetails", "").lower()
        architecture = image.get("Architecture", "").lower()
        virtualization_type = image.get("VirtualizationType", "").lower()
        
        # AMI 설명에서 OS 정보 추출 함수
        def extract_os_from_description(desc):
            """
            AMI 설명에서 OS 정보를 추출합니다.
            예: "base-image:GI-amazonlinux2023-arm-V20240819-CyberArk..."
            """
            # Amazon Linux 패턴 검사 (al2023, EKS 노드 패턴 추가)
            if any(pattern in desc for pattern in ["amazonlinux2023", "amazon-linux-2023", "al2023"]):
                return "Amazon Linux 2023"
            elif "amazonlinux2" in desc or "amazon-linux-2" in desc:
                return "Amazon Linux 2"
            elif "amazonlinux" in desc or "amazon-linux" in desc:
                # 버전 번호가 없으면 Amazon Linux 1로 추정
                return "Amazon Linux 1"
            
            # Ubuntu 패턴 검사
            ubuntu_patterns = [
                ("ubuntu-22.04", "Ubuntu 22.04 LTS"),
                ("ubuntu22.04", "Ubuntu 22.04 LTS"),
                ("ubuntu-jammy", "Ubuntu 22.04 LTS"),
                ("ubuntu-20.04", "Ubuntu 20.04 LTS"),
                ("ubuntu20.04", "Ubuntu 20.04 LTS"),
                ("ubuntu-focal", "Ubuntu 20.04 LTS"),
                ("ubuntu-18.04", "Ubuntu 18.04 LTS"),
                ("ubuntu18.04", "Ubuntu 18.04 LTS"),
                ("ubuntu-bionic", "Ubuntu 18.04 LTS"),
                ("ubuntu", "Ubuntu")
            ]
            
            for pattern, os_name in ubuntu_patterns:
                if pattern in desc:
                    return os_name
            
            # CentOS 패턴 검사
            centos_patterns = [
                ("centos-8", "CentOS 8"),
                ("centos8", "CentOS 8"),
                ("centos-7", "CentOS 7"),
                ("centos7", "CentOS 7"),
                ("centos-6", "CentOS 6"),
                ("centos6", "CentOS 6"),
                ("centos", "CentOS")
            ]
            
            for pattern, os_name in centos_patterns:
                if pattern in desc:
                    return os_name
            
            # RHEL 패턴 검사
            rhel_patterns = [
                ("rhel-9", "Red Hat Enterprise Linux 9"),
                ("rhel9", "Red Hat Enterprise Linux 9"),
                ("rhel-8", "Red Hat Enterprise Linux 8"),
                ("rhel8", "Red Hat Enterprise Linux 8"),
                ("rhel-7", "Red Hat Enterprise Linux 7"),
                ("rhel7", "Red Hat Enterprise Linux 7"),
                ("red-hat", "Red Hat Enterprise Linux"),
                ("rhel", "Red Hat Enterprise Linux")
            ]
            
            for pattern, os_name in rhel_patterns:
                if pattern in desc:
                    return os_name
            
            # Debian 패턴 검사
            debian_patterns = [
                ("debian-12", "Debian 12"),
                ("debian12", "Debian 12"),
                ("debian-11", "Debian 11"),
                ("debian11", "Debian 11"),
                ("debian-10", "Debian 10"),
                ("debian10", "Debian 10"),
                ("debian", "Debian")
            ]
            
            for pattern, os_name in debian_patterns:
                if pattern in desc:
                    return os_name
            
            # Windows 패턴 검사
            if any(pattern in desc for pattern in ["windows-2022", "windows2022", "win2022"]):
                return "Windows Server 2022"
            elif any(pattern in desc for pattern in ["windows-2019", "windows2019", "win2019"]):
                return "Windows Server 2019"
            elif any(pattern in desc for pattern in ["windows-2016", "windows2016", "win2016"]):
                return "Windows Server 2016"
            elif any(pattern in desc for pattern in ["windows", "win-"]):
                return "Windows"
            
            return None
        
        # AWS에서 제공하는 Platform 필드를 우선 확인 (가장 정확)
        if platform == "windows":
            # 설명에서 더 상세한 Windows 버전 찾기
            desc_os = extract_os_from_description(description)
            if desc_os and desc_os.startswith("Windows"):
                return desc_os
            return "Windows"
        
        # AMI 설명에서 OS 정보 추출 시도 (우선순위 높음)
        desc_os = extract_os_from_description(description)
        if desc_os:
            return desc_os
        
        # AMI 이름에서 OS 정보 추출 시도
        desc_os = extract_os_from_description(name)
        if desc_os:
            return desc_os
        
        # PlatformDetails 필드 확인 (더 상세한 정보)
        if "windows" in platform_details:
            return "Windows"
        elif "linux" in platform_details:
            # Linux 계열 상세 분류 (EKS 노드 패턴 추가)
            if any(keyword in name for keyword in ["amzn2-ami", "amazonlinux2", "amazon-linux-2"]):
                return "Amazon Linux 2"
            elif any(keyword in name for keyword in ["al2023-ami", "amazon-linux-2023", "amazonlinux2023", "al2023"]):
                return "Amazon Linux 2023"
            elif any(keyword in name for keyword in ["al2-ami", "amazon-linux-ami"]):
                return "Amazon Linux 1"
            elif any(keyword in name for keyword in ["ubuntu"]):
                # Ubuntu 버전 상세 분류
                if "22.04" in name or "jammy" in name:
                    return "Ubuntu 22.04 LTS"
                elif "20.04" in name or "focal" in name:
                    return "Ubuntu 20.04 LTS"
                elif "18.04" in name or "bionic" in name:
                    return "Ubuntu 18.04 LTS"
                else:
                    return "Ubuntu"
            elif any(keyword in name for keyword in ["centos"]):
                return "CentOS"
            elif any(keyword in name for keyword in ["rhel", "red-hat"]):
                return "Red Hat Enterprise Linux"
            elif any(keyword in name for keyword in ["debian"]):
                return "Debian"
            elif any(keyword in name for keyword in ["suse", "sles"]):
                return "SUSE Linux"
            elif any(keyword in name for keyword in ["alpine"]):
                return "Alpine Linux"
            else:
                return "Linux (Other)"
        
        # 이름과 설명 기반 분류 (Platform 정보가 없는 경우)
        if any(keyword in name or keyword in description for keyword in ["windows", "win-"]):
            return "Windows"
        elif any(keyword in name for keyword in ["amzn2-ami", "amazonlinux2", "amazon-linux-2"]):
            return "Amazon Linux 2"
        elif any(keyword in name for keyword in ["al2023-ami", "amazon-linux-2023", "amazonlinux2023", "al2023"]):
            return "Amazon Linux 2023"
        elif any(keyword in name for keyword in ["al2-ami", "amazon-linux-ami"]):
            return "Amazon Linux 1"
        elif "ubuntu" in name:
            if "22.04" in name or "jammy" in name:
                return "Ubuntu 22.04 LTS"
            elif "20.04" in name or "focal" in name:
                return "Ubuntu 20.04 LTS"
            elif "18.04" in name or "bionic" in name:
                return "Ubuntu 18.04 LTS"
            else:
                return "Ubuntu"
        elif "centos" in name:
            return "CentOS"
        elif any(keyword in name for keyword in ["rhel", "red-hat"]):
            return "Red Hat Enterprise Linux"
        elif "debian" in name:
            return "Debian"
        elif any(keyword in name for keyword in ["suse", "sles"]):
            return "SUSE Linux"
        elif "alpine" in name:
            return "Alpine Linux"
        elif any(keyword in name for keyword in ["freebsd"]):
            return "FreeBSD"
        elif any(keyword in name for keyword in ["openbsd"]):
            return "OpenBSD"
        elif any(keyword in name for keyword in ["netbsd"]):
            return "NetBSD"
        
        # 기본적으로 Linux 계열로 추정 (대부분의 EC2 인스턴스가 Linux)
        if platform_details and "linux" not in platform_details and platform != "windows":
            return "Unknown"
        
        return "Linux (Unknown Distribution)"
    
    # AMI 이름과 설명을 기반으로 OS 타입 분류 및 이름 매핑
    for image in image_details["Images"]:
        image_id = image["ImageId"]
        image_name_map[image_id] = image.get("Name", "Unknown")
        image_os_map[image_id] = determine_os_type(image)
    
    # 필터링 조건에 맞는 인스턴스 정보 수집
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            image_id = instance["ImageId"]
            instance_type = instance["InstanceType"]
            instance_state = instance["State"]["Name"]  # 인스턴스 상태 추가
            os_type = image_os_map.get(image_id, "Other")
            ami_name = image_name_map.get(image_id, "Unknown")
            
            # 태그를 소문자로 변환하여 매핑
            tags = {tag["Key"].lower(): tag["Value"].lower() for tag in instance.get("Tags", [])}
            instance_name = tags.get("name", "N/A")
            
            # 필터링 로직 개선: 조건이 없으면 모든 인스턴스 포함
            should_include = False
            
            # 키워드와 태그 필터가 모두 없으면 모든 인스턴스 포함
            if keyword_filter is None and (tag_filters is None or len(tag_filters) == 0):
                should_include = True
            else:
                # 필터링 조건 1: 키워드 기반 필터링 (키워드가 지정된 경우만)
                if keyword_filter and (keyword_filter.lower() in instance_name.lower() or 
                                     keyword_filter.lower() in ami_name.lower()):
                    should_include = True
                
                # 필터링 조건 2: 태그 기반 필터링 (태그 필터가 지정된 경우만)
                if tag_filters and not should_include:
                    for tag_filter in tag_filters:
                        tag_key = tag_filter["key"].lower()
                        tag_value = tag_filter["value"].lower()
                        if tags.get(tag_key) == tag_value:
                            should_include = True
                            break
            
            # 조건을 만족하는 인스턴스만 결과에 추가 (상태 정보 포함)
            if should_include:
                instances.append([account_name, instance_id, instance_name, instance_state, os_type, image_id, ami_name, instance_type])
    
    return instances

if __name__ == "__main__":
    # ===== 필터링 조건 설정 =====
    # 필터링 조건 1: 키워드 검색 (인스턴스명 또는 AMI명에 포함된 키워드)
    # None 또는 빈 문자열로 설정하면 키워드 필터링 비활성화
    KEYWORD_FILTER = None  # 예: "jdk11", "web", "db", "api" 등 또는 None
    
    # 필터링 조건 2: 태그 기반 필터링 (여러 조건 중 하나라도 맞으면 포함)
    # 빈 리스트 또는 None으로 설정하면 태그 필터링 비활성화
    TAG_FILTERS = [
        # {"key": "team", "value": "devops"},
        # {"key": "project", "value": "project01"},
        # {"key": "environment", "value": "production"},
        # {"key": "APM", "value": "true"}
    ]
    
    # 필터링 조건 3: EC2 인스턴스 상태 필터링
    # 가능한 상태: running, stopped, stopping, starting, shutting-down, terminated, terminating, pending
    INSTANCE_STATES = [
        "running",
        # "stopped",
        # "stopping", 
        # "starting",
        # "pending"
    ]
    
    # 조회할 AWS 계정 프로필 정의
    aws_profiles = {
        # "aws-alias-name": "profile-name",
        # "aws-alias-name2": "profile-name2",
    }
    region = "ap-northeast-2"
    
    # CSV 파일 생성 및 결과 저장
    output_file = "filtered_ec2_list.csv"
    header = ["Account", "Instance ID", "Instance Name", "State", "OS", "AMI ID", "AMI Name", "Instance Type"]
    
    # 필터링 조건 출력
    print(f"필터링 조건:")
    print(f"  - 키워드: {KEYWORD_FILTER if KEYWORD_FILTER else '모든 키워드'}")
    print(f"  - 태그 조건: {TAG_FILTERS if TAG_FILTERS else '모든 태그'}")
    print(f"  - 인스턴스 상태: {INSTANCE_STATES}")
    print(f"  - 조회 리전: {region}")
    
    # 조건이 모두 비어있으면 전체 조회 안내
    if not KEYWORD_FILTER and not TAG_FILTERS:
        print(f"  ⚠️  필터링 조건이 없어 지정된 상태의 모든 EC2 인스턴스를 조회합니다.")
    print()
    
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        
        # 콘솔 출력 헤더
        print("Account | Instance ID | Instance Name | State | OS | AMI ID | AMI Name | Instance Type")
        print("------------------------------------------------------------------------------------------------")
        
        # 각 계정별로 인스턴스 조회 및 출력
        total_instances = 0
        for alias, profile in aws_profiles.items():
            instances = get_ec2_instances(profile, alias, region, KEYWORD_FILTER, TAG_FILTERS, INSTANCE_STATES)
            for instance in instances:
                print(" | ".join(instance))
                writer.writerow(instance)
                total_instances += 1
    
    print(f"\n총 {total_instances}개의 인스턴스가 조회되었습니다.")
    print(f"Output saved to {output_file}")
