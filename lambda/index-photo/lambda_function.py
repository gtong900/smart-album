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

indexDoc = {
    "dataRecord" : {
        "properties" : {
          "objectKey" : {
            "type" : "string"
          },
          "bucket" : {
            "type" : "string"
          },
          "createdTimestamp" : {
            "type" : "date",
            "format" : "dateOptionalTime"
          },
          "labels" : {
            "type" : "string"
          }
        }
      },
    "settings" : {
        "number_of_shards": 1,
        "number_of_replicas": 0
      }
    }

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



def createIndex(esClient):
    try:
        res = esClient.indices.exists('photos')
        print("create:",res)
        if res is False:
            esClient.indices.create('photos', body=indexDoc)
        return 1
    except Exception as e:
            print("Unable to Create Index {0}".format("photos"))
            print(e)
            exit(4)

def indexDocElement(esClient,key,bucket,labels):
    try:
        indexObjectKey = key
        indexBucket = bucket
        indexLabels = labels
        # indexcreatedDate = response['LastModified']
        indexcreatedDate = datetime.datetime.now() 
        # indexmetadata = json.dumps(response['Metadata'])
        retval = esClient.index(index='photos',  body={
            'objectKey': indexObjectKey,
            'bucket': indexBucket,
            'createdTimestamp': indexcreatedDate,
            'labels': indexLabels
        })
    except Exception as E:
        print("Document not indexed")
        print("Error: ",E)
        exit(5) 
      


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    esClient = connectES("vpc-my-photos-wx25o25eygixyqmbq3zat2ebei.us-west-2.es.amazonaws.com")
    createIndex(esClient)

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    # labels=["Dog","Grass","Plant","Mammal","Canine","Pet","Animal","Terrier","Ball","Sphere","Puppy","Lawn"]
    # indexDocElement(esClient,key,bucket,labels)
    rekClient = boto3.client('rekognition')
    response = rekClient.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': key}})

    print('Detected labels for ' + key)
    labels = []
    for label in response['Labels']:
        print(label['Name'] + ' : ' + str(label['Confidence']))
        labels.append(label['Name'])
    indexDocElement(esClient,key,bucket,labels)
    
