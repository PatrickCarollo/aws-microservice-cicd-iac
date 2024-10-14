#!/usr/bin/python3
#Lambda pipeline action for sending test request directly to Temp version
import boto3
import time
import json
import os
from botocore.exceptions import ClientError
lambdaclient = boto3.client('lambda')
pipelineclient = boto3.client('codepipeline')
s3client = boto3.client('s3')
#print('EXECUTING SCRIPT: test-request.py')


#Isolated handler for clarity
def handler():
    env_variables = os.environ
    b = Get_Version(env_variables)
    a = Construct_Request_Body(b,env_variables)
    d = Check_State(env_variables,b)
    c = Invoke_Temp_Version(a,b,env_variables)
    if c != False:
        result = b
        print(b)
    else:
        result = 'FAIL'
    return result


#Request body for test request directly to the Lambda
def Construct_Request_Body(temp_version,env_variables): 

    req_parameters = {
        'body': "mocktest",
        'queryStringParameters': 'test'
    }
    json_test_request = json.dumps(req_parameters)
    print('request about to be sent through to temp lambda  '+ ' version: '+ json_test_request)
    return json_test_request
    

#Test invocation to most recent revision
def Invoke_Temp_Version(json_test_request,temp_version,env_variables):
    print('invoking...')
    try:
        response = lambdaclient.invoke(
            FunctionName = env_variables['LambdaName'],
            InvocationType = 'RequestResponse',
            Payload = json_test_request,
            Qualifier = temp_version
        )
        response_data = json.loads(response['Payload'].read().decode('utf-8'))
        if response['StatusCode'] == 200 and 'errorMessage' not in response_data:  
            print('Response from '+ env_variables['LambdaName']+ ': ')
            print(response_data)
            print('Successful response recieved from test invocation to Temp version: ')
            result = True
        else:
            print(response_data)
            print('Failure response recieved from test invocation to Temp lamdba version')
            result = False
    except ClientError as e:
        print("Client error: %s" % e)
        print('Failed at Invoke_Temp_Version function')
        result = False
    return result



#To persist the most recent function version number to ensure the correct tested version is promoted
def Get_Version(env_variables):
    try:
        response = lambdaclient.list_versions_by_function(
            FunctionName = env_variables['LambdaName']
        )
        temp_version = response['Versions'][-1]['Version']
        print('temp lamba version(most recent main version):')
        print(temp_version)
    except ClientError as e:
        print("Client error: %s" % e)
        temp_version = False
    return temp_version


#Wait for main Lambda State to return from Pending 
def Check_State(env_variables,b):
    print('Checking '+ env_variables['LambdaName']+ ' State after update_function_configuration()')
    while True:
        response = lambdaclient.get_function_configuration(
            FunctionName = env_variables['LambdaName'],
            Qualifier = b
        )
        print(response['State'])
        time.sleep(3)
        if response['State'] == 'Active':
            break


def main():
    handler()   
if __name__ == '__main__':
    main()      