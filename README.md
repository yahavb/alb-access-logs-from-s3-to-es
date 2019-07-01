# alb-access-logs-from-s3-to-es

## Setup
* [Create an elastic search cluster](https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-createupdatedomains.html#es-createdomains)
* Create a target servers
* Create a load balancer that uses the target servers
* Configure the load balancer to rotate access logs to S3
* Create a dummy clients that will generate traffic against the load balancer
* Deploy a lambda function that reads access logs from s3 and pushes it to es

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
