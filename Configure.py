#Script for deploying resources for deploying prerequisites for 'template0.yaml' as well as create_stack for ci/cd pipeline configuration.
import io
import random
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
    projectid = input('enter unique numerical id created for project identification: ').strip()
    repository_provider = input('Codecommit repository or existing GitHub?.. aws/github: ').strip()
    repository_name_path = input('enter <githubaccount/repositoryname> if github or <nameforcodecommitrepository> if aws: ').strip()
    if repository_name_path == 'aws':
        github_connection_arn = 'null'
    else:
        github_connection_arn = input('paste GitHub Connection ARN/ null: ')
    command_data = {}
    command_data['action'] = action
    command_data['projectid'] = projectid
    command_data['repository_provider'] = repository_provider
    command_data['repository_name_path'] = repository_name_path
    command_data['github_connection_arn'] = github_connection_arn
    return command_data


#S3 bucket to store resources for CloudFormation to reference
#such as lambda.zip, appspec.yaml and other deployment resources
def Create_Bucket_Resource(command_data):   
    try:
        response = s3client.create_bucket(
            Bucket = 'deploymentresources-' + command_data['projectid']
        )
        print('Resources bucket launched: '+ 'deploymentresources-' + command_data['projectid'] )
    except ClientError as e:
        print("Client error: %s" % e)
  


#Upload function code. Store appspec, buildspec
def Upload_Resources(command_data):
    main_repository_code = [
        'aws-cicd-microservice-iac/CICDLambda/buildspec.yaml',
        'aws-cicd-microservice-iac/MicroserviceAPI/sourcecode/requirements.txt',
        'aws-cicd-microservice-iac/MicroserviceAPI/sourcecode/app.py'
    ]
    
    file0 = io.BytesIO()
    with ZipFile(file0,"w", ZIP_DEFLATED) as zip_obj:
        for x in main_repository_code:
            indexed = x.rfind('/')
            if indexed != -1:
                key = x[indexed+1:]
            zip_obj.write(x, arcname = key)
    file0.seek(0)
    
    file1 = io.BytesIO()
    with ZipFile(file1,'w',ZIP_DEFLATED) as obj:
        obj.write('aws-cicd-microservice-iac/CICDLambda/LambdaAction1.py', arcname = 'LambdaAction1.py')
    file1.seek(0)
    
    file2 = io.BytesIO()
    with ZipFile(file2,'w',ZIP_DEFLATED) as obj:
        obj.write('aws-cicd-microservice-iac/CICDLambda/LambdaAction2.py', arcname = 'LambdaAction2.py')
    file2.seek(0)
    objects = [
        {
            'body': file0,
            'key': 'cicd/StartingAppCode.zip'
        },
        {    
            'body': file1,
            'key': 'cicd/LambdaAction1.zip'
        },
        {    
            'body': file2,
            'key': 'cicd/LambdaAction2.zip'
        }    
    
    ]
    for x in objects:    
        try:
            response = s3client.put_object(
                Body = x['body'],                        
                Bucket = 'deploymentresources-' + command_data['projectid'],
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


#Conditionally updates or creates the ci/cd 'template0' CF template
def CreateUpdate_Stack(command_data, upload_status):
    if upload_status != 0:
        with open('aws-cicd-microservice-iac/CICDLambda/template0.yaml') as temp:
            template_body = temp.read()
        name = 'CICDstack-' + command_data['projectid']
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
                'ParameterValue':command_data['github_connection_arn'] 
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


#Returns ARN of specific IAM role name for CloudFormation template creation
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


#Stores Project iD for build and deploy services to reference
def Put_Parameter(command_data):
    response = ssmclient.put_parameter(
        Overwrite = True,
        Name = 'LambdaMSprojectid'+ command_data['projectid'],
        Value = command_data['projectid'],
        Type  = 'String'
    )
    if 'Version' in response:
        print('project id updated in Parameter Store: ' + command_data['projectid'])
    else:
        print('Project id failed to upload to Parameter Store..')


#Sample image upload for sample lambda app code to use. This can be removed if repurposing.
def Sample_Image_Upload(command_data):
    response = s3client.put_object(
        Body = json.dumps('ImageDataSampleStandIn'),                        
        Bucket = 'application-user-data-' + command_data['projectid'],
        Key = 'test/testimage.png'
    )

        
def main():
    q = Command()
    if q['action'] == 'create':
        Create_Bucket_Resource(q)
    b = Upload_Resources(q)
    CreateUpdate_Stack(q,b)
    Put_Parameter(q)
    Sample_Image_Upload(q)
if __name__ == '__main__':
    main()