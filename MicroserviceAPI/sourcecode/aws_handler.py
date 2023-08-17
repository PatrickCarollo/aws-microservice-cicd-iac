import boto3
import json
import os
import base64
s3client = boto3.client('s3')


def lambda_handler(event, context):
    #Accessing this Lambda's environment variables
    print(event)
    env_variables = os.environ
    bkt_name = env_variables['userbucket'].strip()
    table_name = env_variables['usertable'].strip()
    #Parsing request data
    user = event['queryStringParameters']['user'].strip()
    upc = event['queryStringParameters']['upc'].strip()
    object_name = event['queryStringParameters']['name'].strip()
    body_data = event['body']
    request_data = {}
    request_data['user'] = user
    request_data['upc'] = upc
    request_data['table_name'] = table_name
    request_data['bkt_name'] = bkt_name
    request_data['name'] = object_name
    request_data['body_data'] = body_data
    #Begin NFT creation flow:
    x = (request_data)
    if x != False:
        a = Update_Table(request_data, x)    
        
        
        
        
        
        
        response_data = { 
            'Url to image': json.dumps(x), 
            'id': request_data['upc'],
            'DatabaseUpdated': json.dumps(a)
        }
    else:
        response_data = 'Error.. put_object for image fail'
    #main response 
    main_response_object = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response_data)
    }
    return main_response_object
    


def Update_Table(request_data, metadata_key):
    dbclient = boto3.client('dynamodb')
    response = dbclient.put_item(
        TableName = request_data['table_name'],
        Item = {
            'name': {'S': request_data['name']},
            'id': {'S': request_data['upc']},
            'user': {'S': request_data['user']},
            'MetadataPath': {'S': metadata_key},
        }
    )
    print(response)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        data = True
    else:
        data = False
    return data
 


#event = {
#    'queryStringParameters': {
#        'name': 'testname',
#        'user': 'patrickjuhugns',
#        'upc': '1234682'
#    },
#    'body': 'imagebodyhere'
#}
#context = ''
#lambda_handler(event, context)