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
    projectid = input('Enter unique tag created for project identification: ').strip()
    repository_provider = input('Codecommit repository or existing GitHub?.. aws/github: ').strip()
    repository_name_path = input('Enter <githubaccount/repositoryname> if github or <nameforcodecommitrepository> if aws: ').strip()
    source_branch = input('Choose branch to act as pipeline source.. dev/main: ').strip()
    compute_type = input('Choose compute architecture of Lambda arm/x86: ')
    build_image_digest = input('Enter ECR build image digest: ')
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
    command_data['compute_type'] = compute_type
    command_data['build_image_digest'] = build_image_digest
    return command_data


#runs list with expected bucket name to check if bucket exists
def Check_Bucket_Resource(bkt_name):
    print('checking if an associated pipeline artifact bucket exists..')
    try:
        response = s3client.list_objects(
            Bucket = bkt_name,
            )    
        print(bkt_name+ ' already found')
        return True
    except: 
        print('No artifact bucket found, Creating new one..')
        return False

#S3 bucket to serve as artifact storage for respective pipeline
def Create_Bucket_Resource(command_data):   
    bkt_name = 'deploymentresources-' + command_data['source_branch'] + command_data['projectid']
    bkt_status = Check_Bucket_Resource(bkt_name)
    if bkt_status == False:
        try:
            response = s3client.create_bucket(
                Bucket = bkt_name
            )
            print('New associated pipeline artifact bucket launched: '+ bkt_name )
        except ClientError as e:
            print("Client error: %s" % e)
            return bkt_name
        
#Conditionally updates or creates from ci/cd services 'template0' CF template
def CreateUpdate_Stack(command_data, stack_roles):
    repo_name = command_data['repository_name_path'].split('/')[1]
    if stack_roles != False:
        with open(repo_name+'/cicd-services/cicd-template.yml') as temp:
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
            },
            {   
                'ParameterKey': 'computetype',
                'ParameterValue': command_data['compute_type'] 
            },
            {   
                'ParameterKey': 'buildimagedigest',
                'ParameterValue': command_data['build_image_digest'] 
            }           
        ]
    Validate_Template(template_body)
    if command_data['action'] == 'update':
        try:
            response = cfclient.update_stack(
                StackName = name,
                Capabilities = ['CAPABILITY_NAMED_IAM'],
                TemplateBody = template_body,
                RoleARN = stack_roles,
                Parameters = params
            )
            stackresponse = response['StackId']
            print('Updated stack')
        except ClientError as e:
            print("Client error: %s" % e)
            stackresponse = False
    elif command_data['action'] == 'create':
        try:
            response = cfclient.create_stack(
                StackName = name,
                Capabilities = ['CAPABILITY_NAMED_IAM'],
                TemplateBody = template_body,
                RoleARN = stack_roles,
                Parameters = params
            )
            stackresponse = response['StackId']
            print('Launched stack')
        except ClientError as e:
            print("Client error: %s" % e)
            stackresponse = False
    else:
        print('invalid action')
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

#Returns IAM Role ARN for CloudFormation to assume 
def Get_RoleARN():
    try:
        response = iamclient.get_role(
            RoleName = 'MainCICDStackServiceRole'
        )                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        if 'Arn' in response['Role']:
            data = response['Role']['Arn'].strip()
            print(data)
        else:
            data = False
            print('Error getting role for stack creation')
        return data
    except ClientError as e:
        print("Client error: %s" % e)

        
def main():
    q = Command()
    Create_Bucket_Resource(q)
    z = Get_RoleARN()
    if z != False:
        CreateUpdate_Stack(q,z)

if __name__ == '__main__':
    main()