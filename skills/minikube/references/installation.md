# Minikube Installation Guide

## Prerequisites

### System Requirements
- 2 CPUs or more
- 2GB+ of free memory
- 20GB+ of free disk space
- Internet connection
- Container or virtual machine manager

### Supported Container/VM Managers
- Docker (recommended)
- Podman
- VirtualBox
- VMware
- Hyper-V (Windows)
- KVM (Linux)
- Parallels (macOS)
- QEMU

## Installation by Platform

### Linux

#### x86-64 (amd64)

**Binary Download:**
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64
```

**Debian/Ubuntu (DEB package):**
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube_latest_amd64.deb
sudo dpkg -i minikube_latest_amd64.deb
```

**RPM-based (Fedora/RHEL/CentOS):**
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-latest.x86_64.rpm
sudo rpm -Uvh minikube-latest.x86_64.rpm
```

#### ARM64

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-arm64
sudo install minikube-linux-arm64 /usr/local/bin/minikube
rm minikube-linux-arm64
```

### macOS

#### Homebrew (Recommended)

```bash
brew install minikube
```

#### Binary Download (Intel)

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-amd64
sudo install minikube-darwin-amd64 /usr/local/bin/minikube
rm minikube-darwin-amd64
```

#### Binary Download (Apple Silicon)

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-arm64
sudo install minikube-darwin-arm64 /usr/local/bin/minikube
rm minikube-darwin-arm64
```

### Windows

#### Chocolatey

```powershell
choco install minikube
```

#### Scoop

```powershell
scoop install minikube
```

#### Windows Installer (.exe)

Download from: https://storage.googleapis.com/minikube/releases/latest/minikube-installer.exe

#### PowerShell (Manual)

```powershell
New-Item -Path 'c:\' -Name 'minikube' -ItemType Directory -Force
Invoke-WebRequest -OutFile 'c:\minikube\minikube.exe' -Uri 'https://github.com/kubernetes/minikube/releases/latest/download/minikube-windows-amd64.exe' -UseBasicParsing
```

Add to PATH:
```powershell
$oldPath = [Environment]::GetEnvironmentVariable('Path', [EnvironmentVariableTarget]::Machine)
if ($oldPath.Split(';') -inotcontains 'C:\minikube'){
  [Environment]::SetEnvironmentVariable('Path', $('{0};C:\minikube' -f $oldPath), [EnvironmentVariableTarget]::Machine)
}
```

## Installing kubectl

Minikube includes kubectl, but you can install it separately:

### Linux
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### macOS
```bash
brew install kubectl
```

### Windows
```powershell
choco install kubernetes-cli
```

## Installing Docker (Recommended Driver)

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER && newgrp docker
```

### macOS
Download Docker Desktop: https://www.docker.com/products/docker-desktop

### Windows
Download Docker Desktop: https://www.docker.com/products/docker-desktop

## Verification

```bash
minikube version
kubectl version --client
docker --version
```

## Initial Start

```bash
minikube start
```

With specific driver:
```bash
minikube start --driver=docker
minikube start --driver=virtualbox
minikube start --driver=kvm2
```

## Post-Installation Configuration

### Set Default Driver

```bash
minikube config set driver docker
```

### Configure Resource Allocation

```bash
minikube config set memory 4096
minikube config set cpus 2
minikube config set disk-size 20g
```

### Enable Auto-Start on Boot (Linux)

Create systemd service:
```bash
sudo tee /etc/systemd/system/minikube.service <<EOF
[Unit]
Description=Minikube Kubernetes Cluster
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/minikube start
ExecStop=/usr/local/bin/minikube stop
RemainAfterExit=yes
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable minikube
```

## Driver-Specific Setup

### Docker Driver (Recommended)

**Advantages:**
- No VM overhead
- Faster startup
- Better integration

**Setup:**
```bash
minikube start --driver=docker
```

### VirtualBox Driver

**Installation:**
```bash
# Linux
sudo apt-get install virtualbox

# macOS
brew install virtualbox

# Windows - Download from virtualbox.org
```

**Usage:**
```bash
minikube start --driver=virtualbox
```

### KVM2 Driver (Linux)

**Installation:**
```bash
sudo apt-get install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils
sudo usermod -aG libvirt $USER
curl -LO https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2
sudo install docker-machine-driver-kvm2 /usr/local/bin/
```

**Usage:**
```bash
minikube start --driver=kvm2
```

### Hyper-V Driver (Windows)

**Enable Hyper-V:**
```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

**Usage:**
```powershell
minikube start --driver=hyperv
```

## Troubleshooting Installation

### Permission Denied (Linux)
```bash
sudo usermod -aG docker $USER && newgrp docker
```

### VirtualBox Not Found
```bash
minikube start --driver=docker
```

### Port Already in Use
```bash
minikube delete
minikube start
```

### Insufficient Resources
```bash
minikube start --memory=2048 --cpus=2
```

## Updating Minikube

### Linux/macOS
```bash
minikube update-check
# Then reinstall using installation commands above
```

### Windows (Chocolatey)
```powershell
choco upgrade minikube
```

### Windows (Scoop)
```powershell
scoop update minikube
```

## Uninstallation

### Remove Minikube Binary

**Linux/macOS:**
```bash
sudo rm /usr/local/bin/minikube
```

**Windows:**
```powershell
Remove-Item 'C:\minikube\minikube.exe'
```

### Remove All Clusters

```bash
minikube delete --all --purge
```

### Remove Configuration

```bash
rm -rf ~/.minikube
```

## Next Steps

After installation:
1. Start your first cluster: `minikube start`
2. Enable dashboard: `minikube dashboard`
3. Deploy your first app: `kubectl create deployment hello-minikube --image=kicbase/echo-server:1.0`
4. Explore addons: `minikube addons list`
