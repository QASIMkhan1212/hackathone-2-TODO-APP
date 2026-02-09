# Minikube Troubleshooting Guide

## Common Issues and Solutions

### 1. Minikube Won't Start

#### Issue: "machine does not exist"
```bash
# Solution: Delete and recreate
minikube delete
minikube start
```

#### Issue: "Exiting due to DRV_NOT_HEALTHY"
```bash
# Check driver status
docker info  # For Docker driver
VBoxManage --version  # For VirtualBox

# Try different driver
minikube start --driver=docker
```

#### Issue: "Unable to pick a default driver"
```bash
# Install Docker or specify driver
minikube start --driver=virtualbox
```

#### Issue: Insufficient resources
```bash
# Reduce resource requirements
minikube start --memory=2048 --cpus=1

# Or increase system resources and retry
minikube start --memory=4096 --cpus=2
```

### 2. Docker Driver Issues

#### Issue: Docker permission denied (Linux)
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Or restart session
logout
# Log back in

# Start minikube
minikube start --driver=docker
```

#### Issue: Docker not running
```bash
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# macOS/Windows
# Start Docker Desktop application

# Verify Docker
docker ps
```

#### Issue: Docker daemon not accessible
```bash
# Check Docker socket
ls -la /var/run/docker.sock

# Fix permissions (Linux)
sudo chmod 666 /var/run/docker.sock
```

### 3. VirtualBox Issues

#### Issue: VirtualBox not installed
```bash
# Ubuntu/Debian
sudo apt-get install virtualbox

# macOS
brew install virtualbox

# Or download from virtualbox.org
```

#### Issue: VT-x/AMD-V not enabled
- Reboot computer
- Enter BIOS/UEFI settings
- Enable "Intel Virtualization Technology" or "AMD-V"
- Save and reboot

#### Issue: VirtualBox kernel module not loaded (Linux)
```bash
# Load kernel modules
sudo modprobe vboxdrv
sudo modprobe vboxnetflt

# Or reinstall VirtualBox
sudo apt-get install --reinstall virtualbox-dkms
```

### 4. Network Issues

#### Issue: Cannot access services
```bash
# Get service URL
minikube service <service-name> --url

# Or use port forwarding
kubectl port-forward service/<service-name> 8080:80

# Or use tunnel for LoadBalancer
minikube tunnel
```

#### Issue: DNS not working
```bash
# Check CoreDNS pods
kubectl get pods -n kube-system | grep coredns

# Restart CoreDNS
kubectl rollout restart deployment/coredns -n kube-system

# Or restart cluster
minikube stop
minikube start
```

#### Issue: Cannot pull images
```bash
# Check internet connectivity
minikube ssh -- ping -c 3 8.8.8.8

# Check DNS
minikube ssh -- nslookup google.com

# Use different DNS
minikube start --dns-domain=cluster.local
```

#### Issue: Port already in use
```bash
# Find process using port
sudo lsof -i :8443  # Linux/macOS
netstat -ano | findstr :8443  # Windows

# Kill process or use different port
minikube start --apiserver-port=8444
```

### 5. Storage Issues

#### Issue: Persistent volumes not working
```bash
# Enable storage provisioner addon
minikube addons enable storage-provisioner
minikube addons enable default-storageclass

# Check storage class
kubectl get storageclass
```

#### Issue: Disk space full
```bash
# Check disk usage
minikube ssh -- df -h

# Clean up Docker
eval $(minikube docker-env)
docker system prune -a

# Increase disk size (requires delete)
minikube delete
minikube start --disk-size=30g
```

#### Issue: PVC pending
```bash
# Check PVC status
kubectl get pvc

# Check events
kubectl describe pvc <pvc-name>

# Ensure storage provisioner is enabled
minikube addons enable storage-provisioner
```

### 6. Resource Issues

#### Issue: Pods stuck in "Pending"
```bash
# Check node resources
kubectl describe node minikube

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Increase cluster resources
minikube stop
minikube config set memory 4096
minikube config set cpus 2
minikube start
```

#### Issue: Out of memory
```bash
# Check memory usage
kubectl top nodes
kubectl top pods --all-namespaces

# Restart cluster with more memory
minikube delete
minikube start --memory=8192
```

#### Issue: High CPU usage
```bash
# Check what's consuming CPU
kubectl top pods --all-namespaces

# Scale down deployments
kubectl scale deployment <name> --replicas=1

# Or increase CPU allocation
minikube stop
minikube config set cpus 4
minikube start
```

### 7. kubectl Issues

#### Issue: kubectl not found
```bash
# Use minikube's kubectl
minikube kubectl -- get pods

# Or install kubectl separately
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# macOS
brew install kubectl

# Windows
choco install kubernetes-cli
```

#### Issue: kubectl can't connect to cluster
```bash
# Check cluster is running
minikube status

# Update kubeconfig
minikube update-context

# Or manually set context
kubectl config use-context minikube
```

#### Issue: Context not found
```bash
# List contexts
kubectl config get-contexts

# Set minikube context
kubectl config use-context minikube

# If missing, recreate
minikube delete
minikube start
```

### 8. Addon Issues

#### Issue: Dashboard not accessible
```bash
# Enable dashboard addon
minikube addons enable dashboard
minikube addons enable metrics-server

