# Minikube Command Reference

## Cluster Management

### Start Cluster

```bash
# Basic start
minikube start

# With specific Kubernetes version
minikube start --kubernetes-version=v1.28.0

# With custom resources
minikube start --memory=4096 --cpus=2 --disk-size=20g

# With specific driver
minikube start --driver=docker

# With specific profile
minikube start -p dev-cluster
```

### Stop Cluster

```bash
# Stop default cluster
minikube stop

# Stop specific profile
minikube stop -p dev-cluster

# Stop all clusters
minikube stop --all
```

### Delete Cluster

```bash
# Delete default cluster
minikube delete

# Delete specific profile
minikube delete -p dev-cluster

# Delete all clusters and purge configuration
minikube delete --all --purge
```

### Pause/Unpause Cluster

```bash
# Pause cluster (saves resources)
minikube pause

# Resume paused cluster
minikube unpause
```

### Cluster Status

```bash
# Check cluster status
minikube status

# Check specific profile
minikube status -p dev-cluster

# Get cluster info
kubectl cluster-info
```

## Profile Management

### Create Profile

```bash
# Create and start new profile
minikube start -p staging-cluster

# Create with specific configuration
minikube start -p test-cluster --memory=2048 --cpus=1
```

### List Profiles

```bash
minikube profile list
```

### Switch Profile

```bash
minikube profile dev-cluster
```

### Delete Profile

```bash
minikube delete -p dev-cluster
```

## Configuration

### Set Configuration

```bash
# Set default memory
minikube config set memory 4096

# Set default CPUs
minikube config set cpus 2

# Set default driver
minikube config set driver docker

# Set default disk size
minikube config set disk-size 20g

# Set Kubernetes version
minikube config set kubernetes-version v1.28.0
```

### View Configuration

```bash
# View all configuration
minikube config view

# Get specific value
minikube config get memory
```

### Unset Configuration

```bash
minikube config unset memory
```

## Addons Management

### List Addons

```bash
minikube addons list
```

### Enable Addon

```bash
# Enable dashboard
minikube addons enable dashboard

# Enable ingress
minikube addons enable ingress

# Enable metrics-server
minikube addons enable metrics-server

# Enable registry
minikube addons enable registry

# Enable storage provisioner
minikube addons enable storage-provisioner
```

### Disable Addon

```bash
minikube addons disable dashboard
```

### Common Addons

- **dashboard** - Kubernetes Dashboard
- **ingress** - Nginx Ingress Controller
- **ingress-dns** - DNS for Ingress
- **metrics-server** - Resource metrics
- **registry** - Container registry
- **storage-provisioner** - Dynamic storage
- **default-storageclass** - Default storage class
- **efk** - Elasticsearch, Fluentd, Kibana logging
- **helm-tiller** - Helm package manager
- **metallb** - Load balancer
- **registry-creds** - Registry credentials

## Service Management

### Expose Service

```bash
# Get service URL
minikube service <service-name>

# Get service URL for specific namespace
minikube service <service-name> -n <namespace>

# Just print URL
minikube service <service-name> --url

# List all services
minikube service list
```

### Tunnel (LoadBalancer Support)

```bash
# Create network tunnel for LoadBalancer services
minikube tunnel

# Run in background
minikube tunnel &
```

## Docker Integration

### Use Minikube Docker Daemon

```bash
# Linux/macOS
eval $(minikube docker-env)

# Windows PowerShell
minikube docker-env | Invoke-Expression

# Unset
eval $(minikube docker-env -u)
```

### Build Images in Minikube

```bash
# Set Docker environment
eval $(minikube docker-env)

# Build image
docker build -t myapp:latest .

# Deploy without pull
kubectl run myapp --image=myapp:latest --image-pull-policy=Never
```

### Load Local Image

```bash
minikube image load myimage:tag

# Or cache image
minikube cache add myimage:tag
```

## SSH and Shell Access

### SSH into Node

```bash
minikube ssh

# SSH to specific profile
minikube ssh -p dev-cluster

# Execute command
minikube ssh "docker ps"
```

### Run Command in Node

