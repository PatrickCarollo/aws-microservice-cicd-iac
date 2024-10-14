#!/usr/bin/python3
#Deploys revision to live Lambda Alias
import boto3
import json
import os
import sys
from botocore.exceptions import ClientError
codedeployclient = boto3.client('codedeploy')
lambdaclient = boto3.client('lambda')
pipelineclient = boto3.client('codepipeline')
print('EXECUTING SCRIPT: promote-to-live.py')


def handler():
    env_variables = os.environ
    test_result = sys.argv[1].strip()
    if  test_result != 'FAIL':
        Wipe_Old_Versions(env_variables)
        a = Describe_Version(env_variables, test_result)
        if a != False:
            Create_Deployment(env_variables,a)
    else:
        print('stopped')



def Wipe_Old_Versions(env_vars):
    print('checking for deprecated versions of main lambda to delete')
    try:

        response = lambdaclient.list_versions_by_function(
            FunctionName = env_vars['LambdaName'],
            MaxItems = 49
        )
        versions = []
        for x in response['Versions']:
            if x['Version'] != '$LATEST':
                versions.append(x['Version'])
            else:
                pass
        if len(versions) > 30:
            print('reached threshold.. rming old versions')
            versions = [int(x) for x in versions]
            versions.sort()
            # Remove the last two elements (the highest two numbers)
            versions = versions[:-5]
            #convert back to str
            versions = [str(x) for x in versions]
            for x in versions:
                response = lambdaclient.delete_function(
                    FunctionName = env_vars['LambdaName'],
                    Qualifier = x
                )
        else:
            print('threshold not reached')
            return
    except ClientError as e:
        print('Client error: %s' % e)



#Used to return current version alias is mapped to and accesses the temp tested version from env 
def Describe_Version(env_vars, test_result):
    try:
        response = lambdaclient.get_function(
            FunctionName = env_vars['LambdaName'],
            Qualifier = env_vars['livealias']
        )
        print(response)
        version_dict = {}
        version_dict['temp'] = test_result
        version_dict['live'] = response['Configuration']['Version']
        return version_dict
    except ClientError as e:
        print('Client error: %s' % e)
        msg = 'Failed at Describe_Version of main function..'
        print(msg)
        return False
        
        
#Creates CodeDeploy deployment ontop of Group using buildspec json to update alias' version
def Create_Deployment(env_vars, version_dict):
    try:
        revision_object = {
            "version": 0.0,
            "Resources": [
                {
                    "Lambdafunction": {
                        "Type": "AWS::Lambda::Function",
                            "Properties": {
                                "Name": env_vars['LambdaName'],
                                "Alias": env_vars['livealias'],
                                "CurrentVersion": version_dict['live'],
                                "TargetVersion": version_dict['temp']
                            }
                    }
                }
            ]
        }
        json_revision_object = json.dumps(revision_object) 
        print(json_revision_object)
        response = codedeployclient.create_deployment(
            applicationName = env_vars['codedeployapp'],
            deploymentGroupName = env_vars['codedeploygroup'],
            revision = {
                'revisionType': 'String',
                'string': {
                    'content': json_revision_object
                }
            }
        )
        msg = 'Created deployment on deployment group for main app Lambda'
        print(msg)
    except ClientError as e:
        print('Client error: %s' % e)
        msg = 'Failed at Create_Deployment for version swapping..'
        print(msg)


def main():
    handler()
if __name__ == '__main__':
    main()  