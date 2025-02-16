# **IP-Tool**  

## **Overview**  
The `ip-tool` script is designed to report configured IP networks inside a container and collect outputs from all containers in the cluster. It also includes a **collision check feature** to detect overlapping IP networks across the cluster.  

## **Features**  
- **Report IP networks** from the container where the script is deployed.  
- **Collect outputs** from all containers in the cluster and concatenate them.  
- **Collision Check**: Detect overlapping IP networks using the `--check-collision <file_path>` flag.  
- **Dockerized Deployment**: Runs inside a container and stops after execution.  

---

## **Installation & Usage**  

### **1. Build the Docker Image**  
```sh
docker build -t ip-tool .
```

### **2. Run the Container**  
To report the IP networks from a single container:  
```sh
docker run --rm ip-tool
```

### **3. Run with Collision Check**  
To analyze collected IP networks for collisions, use:  
```sh
docker run --rm ip-tool --check-collision /path/to/ip_list.txt
```
- `/path/to/ip_list.txt` should contain a list of IP networks from all containers.  

---

## **Kubernetes Deployment**
To deploy `ip-tool` on Kubernetes:  

```sh
kubectl apply -f ip-tool-deployment.yaml
```