import json
import boto3
import urllib
import gzip
import subprocess

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        print(bucket)
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        print(key)
        obj = s3_client.get_object(Bucket=bucket, Key=key)
        print(obj)
        s3_client.download_file(bucket, key, '/tmp/file.gz')
        subprocess.call(["/bin/ls", "/tmp"])
        key_unzip = gzip.open('/tmp/file.gz','rb')
        subprocess.call(["/bin/ls", "/tmp"])
        lines=key_unzip.read().decode('UTF-8')
        print(lines)
    except Exception as e:
        print(e)   
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
