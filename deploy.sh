pip install requests -t .
pip install requests_aws4auth -t .

zip -r lambda.zip *
aws lambda update-function-code --function-name alb-access-logs-from-s3-to-es --zip-file fileb://lambda.zip
