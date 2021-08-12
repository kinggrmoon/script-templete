import boto3
from datetime import datetime, timezone

## AWS Groups
groups = []

## AWS Users
users = []

## Group Attached Policies
policies = []

## Group Inline Policies
inlinepolicies = []

def groupdetail(groupname):
    result = iam.get_group(GroupName = groupname)
    GroupName = result['Group']['GroupName']
    GroupId = result['Group']['GroupId']
    Path = result['Group']['Path']
    Arn = result['Group']['Arn']
    users = result['Users']
    print("GroupName: " +GroupName+" | GroupId: " +GroupId+ " | ARN: " +Arn)

    ## Attached Policies
    policies = iam.list_attached_group_policies(GroupName = groupname)
    for policy in policies['AttachedPolicies']:
        print("PolicyName: " +policy['PolicyName']+ " | ARN: " + policy['PolicyArn'])
    
    ## Inline Policies
    inlinepolicies = iam.list_group_policies(GroupName = groupname)
    for inlinepolicy in inlinepolicies['PolicyNames']:
        print("InlinePolicyName: " +inlinepolicy) 

    ## Users
    for user in users:
        print("User: " +user['UserName']+ " | UserID: " +user['UserId']+ " | UserCreateDate: " + str(user['CreateDate']))

def run():
    groups = iam.list_groups()
    ## make iam groupname list
    for group in groups['Groups']:
        groupname = group['GroupName']
        groupdetail(groupname)
        print("===============")

## main
iam = boto3.client('iam')
run()