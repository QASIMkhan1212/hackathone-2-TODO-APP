---
name: minikube
description: "Local Kubernetes development with Minikube. Use when working with Minikube for: (1) Setting up local Kubernetes clusters, (2) Deploying and testing applications locally, (3) Learning Kubernetes concepts, (4) Developing Kubernetes-native applications, (5) Testing Helm charts and manifests, (6) Troubleshooting cluster issues, (7) Managing multiple cluster profiles, (8) Configuring ingress and storage, or any other Minikube or local Kubernetes development tasks"
---

# Minikube - Local Kubernetes Development

## Overview

Minikube is a lightweight tool that runs a single-node Kubernetes cluster on your local machine. This skill provides automated setup, deployment workflows, and best practices for local Kubernetes development.

## Quick Start

### Setup New Cluster

Use the automated setup script:

```bash
python scripts/setup_minikube.py
```

Options:
- `--profile <name>` - Cluster profile name
- `--memory <MB>` - Memory allocation (default: 4096)
- `--cpus <N>` - CPU allocation (default: 2)
- `--driver <driver>` - Driver (docker, virtualbox, kvm2, etc.)
- `--kubernetes-version <version>` - Kubernetes version
- `--addons <addon1> <addon2>` - Addons to enable

Example:
```bash
python scripts/setup_minikube.py \
  --profile dev \
  --memory 8192 \
  --cpus 4 \
  --driver docker \
  --addons dashboard metrics-server ingress
```

### Manual Setup

```bash
# Start cluster
minikube start

# Enable common addons
minikube addons enable dashboard
minikube addons enable metrics-server

# Open dashboard
minikube dashboard
```

## Workflows

### 1. Installing Minikube

**Linux (x86-64):**
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**macOS:**
```bash
brew install minikube
```

**Windows (Chocolatey):**
```powershell
choco install minikube
```

For detailed installation instructions for all platforms and drivers, see [installation.md](references/installation.md).

### 2. Deploying Applications

**Using Deployment Script:**

```bash
python scripts/deploy_app.py myapp \
  --image nginx:latest \
  --port 80 \
  --replicas 3 \
  --service-type NodePort
```

Options:
- `--image` - Container image
- `--port` - Service port
- `--target-port` - Container port
- `--replicas` - Number of replicas
- `--namespace` - Kubernetes namespace
- `--service-type` - ClusterIP, NodePort, or LoadBalancer
- `--ingress` - Create ingress resource
- `--host` - Ingress hostname
- `--env KEY=VALUE` - Environment variables
- `--wait` - Wait for deployment to be ready
- `--open` - Open service in browser

**Using kubectl:**

```bash
# Create deployment
kubectl create deployment myapp --image=nginx:latest

# Expose as service
kubectl expose deployment myapp --type=NodePort --port=80

# Access service
minikube service myapp
```

**Using YAML Templates:**

The skill includes ready-to-use templates in `assets/deployment-templates/`:

- `simple-deployment.yaml` - Basic deployment + service
- `with-configmap.yaml` - With ConfigMap
- `with-ingress.yaml` - With Ingress
- `with-persistent-storage.yaml` - With PVC

Deploy template:
```bash
kubectl apply -f assets/deployment-templates/simple-deployment.yaml
```

### 3. Managing Clusters

**Using Management Script:**

```bash
# List all profiles
python scripts/manage_cluster.py list

# Start cluster
python scripts/manage_cluster.py start --profile dev

# Check status
python scripts/manage_cluster.py status --profile dev

# Stop cluster
python scripts/manage_cluster.py stop --profile dev

# Delete cluster
python scripts/manage_cluster.py delete --profile dev

# Manage addons
python scripts/manage_cluster.py addons list --profile dev
python scripts/manage_cluster.py addons enable dashboard --profile dev

# View services
python scripts/manage_cluster.py services --profile dev

# Open dashboard
python scripts/manage_cluster.py dashboard --profile dev

# Get cluster IP
python scripts/manage_cluster.py ip --profile dev

# SSH into node
python scripts/manage_cluster.py ssh --profile dev

# View logs
python scripts/manage_cluster.py logs --profile dev
```

