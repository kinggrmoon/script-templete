# AMI 및 EC2 인스턴스 관리 도구 모음

AWS EC2 인스턴스와 AMI를 다양한 관점에서 조회하고 분석하는 Python 스크립트 모음입니다.

## 구성 요소

### 1. 필터링된 EC2 조회 도구
- `filtered_ec2_list.py`

### 2. AMI 기반 인스턴스 검색 도구
- `check_ami_to_ec2.py` (단일 계정)
- `check_ami_to_ec2_mult_account.py` (다중 계정)

## 필요 조건

### Python 패키지
```bash
pip install boto3
```

### AWS 설정
- AWS CLI 설정 완료
- 각 계정별 AWS 프로필 구성
- 필요한 IAM 권한:
  - `ec2:DescribeInstances`
  - `ec2:DescribeImages`

## 1. 필터링된 EC2 조회 도구 (향상된 버전)

### filtered_ec2_list.py
특정 조건에 맞는 EC2 인스턴스를 필터링하여 CSV로 저장하는 향상된 도구입니다.

#### 🆕 주요 개선사항
1. **유연한 필터링**: 조건이 없으면 모든 EC2 인스턴스 조회
2. **인스턴스 상태 지정**: 실행 중, 중지된 인스턴스 등 상태별 조회
3. **향상된 OS 감지**: AMI 설명에서도 OS 정보 추출
4. **변수화된 설정**: 키워드와 태그 조건을 쉽게 변경 가능

#### 필터링 조건 설정
```python
# 키워드 필터 (None이면 모든 키워드)
KEYWORD_FILTER = "jdk11"  # 또는 None

# 태그 필터 (빈 리스트면 모든 태그)
TAG_FILTERS = [
    {"key": "team", "value": "devops"},
    {"key": "project", "value": "project01"},
    {"key": "environment", "value": "production"},
    {"key": "APM", "value": "true"}
]

# 인스턴스 상태 필터
INSTANCE_STATES = ["running", "stopped"]
```

#### 실행 방법
```bash
python filtered_ec2_list.py
```

#### 출력 컬럼 (업데이트됨)
| 컬럼 | 설명 |
|------|------|
| Account | AWS 계정 별칭 |
| Instance ID | EC2 인스턴스 ID |
| Instance Name | 인스턴스 Name 태그 |
| **State** | **인스턴스 상태 (신규 추가)** |
| OS | 운영체제 (향상된 감지) |
| AMI ID | 사용 중인 AMI ID |
| AMI Name | AMI 이름 |
| Instance Type | 인스턴스 타입 |

#### 🔍 향상된 OS 감지 기능
이제 다음과 같은 다양한 소스에서 OS 정보를 정확하게 추출합니다:

1. **AWS Platform 필드** (최우선)
2. **AMI 설명(Description)** 
3. **AMI 이름(Name)**
4. **PlatformDetails 필드**

##### 지원하는 OS 패턴
- **Amazon Linux**: `amazonlinux2023`, `amazonlinux2`, `amazonlinux`
- **Ubuntu**: `ubuntu-22.04`, `ubuntu20.04`, `ubuntu-jammy` 등
- **CentOS**: `centos-8`, `centos7` 등
- **RHEL**: `rhel-9`, `rhel8` 등
- **Windows**: `windows-2022`, `win2019` 등
- **기타**: Debian, SUSE, Alpine, FreeBSD 등

#### 사용 시나리오

##### 1. 모든 EC2 조회 (상태별)
```python
KEYWORD_FILTER = None
TAG_FILTERS = []
INSTANCE_STATES = ["running", "stopped"]
```

##### 2. 특정 키워드 검색
```python
KEYWORD_FILTER = "mongodb"
TAG_FILTERS = []
INSTANCE_STATES = ["running"]
```

##### 3. 태그 기반 필터링
```python
KEYWORD_FILTER = None
TAG_FILTERS = [
    {"key": "environment", "value": "production"},
    {"key": "team", "value": "devops"}
]
INSTANCE_STATES = ["running"]
```

