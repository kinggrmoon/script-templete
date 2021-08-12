# AwsIamControlCmd(with bodo3)

## Feature
- 생성후 90일 지난 AccessKey 확인 및 중지, 삭제
- AccessKey 마지막 사용 내역 조회
- Group, Policy, User 조회

## 환경
- python3
- awscli
- bodo3

## 실행
```bash
$> python {파일명}.py
```
    accesskeyexpir_ck.py
    accesskeylastused_ck.py
    grouppolicyuser.py


### AWS Cli

awscli: list-users
```bash
aws iam list-users
```
Output:
```json
"Users": [
    {
        "UserName": "Adele",
        "Path": "/",
        "CreateDate": "2013-03-07T05:14:48Z",
        "UserId": "AKIAI44QH8DHBEXAMPLE",
        "Arn": "arn:aws:iam::123456789012:user/Adele"
    },
    {
        "UserName": "Bob",
        "Path": "/",
        "CreateDate": "2012-09-21T23:03:13Z",
        "UserId": "AKIAIOSFODNN7EXAMPLE",
        "Arn": "arn:aws:iam::123456789012:user/Bob"
    }
]
```

awscli: list-access-keys
```bash
aws iam list-access-keys --user-name Bob
```
Output:
```json
"AccessKeyMetadata": [
    {
        "UserName": "Bob",
        "Status": "Active",
        "CreateDate": "2013-06-04T18:17:34Z",
        "AccessKeyId": "AKIAIOSFODNN7EXAMPLE"
    },
    {
        "UserName": "Bob",
        "Status": "Inactive",
        "CreateDate": "2013-06-06T20:42:26Z",
        "AccessKeyId": "AKIAI44QH8DHBEXAMPLE"
    }
]
```

awscli: get-access-key-last-used
```bash
aws iam get-access-key-last-used --access-key-id ABCDEXAMPLE
```
Output:
```json
{
  "UserName":  "Bob",
  "AccessKeyLastUsed": {
      "Region": "us-east-1",
      "ServiceName": "iam",
      "LastUsedDate": "2015-06-16T22:45:00Z"
  }
}
```

awscli: aws get-group
```bash
aws iam get-group --group-name Admins
```
Output:
```json
{
    "Group": {
        "Path": "/",
        "CreateDate": "2015-06-16T19:41:48Z",
        "GroupId": "AIDGPMS9RO4H3FEXAMPLE",
        "Arn": "arn:aws:iam::123456789012:group/Admins",
        "GroupName": "Admins"
    },
        "Users": []
}
```

awscli: list-attached-group-policies
```bash
aws iam list-attached-group-policies --group-name Admins
```
Output:
```json
{
  "AttachedPolicies": [
    {
      "PolicyName": "AdministratorAccess",
      "PolicyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
    },
    {
      "PolicyName": "SecurityAudit",
      "PolicyArn": "arn:aws:iam::aws:policy/SecurityAudit"
    }
  ],
  "IsTruncated": false
}
```

awscli: get-account-summary
```bash
#To get information about IAM entity usage and IAM quotas in the current account
$> aws iam get-account-summary
```
Output:
```json
{
  "SummaryMap": {
      "UsersQuota": 5000,
      "GroupsQuota": 100,
      "InstanceProfiles": 6,
      "SigningCertificatesPerUserQuota": 2,
      "AccountAccessKeysPresent": 0,
      "RolesQuota": 250,
      "RolePolicySizeQuota": 10240,
      "AccountSigningCertificatesPresent": 0,
      "Users": 27,
      "ServerCertificatesQuota": 20,
      "ServerCertificates": 0,
      "AssumeRolePolicySizeQuota": 2048,
      "Groups": 7,
      "MFADevicesInUse": 1,
      "Roles": 3,
      "AccountMFAEnabled": 1,
      "MFADevices": 3,
      "GroupsPerUserQuota": 10,
      "GroupPolicySizeQuota": 5120,
      "InstanceProfilesQuota": 100,
      "AccessKeysPerUserQuota": 2,
      "Providers": 0,
      "UserPolicySizeQuota": 2048
  }
}
```

### Reference
- [AWS CLI Command Reference/iam](https://docs.aws.amazon.com/cli/latest/reference/iam/)
- [Boto3 Docs/Available/iam](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam.html#client)
- [python 에러와 예외](https://docs.python.org/ko/3/tutorial/errors.html)