#Script for deploying prerequisites for 'template0.yaml' as well as running CF stack commands for ci/cd pipeline configuration.
import io
import boto3
import json
from zipfile import ZipFile, ZIP_DEFLATED
from botocore.exceptions import ClientError

cfclient = boto3.client('cloudformation')
s3client = boto3.client('s3')
iamclient = boto3.client('iam')
ssmclient = boto3.client('ssm')

def Command():
    action = input('create/update: ')
    projectid = input('enter unique tag created for project identification: ').strip()
    repository_provider = input('Codecommit repository or existing GitHub?.. aws/github: ').strip()
    repository_name_path = input('enter <githubaccount/repositoryname> if github or <nameforcodecommitrepository> if aws: ').strip()
    source_branch = input('Choose branch to act as pipeline source.. dev/main: ').strip()
    if repository_name_path == 'aws':
        github_connection_arn = 'null'
    else:
        github_connection_arn = input('paste GitHub Connection ARN here: ')
    command_data = {}
    command_data['action'] = action
    command_data['projectid'] = projectid
    command_data['repository_provider'] = repository_provider
    command_data['repository_name_path'] = repository_name_path
    command_data['github_connection_arn'] = github_connection_arn
    command_data['source_branch'] = source_branch    
    command_data['resources_bucket_name'] = 'deploymentresources-' + command_data['source_branch'] + command_data['projectid']
    return command_data

#runs list with expected bucket name to check if bucket exists
def Check_Bucket_Resource(command_data):
    try:
        response = s3client.list_objects(
            Bucket = command_data['resources_bucket_name'],
            )    
        print(command_data['resources_bucket_name']+ ' already found')
        return command_data['resources_bucket_name']

    except: 
        print('No resource bucket found, Creating new one..')
        return False
        
#S3 bucket to store resources for CloudFormation to reference
def Create_Bucket_Resource(command_data):   
    try:
        response = s3client.create_bucket(
            Bucket = command_data['resources_bucket_name']
        )
        print('Resources bucket launched: '+ command_data['resources_bucket_name'] )
    except ClientError as e:
        print("Client error: %s" % e)
        return command_data['resources_bucket_name']

#Upload ci/cd pipeline stages' function code for test and deploy
def Upload_Resources(command_data):
    file1 = io.BytesIO()
    with ZipFile(file1,'w',ZIP_DEFLATED) as obj:
        obj.write('app1/cicd-services/lambda-action1.py', arcname = 'lambda-action1.py')
    file1.seek(0)
    file2 = io.BytesIO()
    with ZipFile(file2,'w',ZIP_DEFLATED) as obj:
        obj.write('app1/cicd-services/lambda-action2.py', arcname = 'lambda-action2.py')
    file2.seek(0)
    objects = [
        {    
            'body': file1,
            'key': 'cicd/lambda-action1.zip'
        },
        {    
            'body': file2,
            'key': 'cicd/lambda-action2.zip'
        }    
    ]
    for x in objects:    
        try:
            response = s3client.put_object(
                Body = x['body'],                        
                Bucket = command_data['resources_bucket_name'],
                Key = x['key']
            )
            if 'ETag' in response: 
                data = response['ETag']
                print('stored object successfuly: '+ x['key'])
            else: 
                data = 0
        except ClientError as e:
            print("Client error: %s" % e)
    return data

#Conditionally updates or creates from ci/cd services 'template0' CF template
def CreateUpdate_Stack(command_data, upload_status):
    if upload_status != False:
        with open('app1/CICDLambda/cicd-template.yaml') as temp:
            template_body = temp.read()
        name = 'CICDstack-'+ command_data['source_branch']+ command_data['projectid']
        params = [ 
            {
                'ParameterKey': 'repositoryprovider',
                'ParameterValue': command_data['repository_provider']
            },
            {
                'ParameterKey': 'repositorynamepath',
                'ParameterValue': command_data['repository_name_path']
            },
            {   
                'ParameterKey': 'projectid',
                'ParameterValue': command_data['projectid']
            },
            {   
                'ParameterKey': 'githubconnectionarn',
                'ParameterValue': command_data['github_connection_arn'] 
            },
            {   
                'ParameterKey': 'sourcebranch',
                'ParameterValue': command_data['source_branch'] 
            }
        ]
    Validate_Template(template_body)
    stack_roles = Get_RoleARN()
    if command_data['action'] == 'update':
        try:
            response = cfclient.update_stack(
                StackName = name,
                TemplateBody = template_body,
                RoleARN = stack_roles,
                Parameters = params
            )
        except ClientError as e:
            print("Client error: %s" % e)
    elif command_data['action'] == 'create':
        try:
            response = cfclient.create_stack(
                StackName = name,
                Capabilities = ['CAPABILITY_NAMED_IAM'],
                TemplateBody = template_body,
                RoleARN = stack_roles,
                Parameters = params
            )
        except ClientError as e:
            print("Client error: %s" % e)
    else:
        print('invalid action')
    if 'StackId' in response:
        print('Resources deployed')
        stackresponse = response['StackId']
    else:
        print(response)
        print('stack creation failed')
        
        stackresponse = 0
    return stackresponse
        

#Prints out validation result of local template0.yaml
def Validate_Template(template_body):
    try:
        response = cfclient.validate_template(
            TemplateBody = template_body
            )
        validation_results = json.dumps(response)
        print('Template validation results: '+ validation_results)
    except ClientError as e:
        print("Client error: %s" % e)      


#Returns ARN of set IAM role name for CloudFormation template creation
def Get_RoleARN():
    try:
        response = iamclient.get_role(
            RoleName = 'MainCICDStackServiceRole'
        )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        if 'Arn' in response['Role']:
            data = response['Role']['Arn'].strip()
            print(data)
        else:
            data = 0
            print('Error getting role for stack creation')
        return data
    except ClientError as e:
        print("Client error: %s" % e)

        
def main():
    q = Command()
    if q['action'] == 'create':
        a = Check_Bucket_Resource(q)
        if a == False:
            b = Create_Bucket_Resource(q)
    c = Upload_Resources(q)
    CreateUpdate_Stack(q, c)

if __name__ == '__main__':
    main()