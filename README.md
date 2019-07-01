# alb-access-logs-from-s3-to-es

## Setup
* Create an elastic search cluster
* Create a target servers
* Create a load balancer that uses the target servers
* Configure the load balancer to rotate access logs to S3
* Create a dummy clients that will generate traffic against the load balancer
* Deploy a lambda function that reads access logs from s3 and pushes it to es

## Dataflow
* 