##### 4. 복합 조건
```python
KEYWORD_FILTER = "web"
TAG_FILTERS = [{"key": "APM", "value": "true"}]
INSTANCE_STATES = ["running", "stopped"]
```

### mongodb_serviceng_ec2_exporter.py
동일한 필터링 로직이지만 콘솔 출력만 제공하는 경량 버전입니다.

#### 실행 방법
```bash
python mongodb_serviceng_ec2_exporter.py
```

## 2. AMI 기반 인스턴스 검색 도구

### check_ami_to_ec2.py (단일 계정)
특정 AMI ID를 사용하는 인스턴스를 단일 AWS 계정에서 검색합니다.

#### 실행 방법
```bash
python check_ami_to_ec2.py
```

#### 대화형 입력
- AWS Profile Name
- AMI ID
- Output CSV File Name (선택사항)

#### 출력 컬럼
- InstanceName
- AMI_ID

### check_ami_to_ec2_mult_account.py (다중 계정 기본)
여러 AWS 계정에서 특정 AMI ID를 사용하는 인스턴스를 검색합니다.

#### 실행 방법
```bash
python check_ami_to_ec2_mult_account.py
```

#### 대화형 입력
- AWS Profile Names (쉼표로 구분)
- AMI ID
- Output CSV File Name (선택사항)

#### 출력 컬럼
- Profile
- InstanceName
- AMI_ID

### check_ami_to_ec2_mult_account_v2.py (다중 계정 상세)
다중 계정 검색에 인스턴스 상태와 ID 정보를 추가한 향상된 버전입니다.

#### 실행 방법
```bash
python check_ami_to_ec2_mult_account_v2.py
```

#### 출력 컬럼
- Profile
- InstanceName
- InstanceID
- State (running, stopped, terminated 등)
- AMI_ID

## 🆕 인스턴스 상태 유형

다음 인스턴스 상태를 지정할 수 있습니다:

| 상태 | 설명 |
|------|------|
| `running` | 실행 중 |
| `stopped` | 중지됨 |
| `stopping` | 중지 중 |
| `starting` | 시작 중 |
| `pending` | 대기 중 |
| `shutting-down` | 종료 중 |
| `terminated` | 종료됨 |
| `terminating` | 종료 처리 중 |

## 사용 시나리오

### 시나리오 1: 전체 인프라 현황 파악
```bash
# 모든 상태의 EC2 인스턴스 조회
python filtered_ec2_list.py
# (KEYWORD_FILTER = None, TAG_FILTERS = [], INSTANCE_STATES = ["running", "stopped"])
```

### 시나리오 2: 특정 팀의 리소스 현황
```bash
# Service Engineering 팀 관련 인스턴스만 조회
python filtered_ec2_list.py
# (TAG_FILTERS = [{"key": "devteam", "value": "service engineering"}])
```

### 시나리오 3: 특정 서비스 인스턴스 추적
```bash
# MongoDB 관련 인스턴스 조회
python filtered_ec2_list.py
# (KEYWORD_FILTER = "mongo")
```

### 시나리오 4: 중지된 인스턴스 점검
```bash
# 중지된 인스턴스만 조회하여 비용 최적화 검토
python filtered_ec2_list.py
# (INSTANCE_STATES = ["stopped"])
```

### 시나리오 5: 특정 AMI 사용 현황 조회
```bash
# 단일 계정에서 AMI 사용 현황
python check_ami_to_ec2.py

# 여러 계정에서 AMI 사용 현황 (상세 정보)
python check_ami_to_ec2_mult_account_v2.py
```

## 활용 사례

### 인프라 관리
- **전체 현황 파악**: 모든 인스턴스의 상태와 OS 분포 확인
- **팀별 리소스 관리**: 특정 팀이 사용하는 인스턴스 현황
- **서비스별 분류**: MongoDB 등 특정 서비스 인스턴스 파악
- **AMI 사용 추적**: 특정 AMI를 사용하는 모든 인스턴스 추적

