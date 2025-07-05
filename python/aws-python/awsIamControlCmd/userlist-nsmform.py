import boto3
from datetime import datetime, timezone

## AWS Users
usernames = []
tags = []
usergroups = []

def getUserTags(userName):
    usernm=""
    team=""
    company=""
    tags = iam.list_user_tags(UserName = userName)
    for tag in tags['Tags']:
        if tag['Key'] == "Name":
            usernm = tag['Value']
            #print(tag['Key']+": " + tag['Value'])

        if tag['Key'] == "Team":
            team = tag['Value']
            #print(tag['Key']+": " + tag['Value'])

        if tag['Key'] == "Company":
            company = tag['Value']
            #print(tag['Key']+": " + tag['Value'])

    return (usernm, team, company)

def getUserGroup(userName):
    result = []
    usergroups = iam.list_groups_for_user(UserName = userName)
    for usergroup in usergroups['Groups']:
        #print(usergroup['GroupName'])
        result.append(usergroup['GroupName'])
    return result

def run():
    ## make IAM User list
    users = iam.list_users()
    for user in users['Users']:
        usernames.append(user['UserName'])
    
    ## make expir accesskey list(and check acive accesskey)
    for username in usernames:
        tmp = iam.get_user(UserName = username)
        usernm, team, company = getUserTags(username)
        #group = getUserGroup(username)
        if company == "":
            print("IAMUser: " +username)
            print("Company: " +company+ " | Team: " +team+ " | Name: " +usernm+ " | IAMUser: " +username+ " | CreateDate:" + str(tmp['User']['CreateDate']))
            print(getUserGroup(username))
            print("===================")

def selectrun(iamuser):
    ## make IAM User list
    users = iam.list_users()
    for user in users['Users']:
        usernames.append(user['UserName'])
    
    ## make expir accesskey list(and check acive accesskey)
    for username in usernames:
        tmp = iam.get_user(UserName = username)
        usernm, team, company = getUserTags(username)
        #group = getUserGroup(username)
        if username == iamuser:
            print("IAMUser: " +username)
            print("Company: " +company+ " | Team: " +team+ " | Name: " +usernm+ " | IAMUser: " +username+ " | CreateDate:" + str(tmp['User']['CreateDate']))
            print(getUserGroup(username))
            break    

## main
iam = boto3.client('iam')
run()
#selectrun("grmoon")