**Using Minikube Commands:**

```bash
# Start/stop
minikube start
minikube stop

# Status
minikube status

# Delete
minikube delete

# Multiple profiles
minikube start -p dev-cluster
minikube start -p test-cluster
minikube profile list
```

For complete command reference, see [commands.md](references/commands.md).

### 4. Working with Docker

**Use Minikube's Docker Daemon:**

```bash
# Configure shell
eval $(minikube docker-env)

# Build image
docker build -t myapp:latest .

# Deploy without pulling
kubectl run myapp --image=myapp:latest --image-pull-policy=Never
```

**Load Local Image:**

```bash
# Load image to Minikube
minikube image load myimage:tag

# Or cache image
minikube cache add myimage:tag
```

### 5. Ingress Configuration

**Enable Ingress:**

```bash
minikube addons enable ingress
```

**Deploy with Ingress:**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
spec:
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp
            port:
              number: 80
```

**Update /etc/hosts:**

```bash
echo "$(minikube ip) myapp.local" | sudo tee -a /etc/hosts
```

**Access:**

```bash
curl http://myapp.local
```

### 6. Persistent Storage

**Enable Storage Provisioner:**

```bash
minikube addons enable storage-provisioner
minikube addons enable default-storageclass
```

**Create PVC:**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: myapp-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

**Use in Deployment:**

```yaml
spec:
  containers:
  - name: myapp
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: myapp-pvc
```

### 7. LoadBalancer Services

**Enable Tunnel:**

```bash
# Create tunnel (run in separate terminal)
minikube tunnel
```

**Create LoadBalancer Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  type: LoadBalancer
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 80
```

**Access Service:**

```bash
kubectl get svc myapp
# Use EXTERNAL-IP to access
```

### 8. Multiple Profiles

**Create Multiple Clusters:**

```bash
# Development cluster
minikube start -p dev --memory=2048 --cpus=1

# Testing cluster
minikube start -p test --memory=4096 --cpus=2

# Production-like cluster
minikube start -p staging --memory=8192 --cpus=4
```

**Switch Between Profiles:**

```bash
minikube profile dev
kubectl get nodes

minikube profile test
kubectl get nodes
```

**List All Profiles:**

```bash
minikube profile list
```

### 9. Monitoring and Debugging

**Enable Dashboard:**

```bash
minikube addons enable dashboard
minikube addons enable metrics-server
minikube dashboard
```

**View Logs:**

```bash
# Cluster logs
minikube logs

# Pod logs
kubectl logs <pod-name>

# Follow logs
kubectl logs -f <pod-name>
```

**Check Resources:**

```bash
# Node resources
kubectl top node

# Pod resources
kubectl top pod
```

**Debug Pod:**

```bash
# Describe pod
kubectl describe pod <pod-name>

# Get events
kubectl get events --sort-by='.lastTimestamp'

# Execute in pod
kubectl exec -it <pod-name> -- /bin/sh
```

### 10. Troubleshooting

**Common issues and solutions:**

**Cluster won't start:**
```bash
minikube delete
minikube start
```

**Docker permission denied (Linux):**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

**Cannot access service:**
```bash
# Use port forwarding
kubectl port-forward service/<service-name> 8080:80

# Or use tunnel
minikube tunnel
```

**Pods stuck in Pending:**
```bash
# Check resources
kubectl describe node minikube

# Increase resources
minikube delete
minikube start --memory=8192 --cpus=4
```

For comprehensive troubleshooting, see [troubleshooting.md](references/troubleshooting.md).

## Common Patterns

### Quick Deployment

```bash
# Deploy nginx
kubectl create deployment nginx --image=nginx:latest
kubectl expose deployment nginx --type=NodePort --port=80
minikube service nginx
```

### Deploy from YAML

```bash
kubectl apply -f deployment.yaml
kubectl get deployments
kubectl get pods
kubectl get services
```

### Scale Application

