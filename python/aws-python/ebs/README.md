# EBS Encryption Status Checker

AWS 계정별로 EBS 볼륨의 암호화 상태를 조회하고 분석하는 Python 스크립트입니다.

## 기능

- 여러 AWS 계정의 EBS 볼륨 암호화 상태 분석
- 루트 볼륨과 데이터 볼륨 분리 통계
- 암호화되지 않은 볼륨을 가진 인스턴스 상세 정보 제공
- 연결되지 않은 볼륨 목록 조회
- 계정별 암호화율 계산

## 필요 조건

### Python 패키지
```bash
pip install boto3
```

### AWS 설정
- AWS CLI 설정 완료
- 각 계정별 AWS 프로필 구성
- EC2 읽기 권한 (ec2:DescribeVolumes, ec2:DescribeInstances)

## 사용법

### 1. 기본 실행
```bash
python check_ebs_encryption.py
```

### 2. 스크립트 수정
`aws_profiles` 딕셔너리에서 조회하고 싶은 계정의 주석을 해제하거나 새로운 프로필을 추가:

```python
aws_profiles = {
    "your_profile_name": "your_alias",
    # 추가 프로필...
}
```

## 출력 형태

```
=== AWS Profile: 491215854025_AdministratorAccess (Alias: alias01) ===
Unattached EBS Volumes: ['vol-12345678', 'vol-87654321']
Root Volume Encryption: 8 / 10 (80.00%)
Non-Root Volume Encryption: 15 / 20 (75.00%)
Instances with Unencrypted EBS:
Instance Name: web-server-01, ID: i-1234567890abcdef0, Unencrypted Volumes: ['vol-abcdef123456789']
Instance Name: db-server-02, ID: i-0987654321fedcba0, Unencrypted Volumes: ['vol-9876543210fedcba']
```

### 출력 정보 설명

#### 기본 통계
- **Unattached EBS Volumes**: 인스턴스에 연결되지 않은 볼륨 ID 목록
- **Root Volume Encryption**: 루트 볼륨 암호화 현황 (암호화된 수 / 전체 수 (백분율))
- **Non-Root Volume Encryption**: 데이터 볼륨 암호화 현황 (암호화된 수 / 전체 수 (백분율))

#### 상세 정보
- **Instance Name**: EC2 인스턴스의 Name 태그 값
- **Instance ID**: EC2 인스턴스 ID
- **Unencrypted Volumes**: 해당 인스턴스에 연결된 암호화되지 않은 볼륨 ID 목록

## 볼륨 분류 기준

### 루트 볼륨 (Root Volume)
- 디바이스명이 `/dev/sda` 또는 `/dev/xvda`로 끝나는 볼륨
- 일반적으로 OS가 설치된 주 스토리지

### 데이터 볼륨 (Non-Root Volume)
- 루트 볼륨이 아닌 모든 연결된 볼륨
- 추가 데이터 저장용 볼륨

### 연결되지 않은 볼륨 (Unattached Volume)
- 어떤 EC2 인스턴스에도 연결되지 않은 볼륨
- 스냅샷에서 생성되었거나 분리된 볼륨

## 보안 고려사항

### 암호화의 중요성
1. **데이터 보호**: 저장 데이터 암호화로 무단 접근 방지
2. **규정 준수**: GDPR, HIPAA 등 규정 요구사항 충족
3. **키 관리**: AWS KMS를 통한 암호화 키 관리

### 권장사항
- 모든 EBS 볼륨에 대해 암호화 활성화
- 기본 EBS 암호화 설정 활성화
- 정기적인 암호화 상태 모니터링

## 활용 사례

- **보안 감사**: 암호화되지 않은 볼륨 식별 및 조치
- **규정 준수**: 데이터 보호 규정 준수 현황 확인
- **비용 최적화**: 사용하지 않는 볼륨 식별
- **보안 정책**: 계정별 암호화 정책 수립 및 모니터링

## 주요 특징

1. **다중 계정 지원**: 여러 AWS 계정을 한 번에 분석
2. **상세 분류**: 루트/데이터 볼륨 분리 통계
3. **실행 가능한 정보**: 암호화가 필요한 구체적인 인스턴스 정보 제공
4. **효율적인 조회**: 배치 API 호출로 성능 최적화

## 에러 처리

- 잘못된 프로필명이나 권한 부족 시 boto3에서 예외 발생
- 네트워크 연결 문제 시 AWS API 호출 실패
- 태그가 없는 인스턴스의 경우 'N/A'로 표시

## 개선 방향

- CSV/JSON 형태의 결과 출력 기능
- 특정 리전만 조회하는 옵션
- 암호화되지 않은 볼륨 자동 암호화 기능
- 이메일 알림 기능