```bash
minikube ssh -- docker ps
minikube ssh -- sudo systemctl status kubelet
```

## Dashboard

### Open Dashboard

```bash
# Open in browser
minikube dashboard

# Get URL only
minikube dashboard --url
```

## IP and Network

### Get Cluster IP

```bash
minikube ip
```

### Get Service URL

```bash
minikube service <service-name> --url
```

### Port Forward

```bash
kubectl port-forward service/<service-name> 8080:80
```

## Logs and Debugging

### View Logs

```bash
# View cluster logs
minikube logs

# Follow logs
minikube logs -f

# Last N lines
minikube logs --length=100
```

### Get Events

```bash
kubectl get events --all-namespaces
```

### Describe Node

```bash
kubectl describe node minikube
```

## File Transfer

### Copy to Cluster

```bash
# Copy file to node
minikube cp <local-path> <node-path>

# Example
minikube cp ./config.yaml /tmp/config.yaml
```

### Mount Host Directory

```bash
# Mount local directory
minikube mount <local-path>:<remote-path>

# Example
minikube mount ~/projects:/mnt/projects
```

## Version and Update

### Check Version

```bash
minikube version
```

### Update Check

```bash
minikube update-check
```

### Kubernetes Version

```bash
# List available versions
minikube kubectl -- version

# Start with specific version
minikube start --kubernetes-version=v1.28.0
```

## Resource Management

### View Resource Usage

```bash
# Node resources
kubectl top node

# Pod resources
kubectl top pod

# All pods with resources
kubectl top pod --all-namespaces
```

### Scale Resources

```bash
# Stop and reconfigure
minikube stop
minikube config set memory 8192
minikube config set cpus 4
minikube start
```

## Cache Management

### Add Image to Cache

```bash
minikube cache add <image>
```

### List Cached Images

```bash
minikube cache list
```

### Delete Cached Image

```bash
minikube cache delete <image>
```

### Reload Cached Images

```bash
minikube cache reload
```

## kubectl Commands via Minikube

```bash
# Use minikube's kubectl
minikube kubectl -- get pods

# Get nodes
minikube kubectl -- get nodes

# Create deployment
minikube kubectl -- create deployment nginx --image=nginx

# Expose service
minikube kubectl -- expose deployment nginx --port=80 --type=NodePort
```

## Troubleshooting Commands

### Verify Installation

```bash
minikube version
kubectl version --client
docker --version
```

### Check Cluster Health

```bash
minikube status
kubectl get nodes
kubectl get pods --all-namespaces
```

### Reset Cluster

```bash
minikube delete
minikube start
```

### Clean Docker Images

```bash
eval $(minikube docker-env)
docker system prune -a
```

### View System Info

```bash
minikube kubectl -- cluster-info dump
```

## Advanced Commands

### Custom Container Runtime

```bash
# Use containerd
minikube start --container-runtime=containerd

# Use CRI-O
minikube start --container-runtime=cri-o
```

### Enable Feature Gates

```bash
minikube start --feature-gates=EphemeralContainers=true
```

### Custom API Server Args

```bash
minikube start --extra-config=apiserver.enable-admission-plugins=PodSecurityPolicy
```

### Multi-Node Cluster

```bash
# Create 3-node cluster
minikube start --nodes=3

# Add node to existing cluster
minikube node add
```

### Snapshot Management

```bash
# Take snapshot
minikube pause
# Backup ~/.minikube

# Restore snapshot
# Restore ~/.minikube
minikube unpause
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `minikube start` | Start cluster |
| `minikube stop` | Stop cluster |
| `minikube delete` | Delete cluster |
| `minikube status` | Check status |
| `minikube dashboard` | Open dashboard |
| `minikube ip` | Get cluster IP |
| `minikube ssh` | SSH into node |
| `minikube logs` | View logs |
| `minikube service <name>` | Access service |
| `minikube addons list` | List addons |
| `minikube profile list` | List profiles |
| `minikube tunnel` | Create LoadBalancer tunnel |
| `eval $(minikube docker-env)` | Use Minikube Docker |