### 보안 및 컴플라이언스
- **취약한 AMI 추적**: 보안 패치가 필요한 AMI 사용 인스턴스 식별
- **OS 버전 관리**: 구버전 OS 사용 인스턴스 파악 및 업그레이드 계획
- **라이선스 관리**: 상용 소프트웨어 AMI 사용 현황 파악
- **규정 준수**: 특정 기준에 맞는 인스턴스만 운영 중인지 확인

### 비용 최적화
- **중지된 인스턴스 관리**: 불필요하게 중지된 인스턴스 정리
- **인스턴스 타입 분석**: 팀별 또는 용도별 인스턴스 타입 사용 패턴
- **리소스 통합**: 유사한 용도의 인스턴스 통합 가능성 검토
- **사용하지 않는 리소스**: 특정 조건의 인스턴스 상태 모니터링

## 도구별 비교 (업데이트됨)

| 기능 | filtered_ec2_list.py | check_ami_to_ec2.py | check_ami_to_ec2_mult_account_v2.py |
|------|---------------------|---------------------|-------------------------------------|
| 검색 방식 | 키워드/태그/상태 기반 | AMI ID 기반 | AMI ID 기반 |
| 계정 수 | 다중 (설정 가능) | 단일 | 다중 (동적 입력) |
| 상태 필터링 | ✅ **신규** | ❌ | ❌ |
| OS 감지 | ✅ **향상됨** | ❌ | ❌ |
| 유연한 필터링 | ✅ **신규** | ❌ | ❌ |
| 출력 정보 | 상세 (상태, OS 등) | 기본 (이름, AMI) | 상세 (상태, ID 포함) |
| CSV 저장 | ✅ | ✅ | ✅ |
| 대화형 입력 | ❌ | ✅ | ✅ |
| 사용 용도 | 포괄적 인프라 관리 | 일회성 AMI 추적 | AMI 마이그레이션 계획 |

## 확장 가능성

### 추가 기능
- VPC, 서브넷, 보안그룹 정보 추가
- 실시간 모니터링 및 알림 기능
- 웹 대시보드 연동
- 자동화된 정기 보고서 생성
- 인스턴스 비용 정보 통합

### 통합 도구
- 모든 기능을 포함하는 통합 CLI 도구
- 설정 파일 기반 일괄 처리
- API 서버로 확장하여 웹 서비스 제공
- Slack/Teams 알림 연동

## 문제 해결

### 일반적인 오류
1. **인증 오류**: AWS 프로필 설정 확인
2. **권한 부족**: IAM 권한 확인
3. **프로필 없음**: `~/.aws/config` 파일 확인
4. **리전 오류**: 올바른 리전 설정 확인
5. **OS 감지 실패**: AMI 이름/설명 패턴 확인

### 성능 최적화
- 대량의 인스턴스 조회 시 페이지네이션 고려
- AMI 정보 캐싱으로 API 호출 최소화
- 비동기 처리로 다중 계정 조회 성능 향상
- 인스턴스 상태별 필터링으로 불필요한 조회 제거

### 🆕 새로운 기능 활용 팁

#### 1. 정기적인 인프라 감사
```python
# 매주 모든 인스턴스 상태 점검
INSTANCE_STATES = ["running", "stopped", "stopping"]
```

#### 2. OS 업그레이드 계획
```python
# Amazon Linux 2 인스턴스만 조회하여 AL2023 마이그레이션 계획
KEYWORD_FILTER = None
# CSV에서 OS 컬럼으로 "Amazon Linux 2" 필터링
```

#### 3. 비용 최적화 검토
```python
# 중지된 인스턴스만 조회
INSTANCE_STATES = ["stopped"]
```

#### 4. 개발팀별 리소스 할당 현황
```python
# 팀별 태그로 리소스 사용량 파악
TAG_FILTERS = [{"key": "team", "value": "backend"}]
```
