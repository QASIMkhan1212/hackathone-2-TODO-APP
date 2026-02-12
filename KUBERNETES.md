# Q.TODO App - Kubernetes Deployment Guide

## Phase IV: Local Kubernetes Deployment

This guide covers deploying the Q.TODO AI-powered Todo Chatbot application to a local Kubernetes cluster using Minikube and Helm.

## Prerequisites

Before deploying, ensure you have the following installed:

- **Docker Desktop** - Container runtime
- **Minikube** - Local Kubernetes cluster
- **kubectl** - Kubernetes CLI
- **Helm** - Kubernetes package manager

### Optional AI-Assisted Tools
- **Docker Gordon** - AI assistant for Docker operations
- **kubectl-ai** - Natural language interface for kubectl
- **Kagent** - Kubernetes AI agent

## Architecture Overview

```
                    ┌─────────────────────────────────────────┐
                    │              Minikube Cluster            │
                    │  ┌───────────────────────────────────┐  │
                    │  │           Ingress (nginx)          │  │
                    │  │         qtodo.local                │  │
                    │  └─────────────┬─────────────────────┘  │
                    │                │                         │
                    │    ┌───────────┴───────────┐            │
                    │    │                       │            │
                    │    ▼                       ▼            │
                    │  ┌─────────┐         ┌─────────┐        │
                    │  │Frontend │         │ Backend │        │
                    │  │Next.js  │────────▶│ FastAPI │        │
                    │  │ (2-5)   │         │ (2-10)  │        │
                    │  └─────────┘         └─────────┘        │
                    │       │                   │             │
                    │       └───────┬───────────┘             │
                    │               │                         │
                    │  ┌────────────┴────────────┐            │
                    │  │   Horizontal Pod        │            │
                    │  │   Autoscaler (HPA)      │            │
                    │  └─────────────────────────┘            │
                    └─────────────────────────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────────────┐
                    │         External Services               │
                    │  • PostgreSQL (Neon/Supabase)          │
                    │  • GROQ API (LLM)                      │
                    │  • Better Auth                          │
                    └─────────────────────────────────────────┘
```

## Quick Start

### Windows (PowerShell)
```powershell
# Set environment variables (optional - will use placeholders if not set)
$env:DATABASE_URL = "your-database-url"
$env:BETTER_AUTH_SECRET = "your-auth-secret"
$env:GROQ_API_KEY = "your-groq-api-key"

# Run deployment script
.\scripts\deploy.ps1
```

### Linux/macOS (Bash)
```bash
# Set environment variables (optional - will use placeholders if not set)
export DATABASE_URL="your-database-url"
export BETTER_AUTH_SECRET="your-auth-secret"
export GROQ_API_KEY="your-groq-api-key"

# Make script executable and run
chmod +x ./scripts/deploy.sh
./scripts/deploy.sh
```

## Manual Deployment Steps

### 1. Start Minikube
```bash
# Start with recommended resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Build Docker Images
```bash
# Set Docker environment to Minikube
eval $(minikube docker-env)  # Linux/macOS
# OR for PowerShell:
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build frontend
docker build -t qtodo-frontend:latest ./frontend

# Build backend
docker build -t qtodo-backend:latest ./backend
```

### 3. Deploy with Helm
```bash
# Create namespace
kubectl create namespace qtodo

# Install the chart
helm upgrade --install qtodo ./helm/qtodo \
    --namespace qtodo \
    --set backend.secrets.databaseUrl="$DATABASE_URL" \
    --set backend.secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
    --set backend.secrets.groqApiKey="$GROQ_API_KEY" \
    --wait \
    --timeout 5m
```

### 4. Access the Application

**Option 1: Add to hosts file**
```bash
# Get Minikube IP
minikube ip

# Add to hosts file:
# Linux/macOS: /etc/hosts
# Windows: C:\Windows\System32\drivers\etc\hosts
<MINIKUBE_IP> qtodo.local
```

**Option 2: Use Minikube tunnel**
```bash
minikube tunnel
```

Then access:
- Frontend: http://qtodo.local
- Backend API: http://qtodo.local/api

## Helm Chart Configuration

### Default Values
| Parameter | Default | Description |
|-----------|---------|-------------|
| `frontend.replicaCount` | 2 | Initial frontend replicas |
| `frontend.autoscaling.minReplicas` | 2 | Minimum frontend replicas |
| `frontend.autoscaling.maxReplicas` | 5 | Maximum frontend replicas |
| `backend.replicaCount` | 2 | Initial backend replicas |
| `backend.autoscaling.minReplicas` | 2 | Minimum backend replicas |
| `backend.autoscaling.maxReplicas` | 10 | Maximum backend replicas |
| `ingress.enabled` | true | Enable Ingress |
| `ingress.hosts[0].host` | qtodo.local | Application hostname |

### Custom Values File
Create a `values-custom.yaml` for your environment:
```yaml
frontend:
  replicaCount: 3
  autoscaling:
    minReplicas: 3
    maxReplicas: 8

