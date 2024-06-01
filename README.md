# K8s-INFRA-APP
The only real purpose of this repo is for me to practice and understand different k8s services.

## Ingress
In the first interration of this repo, I have successfully created a Haproxy Ingress service, which will route to two different deployments, which in my case happen to be custom NGINX containers, that I quickly built locally. I intend to push there to docker hub, so some of the steps below can be omitted.

## Services

This is more of a note to myself. Due to some weird reason minikube doesn't like nodePort services or a loadbalancer service. Only thing that works is a clusterIP service upon which we do a port-forward on the port we defiend on it.

![haproxy-ingress](https://github.com/BhruguR/k8s-infra-app/assets/94770711/c49b6649-ec58-4119-aabb-0db52e1673d9)

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
helm repo add haproxytech https://haproxytech.github.io/helm-charts

helm repo update

helm upgrade -i haproxy haproxytech/kubernetes-ingress
```

### Deploying our YAML files
Now we are ready to deploy our YAML files, and we will deploy them in the following order:

```
kubectl apply -f haproxy-ingress/
```

### Last Step: Doing a port-forward

Due to the limitations of minikube, we need to do a portforward so we can access our ingress.

We run this command to do just that:

```
kubectl port-forward services/haproxy-kubernetes-ingress 8082:80
```

Run or simply access the service by copy pasting the URL below to access the service:
 ```
curl http://localhost:8082/route1
curl http://localhost:8082/route2
```

## Final Comments
Work is still in progress, and I am aware for the need to cut down on several of the manual steps to get this runing. However, it was important for me to release a bare-bones version, which I can utilize to build more stuff.

# ISTIO
Doesn't work yet, but work in-progress!

## Docker-Desktop
First things first, I ran into this head first, but apparently Istiod (Istio Discovery Deployment Pod) requires 2 GiB memory to run, however Docker-Desktop is capped at approx. 2 GiB memory! Which means our istiod will never be ready if you are running something else in Docker!

To solve this, you not only need to increase the memory resource for Docker-Desktop, but also for minikube, because guess what? Minikube's default memory is also capped at approx. 1 Gib.

### Solution
If you are using a proper linux distro then you can simply edit `MemoryMib` in this file `C:\Users\Personal\AppData\Roaming\Docker\settings.json`

If you are on windows, you will need to create a .wslconfig file in your home directory, which should be at `C:\Users\.wslconfig`, add this to the file:
```
[wsl2]
memory=4GB 
```
I set it to 4GB for now, but feel free to set a higher number.

Of course, you need to restart Linux Distro, and for good measure, if you are on windows, restart your whole system (this is what ultimately caused the changes to take effect for me).

We are not done yet, run this command to permanently start minikube with approx. 3GB memory or more, but not more than what you defined above:
```
minikube config set memory 3000
```

Run: `cp /mnt/c/Users/{USER_ACCOUNT}/.kube/config ~/.kube` and change the formatting of `dir` to linux style. This will allow you to use kubectl in wsl. 

## Installing Calico

Networking in minikube is limited. I discovered that the CNI that comes with minikube is not enough, hence the need for Calico. Luckily, Calico comes packaged with minikube, we simply run:

```
minikube start --network-plugin=cni --cni=calico
```

## Installing Istio with Helm

If I don't use a package manager, I feel my stomach rumble (aka feel sick), so here are the steps to install Istio 1.20 with Helm, they slightly differ from the official steps, because the official steps didn't work for me, regardless here is the link https://istio.io/latest/docs/setup/install/helm/:

```
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
kubectl create namespace istio-system
helm install istio-base istio/base -n istio-system --set defaultRevision=default
helm install istiod istio/istiod --namespace istio-system
kubectl create namespace istio-ingress
helm install istio-ingressgateway istio/gateway -n istio-ingress
```

Checking if everything is running properly
```
helm ls -n istio-system
helm status istiod -n istio-system
 kubectl get deployments -n istio-system --output wide
```
# Prometheus

<<<<<<< HEAD
I quickly realized, I would be unable to set-up Istio without the help of prometheus and kiali, and this is because I need a way to verify that my istio set-up is indeed working in the expected way or not. Therefore, we first need to configure prometheus, and then connect kiali to prometheus. This as I found out was not trivial to do so and required considerable amount of reconfiguration.

## Installing prometheus
Using the values.yaml file for prometheus called prometheus.yaml, install prometheus using the following commands:

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/prometheus --values /istio/prometheus.yaml
```

## Accessing Prometheus
We need to do a port-forward to access prometheus locally.

```
export POD_NAME=$(kubectl get pods --namespace istio-system -l "app.kubernetes.io/name=prometheus,app.kubernetes.io/instance=prometheus" -o jsonpath="{.items[0].metadata.name}")
kubectl --namespace istio-system port-forward $POD_NAME 9090
kubectl port-forward seneca-v1-5c468cbd5-24mm9 8000
```

The values.yaml for prometheus.yaml need to have the following job:
```
    scrape_configs:
      - job_name: prometheus
        static_configs:
          - targets: ['localhost:9090']
      - job_name: "seneca"
        kubernetes_sd_configs:
          - role: pod
            selectors:
              - role: "pod"
                label: "app.kubernetes.io/name=seneca"
      - job_name: 'service'
        static_configs:
        - targets: ['svc-seneca.app.svc.cluster.local']
```

The second job makes prometheus to look for pods with the label given above. We dance back with prometheus by adding the following annotations in our pods:

```
annotations:
   prometheus.io/scrape: "true"
   prometheus.io/path: /metrics
   prometheus.io/port: "80"
```
This will dynamically target the pods. 

Lastly, for the last job we give the full DNS name of our service so that prometheus can locate it, and this hooks-up our entire app with prometheus:
```
svc-seneca.app.svc.cluster.local
```

This finishes our prometheus set-up.

### Future ToDO:
Hook-up prometheus-operator or the helm chart known as kube-prometheus-stack: 
![prometheus-operator](https://artifacthub.io/packages/helm/prometheus-community/kube-prometheus-stack)

This enables us to hook-up pods and services to a monitor dynamically. 


## Reconfiguring our applicaion with Django

Previously our applaication was as simple as it gets, it was a simple html page loaded onto an nginx server, however I quickly realized that this was not enough. This is because prometheus needs a `metrics` endpoint, paritcularly, Kiali requires prometheus to have a `metrics` endpoint to map our application. This was simply not possible with a simple html page. I turned to python, found Django, and decided to serve our application in Django. 

Note: I am using the webserver option provided by django to run the web-application it created, but by no means that is supposed to be used in production.

### ToDO
Hook-up Django with a ngninx server. The reason I haven't done this yet is because my purpose is to get Istio Ingress Gateway down first and then refine later. 

I simply made the server serve an HTML page and hooked-up a metrics enpoint which delightfully comes packaged with django-prometheus library. 

One key thing to note is the dockerfile config has to have:
```
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
```
The last part of the command is super important, it will enable k8s to discover your pod and link it up to other pods.

## Credit / Reference:
1. Couldn't have gotten haproxy ingress down without this! 
   https://medium.com/@bm54cloud/deploy-an-haproxy-ingress-controller-on-a-k3d-kubernetes-cluster-3c88007eea36
