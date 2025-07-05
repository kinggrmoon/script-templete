import boto3
from datetime import datetime, timezone

## AWS Users
usernames = []
## AWS User expirkeys
acceskeylist = []

def acceskeylasteused(accesskeyid):
    #print(accesskeyid)
    result = iam.get_access_key_last_used(AccessKeyId = accesskeyid)
    user = result['UserName']
    try:
        lastuseddate = result['AccessKeyLastUsed']['LastUsedDate']
    except:
        lastuseddate = "N/A"
    usedservice = result['AccessKeyLastUsed']['ServiceName']

    print("User: " + user +" AccessKeyID: "+ accesskeyid +" LastUsedDate: "+ str(lastuseddate) +" Use Service: "+ usedservice) 

def run():
    users = iam.list_users()
    ## make IAM User list
    for user in users['Users']:
        tmp = str(user['UserName'])
        usernames.append(tmp)
    
    ## make expir accesskey list(and check acive accesskey)
    for username in usernames:
        accesskeys = iam.list_access_keys(UserName = username)
        for accesskey in accesskeys['AccessKeyMetadata']:
            status = accesskey['Status']
            ## Active and over expir date
            if status == "Active" :
                acceskeylist.append(accesskey['AccessKeyId'])

    for alist in acceskeylist:
        acceskeylasteused(alist)

## main
iam = boto3.client('iam')
run()