# K8s-INFRA_APP
The only real purpose of this repo is for me to practice and understand different k8s services.

## Ingress
In the first interration of this repo, I have successfully created a Haproxy Ingress service, which will route to two different deployments, which in my case happen to be custom NGINX containers, that I quickly built locally. I intend to push there to docker hub, so some of the steps below can be omitted.

### Building local images
In the future I'd like to package all of this in helm, but for now these are the steps:

0. Start minikube with `minikube start`.

1. CD into site-content/route-1 and build my docker image:

```
docker build -t webserver .

minikube image load webserver

minikube image ls
```

Confirm that webserver is listed in here, repeat this for site-content/route-2 and change the name to route-2 insteaad of webserver.

Now, minikube is aware about our two local images.

### Deploying Haproxy Ingress
Next, we will get Haproxy ingress via helm:

```
helm repo add haproxy-ingress https://haproxy-ingress.github.io/charts

helm repo update

helm install ingress haproxy-ingress/haproxy-ingress
```

### Deploying our YAML files
Now we are ready to deploy our YAML files, and we will deploy them in the following order:

```
kubectl apply -f deployment.yaml

kubectl apply -f frontend.yaml

kubectl apply -f ingress-class.yaml

kubectl appy -f haproxy.yaml
```

### Last Step: Doing a port-forward

Due to the limitations of minikube, we need to do a portforward so we can access our ingress.

We run this command to do just that:

```
kubectl port-forward services/haproxy-kubernetes-ingress 8082:80
```

Run or simply access the service by copy pasting the URL below to access the service:
 ```
curl curl http://localhost:8082/route2
curl http://localhost:8082/route2
```

## Final Comments
Work is still in progress, and I am aware for the need to cut down on several of the manual steps to get this runing. However, it was important for me to release a bare-bones version, which I can utilize to build more stuff. 


