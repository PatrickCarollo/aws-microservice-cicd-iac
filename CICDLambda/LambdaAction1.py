#Lambda pipeline action for sending test request directly to dev version
import boto3
import json
import os
import base64
from botocore.exceptions import ClientError
lambdaclient = boto3.client('lambda')
pipelineclient = boto3.client('codepipeline')
s3client = boto3.client('s3')


def lambda_handler(event, context):
    global job_id
    job_id = event['CodePipeline.job']['id'].strip()
    global env_variables
    env_variables = os.environ
    Construct_Request_Body(env_variables['projectid'])


def Construct_Request_Body(projectid): 
    try:
        response = s3client.get_object(
            Bucket = 'application-user-data-' + projectid,
            Key = 'test/testimage.png'
        )
        print(response)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200: 
            print('Getobject for test image successful')
        else:
            print('Getobject for sample/test image failed')
        req_parameters = {
            'body': response['Body'].read().decode('utf-8'),
            'queryStringParameters': {
                'name': 'Sample_Name/123456',
                'id': '010101',
                'user': 'test_userIdentity0'
            }    
        }
        json_test_request = json.dumps(req_parameters)
        print('request here: '+ json_test_request)
        Invoke_Dev_Version(json_test_request, projectid)
    except:
        msg = 'Failed at Construct_Request_Body function'
        Job_Fail(msg)


#Test invocation
def Invoke_Dev_Version(json_test_request, projectid):
    try:
        response = lambdaclient.invoke(
            FunctionName = env_variables['AppName'],
            InvocationType = 'RequestResponse',
            Payload = json_test_request,
        )
        response_data = json.loads(response['Payload'].read().decode('utf-8'))
        if response['StatusCode'] == 200 and 'errorMessage' not in response:   
            print(json.dumps(response_data))
            msg = 'Successful response recieved from test invocation to dev stage app version: '
            print(msg)
            Job_Success(msg)
        else:
            print(response_data)
            msg = 'Failure response recieved from test invokation to development lamdba version'
            print(msg)
            Job_Fail(msg)
    except:
        msg = 'Failed at Invoke_Dev_Version function'
        Job_Fail(msg)


#Send results back to pipeline
def Job_Success(details):
    response = pipelineclient.put_job_success_result(
        executionDetails = 
        {'summary': details},
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