# alb-access-logs-from-s3-to-es

## Setup
* [Create an elastic search cluster](https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-createupdatedomains.html#es-createdomains)
* Create a target servers
* Create a load balancer that uses the target servers
* Configure the load balancer to rotate access logs to S3
* Deploy a lambda function that reads access logs from s3 and pushes it to es
* Create a dummy clients that will generate traffic against the load balancer
* Wait 60 minutes until access logs are written to S3 and search for those lines using Kibana console


## Create a target servers
I used a simple nginx container that I deployed on my EKS cluster:
```bash
kubectl apply -f https://k8s.io/examples/application/deployment.yaml
```
## Create a load balancer
Again, I used k8s service 
```bash
kubectl expose deployment nginx-deployment --type=LoadBalancer --port=80 --target-port=80
```
## Load balancer log rotation into S3
Discover your elb via:
```bash
kubectl get svc nginx-deployment
```
and correlate it with the `DNSName` of:
```bash
aws elb describe-load-balancers
```
Set the `Access logs` attributes using the AWS console to write access log every 60 minutes. 

## Configure and deploy the lambda function
Execute the script [deploy.sh](https://github.com/yahavb/alb-access-logs-from-s3-to-es/blob/master/deploy.sh). It will install the required packages and deploy the lambda function. 

### The lambda function
We start with discovering the s3 and the file that was written to s3
```python
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
        obj = s3.get_object(Bucket=bucket, Key=key)
```
note that the `event` object carries all the required info. 
Next is to load the lines into memory before parsing:

```python
        lines = obj['Body'].read().decode('UTF-8')
        lines = lines.splitlines()
```

Finally, parse the lines and post it to ES

```python
        #Serialize the file as JSON
        for rawline in lines:
            line=rawline.split(' ')
            timestamp=line[0]
            domain=line[1]
            src_client=line[2]
            dest_server=line[3]
            attr_1=line[4]
            attr_2=line[5]
            attr_3=line[6]
            document = { "timestamp": timestamp, "domain": domain, 
                        "src_client": src_client, "dest_server": dest_server, 
                        "attr_1":attr_1,"attr_2":attr_2,"attr_3":attr_3 
                        }
            print(document)
            #Write the line to es
            r = requests.post(url, auth=awsauth, json=document, headers=headers)
   ```


### Creating function trigger 
We want the code to execute whenever a log file arrives in an S3 bucket:

1. Choose S3.

2. Choose your bucket.

3. For Event type, choose PUT.

4. For Prefix, type AWSLogs/.

5. For Filter pattern, type .log.

6. Select Enable trigger.

7. Choose Add.

### Define the lambda IAM role
The lambda function requires read access to the S3 bucket that uses for the elb access logs. Also, the lambda function requires write access to the es cluster. 

The following is the inline policy grants the lambda function permissions to read the access log file from s3:

```yaml
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::nginx-deploymnet/AWSLogs/356566070122/*"
        },
```

The following inline policy grants the lambda function permissions to write lines of access logs to es and to cloudwatch logs
```yaml
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "es:ESHttpPost",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:us-west-2:356566070122:log-group:/aws/lambda/alb-access-logs-from-s3-to-es:*",
                "arn:aws:es:us-west-2:356566070122:domain/gnu-alb-access-logs"
            ]
        }
```
Finally, in Elasticsearch Service dashboard under `Modify access policy` grant `ESHttpPost` rights for `arn:aws:iam::356566070122:role/service-role/alb-access-logs-from-s3-to-es-role-1qfsn4ux` in the es domain `arn:aws:es:us-west-2:356566070122:domain/gnu-alb-access-logs/*`:
```yaml
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::356566070122:role/service-role/alb-access-logs-from-s3-to-es-role-1qfsn4ux"
      },
      "Action": "es:ESHttpPost",
      "Resource": "arn:aws:es:us-west-2:356566070122:domain/gnu-alb-access-logs/*"
    }
  ]
}
```

## Create a dummy clients
I used simple traffic generator:
```bash
#! /bin/bash
  
while true
do
  curl a2ff4c8a49aec11e98a72025dc17acf6-143281082.us-west-2.elb.amazonaws.com
  sleep 3
done
```
 
