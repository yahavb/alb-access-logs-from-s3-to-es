import json
import urllib
import boto3
import requests
from requests_aws4auth import AWS4Auth

region = 'us-west-2' 
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-skydance-telemety-yhosalcu76tkkwbo52ukkvlwdm.us-west-2.es.amazonaws.com' # the Amazon ES domain, including https://
index = 'alb-index'
type = 'lambda-type'
url = host + '/' + index + '/' + type

headers = { "Content-Type": "application/json" }

s3 = boto3.client('s3')


def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        obj = s3.get_object(Bucket=bucket, Key=key)
        lines = obj['Body'].read().decode('UTF-8')
        lines = lines.splitlines()

        for rawline in lines:
            line=rawline.split(' ')
            timestamp=line[0]
            domain=line[1]
            src_client=line[2]
            dest_server=line[3]
            attr_1=line[4]
            attr_2=line[5]
            attr_3=line[6]
            document = { "timestamp": timestamp, "domain": domain, "src_client": src_client, "dest_server": dest_server, "attr_1":attr_1,"attr_2":attr_2,"attr_3":attr_3 }
            print(document)
            r = requests.post(url, auth=awsauth, json=document, headers=headers)
    except Exception as e:
        print(e)
    return {
        'statusCode': 200,
        'body': json.dumps('printing access log to es!')
    }

