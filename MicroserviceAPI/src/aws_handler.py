import boto3
import json
import os
import base64
s3client = boto3.client('s3')


def lambda_handler(event, context):
    print(event)
    p = Parse_Data(event)
    if p != False:
        x = Put_Object(p)
        if x != False:
            a = Update_Table(p, x)    
            if a != False:
                response_data = { 
                    's3 path to image': x, 
                    'id': p['upc'],
                    'DatabaseUpdated': a
                }
            else: response_data = 'Failed to update DB table'
        else: response_data - 'Failed to upload image data'
    else: response_data = 'Failed to parse request'
    #Creating response format 
    main_response_object = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response_data)
    }
    return main_response_object
    

def Parse_Data(event):
    #Accessing this Lambda's environment variables
    try:
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
        return request_data
    except:
        return False
    

def Put_Object(request_data):
    key = 'Images/' + request_data['name']+ '.txt'
    response = s3client.put_object(
        Body = request_data['body_data'],
        Bucket = request_data['bkt_name'],
        Key = key
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        
        data = request_data['bkt_name'] + '/' + key
    else:
        data = False
    return data


def Update_Table(request_data, metadata_key):
    dbclient = boto3.client('dynamodb')
    response = dbclient.put_item(
        TableName = request_data['table_name'],
        Item = {
            'name': {'S': request_data['name']},
            'id': {'S': request_data['upc']},
            'user': {'S': request_data['user']},
            'TransactionData': {'S': metadata_key},
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
#        'user': 'patrickcs',
#        'upc': '1234682'
#    },
#    'body': 'imagebodyhere'
#}
#context = ''
#lambda_handler(event, context)