backend:
  replicaCount: 3
  secrets:
    databaseUrl: "postgresql://..."
    betterAuthSecret: "your-secret"
    groqApiKey: "gsk_..."
```

Deploy with custom values:
```bash
helm upgrade --install qtodo ./helm/qtodo -n qtodo -f values-custom.yaml
```

## AI-Assisted Operations

### Using kubectl-ai
```bash
# Check deployment status
kubectl-ai "check status of qtodo deployment"

# View logs
kubectl-ai "show logs from backend pods"

# Scale deployment
kubectl-ai "scale frontend to 3 replicas"

# Debug issues
kubectl-ai "why are pods not ready in qtodo namespace"
```

### Using Docker Gordon
```bash
# Get container help
docker ai "how do I optimize my Dockerfile"

# Debug container issues
docker ai "analyze why my container is failing"

# Resource optimization
docker ai "suggest resource limits for my containers"
```

### Using Kagent
```bash
# Cluster health analysis
kagent "analyze cluster health"

# Resource optimization
kagent "optimize resource allocation for qtodo"

# Troubleshooting
kagent "diagnose issues with qtodo deployment"
```

## Useful Commands

### Monitor Deployment
```bash
# Watch pods
kubectl get pods -n qtodo -w

# View all resources
kubectl get all -n qtodo

# Check HPA status
kubectl get hpa -n qtodo

# View pod logs
kubectl logs -n qtodo -l app.kubernetes.io/component=frontend --tail=100
kubectl logs -n qtodo -l app.kubernetes.io/component=backend --tail=100
```

### Scaling
```bash
# Manual scaling
kubectl scale deployment qtodo-frontend --replicas=3 -n qtodo

# View autoscaling metrics
kubectl describe hpa -n qtodo
```

### Debugging
```bash
# Describe pod for events
kubectl describe pod <pod-name> -n qtodo

# Execute into pod
kubectl exec -it <pod-name> -n qtodo -- /bin/sh

# Port forward for local access
kubectl port-forward svc/qtodo-frontend 3000:3000 -n qtodo
kubectl port-forward svc/qtodo-backend 8000:8000 -n qtodo
```

## Cleanup

### Using Script
```bash
# Windows
.\scripts\cleanup.ps1

# Linux/macOS
./scripts/cleanup.sh
```

### Manual Cleanup
```bash
# Uninstall Helm release
helm uninstall qtodo -n qtodo

# Delete namespace
kubectl delete namespace qtodo

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## Troubleshooting

### Common Issues

**1. Pods stuck in Pending state**
```bash
kubectl describe pod <pod-name> -n qtodo
# Check for resource constraints or image pull issues
```

**2. Ingress not working**
```bash
# Ensure ingress addon is enabled
minikube addons enable ingress

# Check ingress controller
kubectl get pods -n ingress-nginx
```

**3. Image pull errors**
```bash
# Ensure Docker env is set to Minikube
eval $(minikube docker-env)

# Rebuild images
docker build -t qtodo-frontend:latest ./frontend
docker build -t qtodo-backend:latest ./backend
```

**4. HPA not scaling**
```bash
# Check metrics-server
minikube addons enable metrics-server

# Verify metrics are available
kubectl top pods -n qtodo
```

## Security Considerations

- Secrets are stored in Kubernetes Secrets (base64 encoded)
- For production, consider using:
  - External secrets manager (Vault, AWS Secrets Manager)
  - Sealed Secrets
  - SOPS
- Network policies can be enabled in `values.yaml`
- Pods run as non-root users
- Containers have minimal capabilities

## File Structure

```
helm/
└── qtodo/
    ├── Chart.yaml           # Chart metadata
    ├── values.yaml          # Default configuration
    └── templates/
        ├── _helpers.tpl     # Template helpers
        ├── namespace.yaml   # Namespace definition
        ├── serviceaccount.yaml
        ├── ingress.yaml     # Ingress rules
        ├── NOTES.txt        # Post-install notes
        ├── frontend/
        │   ├── deployment.yaml
        │   ├── service.yaml
        │   ├── configmap.yaml
        │   └── hpa.yaml
        └── backend/
            ├── deployment.yaml
            ├── service.yaml
            ├── configmap.yaml
            ├── secret.yaml
            └── hpa.yaml

scripts/
├── deploy.sh      # Bash deployment script
├── deploy.ps1     # PowerShell deployment script
└── cleanup.sh     # Cleanup script
```
