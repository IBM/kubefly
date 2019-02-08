docker build . -t rvennam/drone-app
docker push rvennam/drone-app
kubectl delete -f drone-app-deployment.yaml
kubectl apply -f drone-app-deployment.yaml