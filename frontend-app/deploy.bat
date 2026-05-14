@echo off

set PROJECT_ID=cisc5550-491418
set ZONE=us-east4-c
set API_VM=hw4-api
set DOCKER_IMAGE=nildatta123/todolist-frontend:v1
set CLUSTER=todolist-cluster

gcloud config set project %PROJECT_ID%

for /f "tokens=*" %%i in ('gcloud compute instances describe %API_VM% --zone=%ZONE% --format="get(networkInterfaces[0].accessConfigs[0].natIP)"') do set API_IP=%%i

echo Current API external IP is: %API_IP%

gcloud container clusters get-credentials %CLUSTER% --zone=%ZONE%

kubectl create deployment todolist-frontend --image=%DOCKER_IMAGE% --dry-run=client -o yaml > deployment.yaml
kubectl apply -f deployment.yaml

kubectl set env deployment/todolist-frontend TODO_API_IP=%API_IP%

kubectl expose deployment todolist-frontend --type=LoadBalancer --port=80 --target-port=5000 --dry-run=client -o yaml > service.yaml
kubectl apply -f service.yaml

kubectl rollout restart deployment/todolist-frontend

kubectl get services