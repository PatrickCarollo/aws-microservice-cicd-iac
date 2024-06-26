#Mock microservice flow
import boto3
import json
import os
s3client = boto3.client('s3')
print('start')
def lambda_handler(event, context):
    print(event)
    #Flow of mock request processing and testing
    if 'mocktest' not in event['body']:
        p = Parse_Data(event)
        if p != False:
            response_data = json.dumps(p)
        else:
            response_data = 'Failed to parse'
    else:
        response_data = 'Pipeline Action mock test invocation'
    #Creating response format 
    main_response_object = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': response_data
    }
    return main_response_object
    

def Parse_Data(event):
    try:
        #Accessing this Lambda's environment variables
        env_variables = os.environ
        bkt_name = env_variables['userbucket'].strip()
        table_name = env_variables['usertable'].strip()
        print(bkt_name)
        print(table_name)
        #Parsing request data
        request_data = {}
        request_data['incoming_body_data'] = event['body']
        request_data['incoming_querystring'] = event['queryStringParameters']
        return request_data
    except:
        return False
    