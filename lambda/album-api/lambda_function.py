import boto3
import json
import datetime
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

print('Loading function')
client = boto3.client('lex-runtime')


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json'
        },
    }


def lambda_handler(event, context):
    '''Demonstrates a simple HTTP endpoint using API Gateway. You have full
    access to the request and response payload, including headers and
    status code.

    To scan a DynamoDB table, make a GET request with the TableName as a
    query string parameter. To put, update, or delete an item, make a POST,
    PUT, or DELETE request respectively, passing in the payload to the
    DynamoDB API as a JSON body.
    '''
    #print("Received event: " + json.dumps(event, indent=2))
    operation = 'GET'
    #operation = event['method']
    if operation == 'GET':
        query = event['queryParams']['qr']
        identityId = event['queryParams']['id']
        #query = 'I want dog'
        #identityId = 'a79ja'
        response = client.post_text(
            botName='pic_lex',
            botAlias='demo',
            userId= identityId,
            sessionAttributes={
            },
            requestAttributes={
            },
            inputText=query
        )
        text = []
        text.append(response['message'])
        if 'responseCard' in response:
            for imgurl in response['responseCard']['genericAttachments']:
                text.append(imgurl['imageUrl'])
            
        logger.debug('json_data>>>{}'.format(response))
        payload = {
            "messages": [
                {
                  "type": "response",
                  "unstructured": {
                    "id": identityId,
                    "text": text,
                    "timestamp": round(datetime.datetime.now().timestamp())
                  }
                }
            ]
        }
        return respond(None, payload)
    else:
        return respond(ValueError('Unsupported method "{}"'.format(operation)))
    

