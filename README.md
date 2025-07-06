# AWS 스크립트 템플릿 저장소

이 저장소는 AWS 클라우드 리소스 관리를 위한 다양한 자동화 스크립트와 도구들을 포함하고 있습니다. Python과 Shell 스크립트를 통해 IAM, EC2, CloudWatch 등 주요 AWS 서비스를 효율적으로 관리할 수 있습니다.

## 📁 디렉토리 구조

```
script-templete/
├── python/                                    # Python 스크립트 모음
│   └── aws-python/
│       ├── awsIamControlCmd/                  # IAM 사용자 및 권한 관리
│       │   ├── accesskeyexpir_ck.py          # Access Key 만료 확인
│       │   ├── accesskeylastused_ck.py       # Access Key 마지막 사용일 확인
│       │   ├── grouppolicyuser.py            # 그룹 정책 사용자 관리
│       │   └── userlist-nsmform.py           # 사용자 목록 포맷팅
│       ├── ami/                               # AMI 관리 스크립트
│       │   ├── check_ami_to_ec2.py           # 단일 계정 AMI-EC2 매핑 확인
│       │   ├── check_ami_to_ec2_mult_account.py # 다중 계정 AMI-EC2 매핑 확인
│       │   └── filtered_ec2_list.py          # 필터링된 EC2 목록 조회
│       ├── ck-ssm/                           # AWS Systems Manager 관리
│       │   ├── ck-ssm.py                     # SSM Parameter Store 확인
│       │   └── ck-ssm-lambda_fuc.py          # Lambda용 SSM 확인 함수
│       ├── ebs/                              # EBS 볼륨 관리
│       │   └── check_ebs_encryption.py       # EBS 암호화 상태 확인
│       └── ec2/                              # EC2 인스턴스 관리
│           └── check_al2.py                  # Amazon Linux 2 확인
├── shell/                                     # Shell 스크립트 모음
│   └── aws-shell/
│       ├── authentication-authorization/      # 인증 및 권한 관리
│       │   ├── sso-login-and-get-accountlist.sh  # SSO 로그인 및 계정 조회
│       │   └── aws-sts-mfa-auth.sh           # MFA 인증 및 역할 전환
│       ├── aws-edit-tags/                    # AWS 리소스 태깅
│       │   ├── tagging-cloudwatchlog.sh      # CloudWatch Logs 태깅 관리
│       │   ├── cloudwatch_logs.list          # 태깅할 로그 그룹 목록
│       │   └── cloudwatch_logs_del.list      # 태그 삭제 대상 목록
│       └── aws-ec2/                          # EC2 관련 도구
│           ├── ck-used-sg-ec2-ecs-lambda.sh  # Security Group 사용 현황 확인
│           └── ec2-get-instance-profile-and-role.sh # EC2 IAM 정보 조회
├── security-check.sh                         # 보안 정보 검사 스크립트
├── SECURITY.md                              # 보안 가이드라인
└── README.md                                # 이 문서
```

## 🎯 주요 기능별 분류

### 🔐 보안 및 인증
- **IAM 관리**: 사용자, 그룹, 권한 관리 및 모니터링
- **MFA 인증**: Multi-Factor Authentication을 통한 보안 강화
- **SSO 로그인**: Single Sign-On을 통한 통합 인증
- **Access Key 관리**: 키 만료일 및 사용 현황 모니터링

### 💾 리소스 관리
- **EC2 인스턴스**: 인스턴스 상태 확인 및 OS 버전 체크
- **AMI 관리**: AMI 사용 현황 및 EC2 매핑 관계 확인
- **EBS 볼륨**: 암호화 상태 및 볼륨 정보 관리
- **CloudWatch Logs**: 로그 그룹 태깅 및 관리

### 📊 모니터링 및 운영
- **SSM Parameter Store**: 파라미터 확인 및 관리
- **태깅 관리**: 리소스 태그 일괄 추가/삭제
- **보안 검사**: 민감한 정보 탐지 및 보안 점검

## 🚀 빠른 시작