```bash
kubectl scale deployment myapp --replicas=5
kubectl get pods -w
```

### Update Image

```bash
kubectl set image deployment/myapp myapp=nginx:1.21
kubectl rollout status deployment/myapp
```

### Rollback Deployment

```bash
kubectl rollout undo deployment/myapp
kubectl rollout history deployment/myapp
```

## Example Applications

The skill includes example applications in `assets/example-apps/`:

**Hello Minikube:**
```bash
kubectl apply -f assets/example-apps/hello-minikube/deployment.yaml
minikube service hello-minikube
```

**Multi-Tier Application:**
```bash
# Deploy backend
kubectl apply -f assets/example-apps/multi-tier/backend.yaml

# Deploy frontend
kubectl apply -f assets/example-apps/multi-tier/frontend.yaml

# Access frontend
minikube service frontend
```

## Reference Documentation

### Installation Guide

See [installation.md](references/installation.md) for:
- Platform-specific installation
- Driver setup (Docker, VirtualBox, KVM2, Hyper-V)
- kubectl installation
- Post-installation configuration
- Verification steps

### Command Reference

See [commands.md](references/commands.md) for:
- Cluster management commands
- Profile management
- Addon management
- Service access
- Docker integration
- SSH and debugging
- Complete command reference

### Troubleshooting Guide

See [troubleshooting.md](references/troubleshooting.md) for:
- Common issues and solutions
- Platform-specific problems
- Network troubleshooting
- Resource management
- Debug commands
- Complete reset procedures

## Best Practices

1. **Use Docker driver** - Faster and more reliable than VM-based drivers
2. **Allocate sufficient resources** - At least 2GB RAM, 2 CPUs
3. **Enable useful addons** - dashboard, metrics-server, ingress
4. **Use profiles** - Separate dev, test, and staging environments
5. **Build locally** - Use Minikube's Docker daemon for faster builds
6. **Clean up regularly** - Delete unused clusters and images
7. **Use kubectl contexts** - Switch between clusters easily
8. **Test manifests locally** - Validate before deploying to production
9. **Monitor resources** - Use `kubectl top` to check usage
10. **Version control** - Keep deployment YAMLs in git

## Development Tips

1. **Hot reload** - Use `kubectl rollout restart` for quick updates
2. **Port forwarding** - Quick access without service exposure
3. **Local registry** - Use registry addon for local images
4. **Pause cluster** - Save resources when not in use
5. **Use NodePort** - Simpler than LoadBalancer for local dev
6. **Test ingress locally** - Add entries to /etc/hosts
7. **Copy files** - Use `kubectl cp` for quick file transfer
8. **Shell access** - `kubectl exec` or `minikube ssh` for debugging
9. **Resource limits** - Always set for realistic testing
10. **Helm charts** - Test Helm installations locally

## Production Preparation

Test these before production deployment:

1. **Resource limits** - Ensure requests/limits are set
2. **Health checks** - Configure liveness and readiness probes
3. **ConfigMaps/Secrets** - Test configuration management
4. **Persistent storage** - Verify PVC behavior
5. **Networking** - Test service communication
6. **Ingress rules** - Validate routing
7. **RBAC** - Test service accounts and permissions
8. **Rolling updates** - Test deployment strategies
9. **Rollback** - Verify rollback procedures
10. **Scaling** - Test horizontal pod autoscaling

## Resources

### Scripts
- `scripts/setup_minikube.py` - Automated cluster setup
- `scripts/deploy_app.py` - Application deployment
- `scripts/manage_cluster.py` - Cluster management

### Reference Documentation
- `references/installation.md` - Installation guide
- `references/commands.md` - Command reference
- `references/troubleshooting.md` - Troubleshooting guide

### Templates
- `assets/deployment-templates/` - Ready-to-use YAML templates
- `assets/example-apps/` - Example applications

### Official Resources
- Minikube Docs: https://minikube.sigs.k8s.io/docs/
- Kubernetes Docs: https://kubernetes.io/docs/
- kubectl Cheatsheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- GitHub: https://github.com/kubernetes/minikube
