from __future__ import print_function
from pprint import pprint
import boto3
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
import requests
import urllib
import json
import datetime

s3 = boto3.client('s3')

print('Loading function')

def connectES(esEndPoint):
    print ('Connecting to the ES Endpoint {0}'.format(esEndPoint))
    try:
        esClient = Elasticsearch(
            hosts=[{'host': esEndPoint, 'port': 443}],
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection)
        print(esClient)
        return esClient
    except Exception as E:
        print("Unable to connect to {0}".format(esEndPoint))
        print(E)
        exit(3)


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    esClient = connectES("vpc-my-photos-wx25o25eygixyqmbq3zat2ebei.us-west-2.es.amazonaws.com")

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    esClient.delete_by_query(index='photos',
                            body={"query": {"match": {'objectKey': key}}})
    
    