### 1. 사전 요구사항
```bash
# Python 환경 (Python 3.7+)
python3 --version

# AWS CLI 설치 및 설정
brew install awscli
aws configure

# 필요한 Python 패키지 설치
pip install boto3
```

### 2. 기본 사용 예시

**IAM 사용자 Access Key 만료 확인**
```bash
cd python/aws-python/awsIamControlCmd/
python3 accesskeyexpir_ck.py
```

**SSO 로그인 및 계정 조회**
```bash
cd shell/aws-shell/authentication-authorization/
./sso-login-and-get-accountlist.sh
```

**CloudWatch Logs 태깅**
```bash
cd shell/aws-shell/aws-edit-tags/
./tagging-cloudwatchlog.sh list
```

### 3. 보안 검사 실행
```bash
# 커밋 전 보안 정보 검사
./security-check.sh
```

## 📖 상세 가이드

각 디렉토리에는 상세한 README.md 파일이 포함되어 있습니다:

- [`python/aws-python/awsIamControlCmd/README.md`](python/aws-python/awsIamControlCmd/README.md) - IAM 관리 스크립트 가이드
- [`python/aws-python/ami/README.md`](python/aws-python/ami/README.md) - AMI 관리 스크립트 가이드
- [`python/aws-python/ck-ssm/README.md`](python/aws-python/ck-ssm/README.md) - SSM 관리 스크립트 가이드
- [`shell/aws-shell/authentication-authorization/README.md`](shell/aws-shell/authentication-authorization/README.md) - 인증 스크립트 가이드
- [`shell/aws-shell/aws-edit-tags/README.md`](shell/aws-shell/aws-edit-tags/README.md) - 태깅 스크립트 가이드
- [`shell/aws-shell/aws-ec2/README.md`](shell/aws-shell/aws-ec2/README.md) - EC2 관리 스크립트 가이드

## 🔒 보안 주의사항

**중요**: 이 저장소는 퍼블릭 저장소입니다. 민감한 정보를 커밋하지 않도록 주의해주세요.

### 필수 확인 사항
- 📖 [보안 가이드라인](SECURITY.md) - 반드시 읽어주세요
- 🚫 실제 AWS 계정 ID, 자격 증명, 이메일 주소 등을 포함하지 마세요
- ✅ 모든 예시는 가상의 데이터를 사용합니다
- 🔍 커밋 전 `security-check.sh` 스크립트로 보안 검사 수행

### 자동 보안 검사
```bash
# 커밋 전 실행 권장
./security-check.sh
```

## 💡 사용 시나리오

### 🏢 기업 환경
- **일일 보안 점검**: IAM 사용자 및 Access Key 상태 모니터링
- **리소스 관리**: EC2, EBS 등 클라우드 리소스 현황 파악
- **비용 최적화**: 태깅을 통한 리소스 분류 및 비용 추적

### 👨‍💻 개발팀
- **환경 관리**: 개발/스테이징/프로덕션 환경별 리소스 관리
- **자동화**: 반복적인 AWS 관리 작업 자동화
- **보안 강화**: MFA 및 역할 기반 접근 제어

### 🔧 운영팀
- **모니터링**: 시스템 상태 및 보안 취약점 모니터링
- **컴플라이언스**: 보안 정책 준수 확인
- **사고 대응**: 빠른 문제 파악 및 대응

## 🤝 기여하기

### 기여 절차
1. 이 저장소를 Fork 합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/새기능`)
3. 변경사항을 커밋합니다 (`git commit -am '새기능 추가'`)
4. 브랜치에 Push 합니다 (`git push origin feature/새기능`)
5. Pull Request를 생성합니다

### 기여 가이드라인
- 코드 기여 전에 [보안 가이드라인](SECURITY.md)을 확인하세요
- 민감한 정보가 포함되지 않았는지 검토하세요
- 새로운 스크립트에는 적절한 주석과 README를 추가하세요
- `security-check.sh` 스크립트로 보안 검사를 수행하세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자유롭게 사용, 수정, 배포할 수 있습니다.

## 📞 지원

문제가 발생하거나 개선 제안이 있으시면 GitHub Issues를 통해 알려주세요.
