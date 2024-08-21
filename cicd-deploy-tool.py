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
    command_data['resources_bucket_name'] = 'deploymentresources-' + command_data['source_branch'] + command_data['projectid']
    command_data['build_image_digest'] = build_image_digest
    return command_data



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
            data = False
            print('Error getting role for stack creation')
        return data
    except ClientError as e:
        print("Client error: %s" % e)

        
        
def main():
    q = Command()
    z = Get_RoleARN()
    if z != False:
        CreateUpdate_Stack(q,z)

if __name__ == '__main__':
    main()