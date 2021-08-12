import boto3
from datetime import datetime, timezone

## AWS Users
usernames = []
## AWS User expirkeys
expirkeys = [] 
## AccessKey expir trem 
expir = 90

def run():
    ## make IAM User list
    users = iam.list_users()
    for user in users['Users']:
        tmp = str(user['UserName'])
        usernames.append(tmp)
    
    ## make expir accesskey list(and check acive accesskey)
    for username in usernames:
        ## except iam user
        if username == "backend-rc" or username == "jenkins-cdn" or username == "dev-monitoring-iam":
            pass
        else:
            accesskeys = iam.list_access_keys(UserName = username)
            for accesskey in accesskeys['AccessKeyMetadata']:
                status = accesskey['Status']
                ## (now - createdate)days
                activeday = (datetime.now(timezone.utc)-accesskey['CreateDate']).days
                ## Active and over expir date
                if status == "Active" and activeday > expir:
                    result = [username,activeday,accesskey['AccessKeyId']]
                    expirkeys.append(result)

    ## Expir List Report
    ## Expir AccessKey Inactive
    ## Expir AccessKey Delete
    for ekey in expirkeys:
        expirkeyuser = ekey[0:1][0]
        activeday = str(ekey[1:2][0])
        accesskeyid = ekey[2:3][0]
        print("[warning] Accesskey is too logging used","| User: ",expirkeyuser,"| AciveDay(",activeday,")","| AccessKeyId: ",accesskeyid)

        ## disable aws accesskey
        #output_update_key = iam.update_access_key(UserName=expirkeyuser,AccessKeyId=accesskeyid,Status='Inactive')
        ## delete aws accesskey
        #output_delete_key = iam.delete_access_key(AccessKeyId=accesskeyid,UserName=expirkeyuser)
        #print(output_update_key,output_delete_key)
 
    print("Expir Accesskey Count: " + str(len(expirkeys)))

## main
iam = boto3.client('iam')
run()