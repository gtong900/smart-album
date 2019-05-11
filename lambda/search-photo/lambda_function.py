import boto3
import json
import requests
from requests_aws4auth import AWS4Auth

region = 'us-west-2'  # For example, us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'vpc-my-photos-wx25o25eygixyqmbq3zat2ebei.us-west-2.es.amazonaws.com'  # For example, search-mydomain-id.us-west-1.es.amazonaws.com
index = 'photos'
url = 'https://' + host + '/' + index + '/_search'


def lambda_handler(event, context):
    # ==========================================
    labels = get_labels(event)
    # write elstic search code here with 'labels'(list)

    print(labels)

    # ==========================================
    # Put the user query into the query DSL for more accurate search results.
    # Note that certain fields are boosted (^).
    photos = set()
    for label in labels:
        query = {
        "size": 20,
        "query": {
            "match": {
                "labels": label}
            }
        }
        # ES 6.x requires an explicit Content-Type header
        headers = {"Content-Type": "application/json"}

        # Make the signed HTTP request
        r = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query))

        # Add the search results to the response
        data = [doc for doc in json.loads(r.text)['hits']['hits']]
        for pic in data:
            print(pic['_source']['objectKey'])
            photos.add(pic['_source']['objectKey'])
    # =================================================
    # after ES, there should be a list include image file names[]
    # imageList = ["London-Intro-4X3.jpg", "nyc-street.jpg"]
    imageList = list(photos)
    s3 = boto3.client('s3')
    bucket = "my-album-photos"
    return sort_image(imageList, s3, bucket)


def get_labels(intent_request):
    labels = []
    slots = ["labelOne", "labelTwo", "labelThree"]
    for slot in slots:
        label = get_slots(intent_request)[slot]
        if label:
            labels.append(label)
    return labels


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def sort_image(imageList, s3, bucket):
    imageUrls = []
    if len(imageList)>=10:
        imageList = imageList[:9]
    for key in imageList:
        params = {'Bucket': bucket, 'Key': key}
        url = s3.generate_presigned_url('get_object', params)
        imageUrls.append({"imageUrl": url})
    response = {
        "dialogAction":
            {
                "fulfillmentState": "Fulfilled",
                "type": "Close", "message":
                {
                    "contentType": "PlainText",
                    "content": ""
                }
            }
    }
    if not imageUrls:
        response["dialogAction"]["message"]["content"] = "There's no such picture"
    else:
        response["dialogAction"]["message"]["content"] = "Here are our search result"
        response["dialogAction"]["responseCard"] = {
            "version": "2",
            "contentType": "application/vnd.amazonaws.card.generic",
            "genericAttachments": imageUrls,
        }
    return response
