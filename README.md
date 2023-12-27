# K8s-INFRA_APP
The only real purpose of this repo is for me to practice and understand different k8s services.

## Ingress
In the first interration of this repo, I have successfully created a Haproxy Ingress service, which will route to two different deployments, which in my case happen to be custom NGINX containers, that I quickly built locally. I intend to push there to docker hub, so some of the steps below can be omitted.

<p align="center">
  <img src="http://some_place.com/image.png](https://github.com/BhruguR/k8s-infra-app/assets/94770711/e5b3eae1-48da-485d-9d96-74c4162b1cda" />
</p>

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

## Installing Istio with Helm

If I don't use a package manager, I feel my stomach rumble (aka feel sick), so here are the steps to install Istio 1.20 with Helm, they slightly differ from the official steps, because the official steps didn't work for me, regardless here is the link https://istio.io/latest/docs/setup/install/helm/:

```
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
kubectl create namespace istio-system
helm install istio-base istio/base -n istio-system --set defaultRevision=default
helm install istiod istio/istiod --namespace istio-system
```

Checking if everything is running properly
```
helm ls -n istio-system
helm status istiod -n istio-system
 kubectl get deployments -n istio-system --output wide
```

## Credit / Reference:
1. Couldn't have gotten haproxy ingress down without this! 
   https://medium.com/@bm54cloud/deploy-an-haproxy-ingress-controller-on-a-k3d-kubernetes-cluster-3c88007eea36
