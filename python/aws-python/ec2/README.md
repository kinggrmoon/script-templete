# EC2 OS Distribution Checker

AWS 계정별로 실행 중인 EC2 인스턴스의 운영체제(OS) 분포를 조회하고 분석하는 Python 스크립트입니다.

## 기능

- 여러 AWS 계정의 EC2 인스턴스 OS 분포 조회
- Amazon Linux 2, Amazon Linux 2023, Windows, 기타 OS 분류
- Amazon Linux 2 사용률 계산
- 테이블 형태의 결과 출력

## 필요 조건

### Python 패키지
```bash
pip install boto3
```

### AWS 설정
- AWS CLI 설정 완료
- 각 계정별 AWS 프로필 구성
- EC2 읽기 권한 (ec2:DescribeInstances, ec2:DescribeImages)

## 사용법

### 1. 기본 실행
```bash
python check_al2.py
```

### 2. 스크립트 수정
`aws_profiles` 딕셔너리에서 조회하고 싶은 계정의 주석을 해제하거나 새로운 프로필을 추가:

```python
aws_profiles = {
    "your_profile_name": "your_alias",
    # 추가 프로필...
}
```

### 3. 리전 변경
기본 리전은 `ap-northeast-2`이며, 필요시 변경 가능:

```python
region = "us-east-1"  # 원하는 리전으로 변경
```

## 출력 형태

```
Alias | Total EC2 | Amazon Linux 2 | Amazon Linux 2023 | Windows | Other | AL2 used %
--------------------------------------------------------------------------------
alias01 | 5 | 3 | 1 | 0 | 1 | 60.00%
```

### 컬럼 설명
- **Alias**: AWS 계정 별칭
- **Total EC2**: 실행 중인 총 EC2 인스턴스 수
- **Amazon Linux 2**: Amazon Linux 2 인스턴스 수
- **Amazon Linux 2023**: Amazon Linux 2023 인스턴스 수  
- **Windows**: Windows 인스턴스 수
- **Other**: 기타 OS 인스턴스 수
- **AL2 used %**: Amazon Linux 2 사용률 (백분율)

## OS 분류 기준

### Amazon Linux 2
- AMI 이름에 `amzn2-ami` 또는 `amazonlinux2` 포함
- AMI 설명에 `amazon linux 2` 포함

### Amazon Linux 2023
- AMI 이름에 `al2023-ami` 포함
- AMI 설명에 `amazon linux 2023` 또는 `amazonlinux2023` 포함

### Windows
- AMI 이름 또는 설명에 `windows` 포함

### Other
- 위 조건에 해당하지 않는 모든 OS

## 주요 특징

1. **효율적인 API 호출**: 고유한 AMI ID들만 수집하여 배치로 조회
2. **다중 계정 지원**: 여러 AWS 계정을 한 번에 조회
3. **유연한 설정**: 프로필과 리전을 쉽게 변경 가능
4. **명확한 결과**: 테이블 형태로 보기 쉬운 결과 제공

## 에러 처리

- 잘못된 프로필명이나 권한 부족 시 boto3에서 예외 발생
- 존재하지 않는 리전 지정 시 오류 발생
- 네트워크 연결 문제 시 AWS API 호출 실패

## 활용 사례

- Amazon Linux 2 EOL 대비 현황 파악
- 계정별 OS 표준화 현황 모니터링
- 비용 최적화를 위한 인스턴스 분포 분석
- 보안 패치 및 업데이트 계획 수립
