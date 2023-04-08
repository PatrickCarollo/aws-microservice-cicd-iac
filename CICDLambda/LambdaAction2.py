#Deploys revision to Prod Lambda Alias
import boto3
import json
import os
from botocore.exceptions import ClientError
codedeployclient = boto3.client('codedeploy')
lambdaclient = boto3.client('lambda')
pipelineclient = boto3.client('codepipeline')


def lambda_handler(event, context):
    global job_id
    job_id = event['CodePipeline.job']['id'].strip()
    env_variables = os.environ
    a = Describe_Version(env_variables)
    if a != False:
        Create_Deployment(env_variables,a)
    
    
def Describe_Version(app_data):
    try:
        response1 = lambdaclient.list_versions_by_function(
            FunctionName = app_data['AppName']
        )
        response2 = lambdaclient.get_function(
            FunctionName = app_data['AppName'],
            Qualifier = app_data['livealias']
        )
        dev_version = response1['Versions'][-1]
        print(dev_version)
        print(response2)
        version_dict = {}
        version_dict['dev'] = dev_version['Version']
        version_dict['prod'] = response2['Configuration']['Version']
        
        return version_dict
    except ClientError as e:
        print('Client error: %s' % e)
        msg = 'Failed at Describe_Version of main function..'
        Job_Fail(msg)
        return False
        

def Create_Deployment(app_data, app_version):
    try:
        revision_object = {
            "version": 0.0,
            "Resources": [
                {
                    "Lambdafunction": {
                        "Type": "AWS::Lambda::Function",
                            "Properties": {
                                "Name": app_data['AppName'],
                                "Alias": app_data['livealias'],
                                "CurrentVersion": app_version['prod'],
                                "TargetVersion": app_version['dev']
                            }
                    }
                }
            ]
        }
        json_revision_object = json.dumps(revision_object) 
        print(json_revision_object)
        response = codedeployclient.create_deployment(
            applicationName = app_data['codedeployapp'],
            deploymentGroupName = app_data['codedeploygroup'],
            revision = {
                'revisionType': 'String',
                'string': {
                    'content': json_revision_object
                }
            }
        )
        msg = 'Created deployment on deployment group for main app Lambda'
        print(msg)
        Job_Success(msg)   
    except ClientError as e:
        print('Client error: %s' % e)
        msg = 'Failed at Create_Deployment for version swapping..'
        print(msg)
        Job_Fail(msg)
    

def Job_Success(details):
    response = pipelineclient.put_job_success_result(
        executionDetails = {'summary': details},
        jobId = job_id,
    )


def Job_Fail(details):
    response = pipelineclient.put_job_failure_result(
        failureDetails = {
            'type': 'JobFailed',
            'message': details
        },
        jobId = job_id
    )    
    
    
    