# Open dashboard
minikube dashboard

# If browser doesn't open, use URL
minikube dashboard --url
```

#### Issue: Ingress not working
```bash
# Enable ingress addon
minikube addons enable ingress

# Wait for ingress controller
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Check ingress controller
kubectl get pods -n ingress-nginx
```

#### Issue: Metrics server not working
```bash
# Enable metrics server
minikube addons enable metrics-server

# Wait for deployment
kubectl wait deployment metrics-server -n kube-system --for condition=Available=True --timeout=90s

# Verify
kubectl top nodes
```

### 9. Image Issues

#### Issue: Image pull errors
```bash
# Check image name
kubectl describe pod <pod-name>

# Use correct image pull policy
kubectl run myapp --image=myimage:latest --image-pull-policy=Never

# Or load image to minikube
minikube image load myimage:latest
```

#### Issue: Cannot build images locally
```bash
# Use minikube's Docker daemon
eval $(minikube docker-env)

# Verify
docker ps

# Build image
docker build -t myapp:latest .

# Deploy without pull
kubectl run myapp --image=myapp:latest --image-pull-policy=Never
```

#### Issue: Registry addon not working
```bash
# Enable registry
minikube addons enable registry

# Port forward registry
kubectl port-forward -n kube-system service/registry 5000:80

# Tag and push
docker tag myimage:latest localhost:5000/myimage:latest
docker push localhost:5000/myimage:latest
```

### 10. Performance Issues

#### Issue: Slow startup
```bash
# Use Docker driver (faster)
minikube start --driver=docker

# Reduce resource allocation
minikube start --memory=2048 --cpus=1

# Use cached images
minikube cache add nginx:latest
```

#### Issue: Cluster slow/unresponsive
```bash
# Check system resources
kubectl top nodes
kubectl top pods --all-namespaces

# Restart cluster
minikube stop
minikube start

# Clear Docker cache
eval $(minikube docker-env)
docker system prune -a
```

### 11. Windows-Specific Issues

#### Issue: Hyper-V conflicts with VirtualBox
```powershell
# Disable Hyper-V
bcdedit /set hypervisorlaunchtype off

# Reboot
Restart-Computer

# Use Docker driver instead
minikube start --driver=docker
```

#### Issue: WSL2 backend issues
```powershell
# Update WSL2
wsl --update

# Set Docker to use WSL2 backend
# In Docker Desktop: Settings > General > Use WSL2 based engine

# Start minikube
minikube start --driver=docker
```

#### Issue: PowerShell execution policy
```powershell
# Set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single command
powershell -ExecutionPolicy Bypass -Command "minikube start"
```

### 12. macOS-Specific Issues

#### Issue: Docker Desktop not starting
```bash
# Check Docker logs
~/Library/Containers/com.docker.docker/Data/log/

# Reset Docker Desktop
# Docker menu > Troubleshoot > Reset to factory defaults

# Or reinstall Docker Desktop
brew reinstall docker
```

#### Issue: Permission denied on /var/folders
```bash
# Reset minikube
minikube delete
rm -rf ~/.minikube

# Start fresh
minikube start
```

### 13. Linux-Specific Issues

#### Issue: Firewall blocking connections
```bash
# Allow required ports (8443 for API server)
sudo ufw allow 8443/tcp

# Or disable firewall temporarily
sudo ufw disable

# Check iptables
sudo iptables -L
```

#### Issue: AppArmor/SELinux blocking
```bash
# Temporarily disable SELinux (CentOS/RHEL)
sudo setenforce 0

# Or configure AppArmor (Ubuntu)
sudo aa-complain /etc/apparmor.d/*
```

## Debugging Commands

### Collect Diagnostic Information

```bash
# Get cluster logs
minikube logs > minikube.log

# Get node info
kubectl describe node minikube > node-info.txt

# Get pod info
kubectl get pods --all-namespaces -o wide > pods.txt

# Get events
kubectl get events --all-namespaces --sort-by='.lastTimestamp' > events.txt

# Get system info
minikube kubectl -- cluster-info dump > cluster-dump.txt
```

### Check Component Health

```bash
# Check system pods
kubectl get pods -n kube-system

# Check kubelet
minikube ssh -- sudo systemctl status kubelet

# Check Docker
minikube ssh -- docker ps

# Check logs
minikube logs -f
```

## Complete Reset

If all else fails, perform a complete reset:

```bash
# Stop minikube
minikube stop

# Delete cluster
minikube delete --all --purge

# Remove configuration
rm -rf ~/.minikube
rm -rf ~/.kube

# Restart Docker (if using Docker driver)
# Linux
sudo systemctl restart docker

# macOS/Windows - Restart Docker Desktop

# Start fresh
minikube start
```

## Getting Help

### Log Files Location

- **Linux/macOS**: `~/.minikube/logs/`
- **Windows**: `C:\Users\<username>\.minikube\logs\`

### Report Issues

1. Collect logs: `minikube logs`
2. Get version: `minikube version`
3. Report at: https://github.com/kubernetes/minikube/issues

### Useful Debug Info

```bash
# System info
minikube version
kubectl version
docker --version

# Cluster status
minikube status
kubectl cluster-info

# Resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Recent events
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | tail -20
```
