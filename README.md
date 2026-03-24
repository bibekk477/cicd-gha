namespace for argo cd installation
kubectl create namespace argocd
Namespace for flask app deployment by argocd
kubectl create namespace flask-app
argocd is also running inside k8s cluster
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
argocd is also running inside k8s cluster
kubectl edit svc argocd-server -n argocd
minikube service argocd-server -n argocd

 for argo cd initial password 
 kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}"| base64 -d 

 for troubleshooting if argocd is not managing the deployment