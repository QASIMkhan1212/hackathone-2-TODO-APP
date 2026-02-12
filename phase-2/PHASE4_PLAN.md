# Phase IV: Local Kubernetes Deployment - Comprehensive Plan

## Overview
Deploy the Q.TODO App (Todo Chatbot) on a local Kubernetes cluster using Minikube, Helm Charts, with AI-assisted DevOps tools (Docker Gordon, kubectl-ai, Kagent).

---

## Table of Contents
1. [Prerequisites & Environment Setup](#1-prerequisites--environment-setup)
2. [Containerization Strategy](#2-containerization-strategy)
3. [Helm Charts Architecture](#3-helm-charts-architecture)
4. [Kubernetes Deployment Strategy](#4-kubernetes-deployment-strategy)
5. [Implementation Tasks](#5-implementation-tasks)
6. [Verification & Testing](#6-verification--testing)

---

## 1. Prerequisites & Environment Setup

### 1.1 Required Tools Installation
| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | 4.53+ | Container runtime with Gordon AI |
| Minikube | Latest | Local Kubernetes cluster |
| kubectl | Latest | Kubernetes CLI |
| Helm | 3.x | Kubernetes package manager |
| kubectl-ai | Latest | AI-assisted kubectl operations |
| Kagent | Latest | Advanced AI Kubernetes operations |

### 1.2 Environment Verification Commands
```bash
# Verify Docker with Gordon
docker --version
docker ai "What can you do?"

# Verify Minikube
minikube version

# Verify kubectl
kubectl version --client

# Verify Helm
helm version

# Verify kubectl-ai
kubectl-ai --version

# Verify Kagent
kagent --version
```

### 1.3 Minikube Cluster Setup
```bash
# Start Minikube with adequate resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

---

## 2. Containerization Strategy

### 2.1 Application Components
| Component | Base Image | Port | Description |
|-----------|------------|------|-------------|
| Frontend | node:20-alpine | 3000 | Next.js application |
| Backend | python:3.11-slim | 8000 | FastAPI application |

### 2.2 Frontend Dockerfile (Next.js)
**Location:** `frontend/Dockerfile`

```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

### 2.3 Backend Dockerfile (FastAPI)
**Location:** `backend/Dockerfile`

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runner
FROM python:3.11-slim AS runner
WORKDIR /app

# Create non-root user
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/bash appuser

# Copy dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Set ownership
RUN chown -R appuser:appgroup /app

USER appuser
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2.4 Docker Compose for Local Testing
**Location:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
      - NEXT_PUBLIC_APP_URL=http://localhost:3000
    depends_on:
      - backend
    networks:
      - qtodo-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - BETTER_AUTH_URL=http://frontend:3000
      - GROQ_API_KEY=${GROQ_API_KEY}
    networks:
      - qtodo-network

networks:
  qtodo-network:
    driver: bridge
```

### 2.5 Gordon AI Commands for Containerization
```bash
# Use Gordon for intelligent Docker operations
docker ai "Create an optimized multi-stage Dockerfile for a Next.js application"
docker ai "Create a secure Dockerfile for a FastAPI Python application"
docker ai "Analyze my Dockerfile for security vulnerabilities"
docker ai "Optimize my Docker image size"
docker ai "Build and tag images for qtodo-frontend and qtodo-backend"
```

---

## 3. Helm Charts Architecture

### 3.1 Chart Structure
```
helm/
├── qtodo/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-dev.yaml
│   ├── values-prod.yaml
│   ├── templates/
│   │   ├── _helpers.tpl
│   │   ├── NOTES.txt
│   │   ├── frontend/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── configmap.yaml
│   │   │   └── hpa.yaml
│   │   ├── backend/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── configmap.yaml
│   │   │   ├── secret.yaml
│   │   │   └── hpa.yaml
│   │   ├── ingress.yaml
│   │   └── networkpolicy.yaml
│   └── charts/
```

### 3.2 Chart.yaml
```yaml
apiVersion: v2
name: qtodo
description: Q.TODO App - AI-powered Todo Chatbot
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - chatbot
  - ai
  - nextjs
  - fastapi
maintainers:
  - name: Q.TODO Team
```

### 3.3 values.yaml (Default Configuration)
```yaml
# Global settings
global:
  namespace: qtodo
  imageRegistry: ""
  imagePullSecrets: []

# Frontend configuration
frontend:
  replicaCount: 2
  image:
    repository: qtodo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 3000
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilization: 70
  env:
    NEXT_PUBLIC_API_URL: "http://qtodo-backend:8000"
    NEXT_PUBLIC_APP_URL: "http://localhost:3000"

# Backend configuration
backend:
  replicaCount: 2
  image:
    repository: qtodo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilization: 70
  secrets:
    databaseUrl: ""
    betterAuthSecret: ""
    groqApiKey: ""

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
  hosts:
    - host: qtodo.local
      paths:
        - path: /
          pathType: Prefix
          service: frontend
        - path: /api
          pathType: Prefix
          service: backend

# Network policies
networkPolicy:
  enabled: true
```

### 3.4 Frontend Deployment Template
**Location:** `helm/qtodo/templates/frontend/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "qtodo.fullname" . }}-frontend
  labels:
    {{- include "qtodo.labels" . | nindent 4 }}
    app.kubernetes.io/component: frontend
spec:
  {{- if not .Values.frontend.autoscaling.enabled }}
  replicas: {{ .Values.frontend.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "qtodo.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: frontend
  template:
    metadata:
      labels:
        {{- include "qtodo.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: frontend
    spec:
      containers:
        - name: frontend
          image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
          imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 3000
              protocol: TCP
          envFrom:
            - configMapRef:
                name: {{ include "qtodo.fullname" . }}-frontend-config
          livenessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.frontend.resources | nindent 12 }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
```

### 3.5 Backend Deployment Template
**Location:** `helm/qtodo/templates/backend/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "qtodo.fullname" . }}-backend
  labels:
    {{- include "qtodo.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  {{- if not .Values.backend.autoscaling.enabled }}
  replicas: {{ .Values.backend.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "qtodo.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
  template:
    metadata:
      labels:
        {{- include "qtodo.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: backend
    spec:
      containers:
        - name: backend
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          envFrom:
            - configMapRef:
                name: {{ include "qtodo.fullname" . }}-backend-config
            - secretRef:
                name: {{ include "qtodo.fullname" . }}-backend-secret
          livenessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
```

---

## 4. Kubernetes Deployment Strategy

### 4.1 Deployment Flow
```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT PIPELINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Build   │───▶│  Push to │───▶│  Deploy  │───▶│  Verify  │  │
│  │  Images  │    │ Registry │    │  Helm    │    │  Health  │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │                │               │               │        │
│       ▼                ▼               ▼               ▼        │
│   Gordon AI      Minikube        kubectl-ai        Kagent      │
│                  Registry                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Namespace Strategy
```yaml
# Create dedicated namespace
apiVersion: v1
kind: Namespace
metadata:
  name: qtodo
  labels:
    name: qtodo
    environment: development
```

### 4.3 Resource Quotas
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: qtodo-quota
  namespace: qtodo
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 4Gi
    limits.cpu: "8"
    limits.memory: 8Gi
    pods: "20"
```

### 4.4 kubectl-ai Commands for Deployment
```bash
# Create namespace
kubectl-ai "create a namespace called qtodo with appropriate labels"

# Deploy frontend
kubectl-ai "deploy the todo frontend with 2 replicas using image qtodo-frontend:latest"

# Deploy backend
kubectl-ai "deploy the backend API with 2 replicas and environment variables from secret"

# Scale operations
kubectl-ai "scale the backend to handle more load"

# Troubleshooting
kubectl-ai "check why the pods are failing"
kubectl-ai "show logs from the backend pods"
kubectl-ai "describe the frontend deployment"
```

### 4.5 Kagent Commands for Advanced Operations
```bash
# Cluster analysis
kagent "analyze the cluster health"
kagent "check resource utilization in qtodo namespace"

# Optimization
kagent "optimize resource allocation for qtodo deployments"
kagent "suggest HPA settings based on current load patterns"

# Security
kagent "audit security posture of qtodo namespace"
kagent "check for any exposed secrets"
```

---

## 5. Implementation Tasks

### Task 1: Environment Setup (30 mins)
- [ ] Install/Update Docker Desktop 4.53+
- [ ] Enable Gordon AI in Docker Desktop settings
- [ ] Install Minikube
- [ ] Install kubectl
- [ ] Install Helm 3.x
- [ ] Install kubectl-ai
- [ ] Install Kagent
- [ ] Verify all installations

### Task 2: Containerization (45 mins)
- [ ] Create Frontend Dockerfile with multi-stage build
- [ ] Create Backend Dockerfile with multi-stage build
- [ ] Update Next.js config for standalone output
- [ ] Create .dockerignore files
- [ ] Use Gordon AI to optimize Dockerfiles
- [ ] Build and test images locally
- [ ] Create docker-compose.yml for local testing

### Task 3: Minikube Setup (20 mins)
- [ ] Start Minikube cluster with resources
- [ ] Enable required addons (ingress, metrics-server)
- [ ] Configure Minikube Docker environment
- [ ] Push images to Minikube registry
- [ ] Verify cluster readiness

### Task 4: Helm Charts Creation (60 mins)
- [ ] Create chart structure
- [ ] Write Chart.yaml
- [ ] Write values.yaml with all configurations
- [ ] Create frontend templates (deployment, service, configmap, hpa)
- [ ] Create backend templates (deployment, service, configmap, secret, hpa)
- [ ] Create ingress template
- [ ] Create network policy template
- [ ] Create _helpers.tpl with common functions
- [ ] Use kubectl-ai to generate/validate manifests
- [ ] Lint Helm charts

### Task 5: Deployment (30 mins)
- [ ] Create qtodo namespace
- [ ] Create secrets for sensitive data
- [ ] Deploy using Helm
- [ ] Verify deployments with kubectl-ai
- [ ] Analyze cluster health with Kagent

### Task 6: Verification & Testing (30 mins)
- [ ] Check pod status and logs
- [ ] Test frontend accessibility
- [ ] Test backend API endpoints
- [ ] Test frontend-backend communication
- [ ] Test AI chatbot functionality
- [ ] Verify HPA is working
- [ ] Document access URLs

---

## 6. Verification & Testing

### 6.1 Health Check Commands
```bash
# Check all resources
kubectl get all -n qtodo

# Check pod status
kubectl get pods -n qtodo -o wide

# Check services
kubectl get svc -n qtodo

# Check ingress
kubectl get ingress -n qtodo

# Check HPA
kubectl get hpa -n qtodo

# View pod logs
kubectl logs -n qtodo -l app.kubernetes.io/component=frontend --tail=100
kubectl logs -n qtodo -l app.kubernetes.io/component=backend --tail=100
```

### 6.2 Access the Application
```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts (or C:\Windows\System32\drivers\etc\hosts on Windows)
# <minikube-ip> qtodo.local

# Or use Minikube tunnel
minikube tunnel

# Access URLs
# Frontend: http://qtodo.local
# Backend API: http://qtodo.local/api
```

### 6.3 Functional Tests
```bash
# Test backend health
curl http://qtodo.local/api/

# Test frontend
curl http://qtodo.local/

# Using kubectl-ai for verification
kubectl-ai "verify the qtodo application is running correctly"
kubectl-ai "check if all endpoints are accessible"

# Using Kagent for analysis
kagent "analyze qtodo application performance"
kagent "check for any issues with the deployment"
```

### 6.4 Load Testing (Optional)
```bash
# Simple load test
kubectl-ai "create a load test job for the backend API"

# Monitor scaling
watch kubectl get pods -n qtodo
watch kubectl get hpa -n qtodo
```

---

## Deployment Commands Summary

### Quick Start (All-in-One)
```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress

# 2. Set Docker environment to Minikube
eval $(minikube docker-env)  # Linux/Mac
# OR for Windows PowerShell:
# & minikube -p minikube docker-env --shell powershell | Invoke-Expression

# 3. Build images
docker build -t qtodo-frontend:latest ./frontend
docker build -t qtodo-backend:latest ./backend

# 4. Create namespace and secrets
kubectl create namespace qtodo
kubectl create secret generic qtodo-secrets -n qtodo \
  --from-literal=DATABASE_URL="your-db-url" \
  --from-literal=BETTER_AUTH_SECRET="your-secret" \
  --from-literal=GROQ_API_KEY="your-api-key"

# 5. Deploy with Helm
helm install qtodo ./helm/qtodo -n qtodo -f ./helm/qtodo/values.yaml

# 6. Verify
kubectl get all -n qtodo

# 7. Access
minikube tunnel
# Visit: http://qtodo.local
```

---

## Rollback Strategy
```bash
# List Helm releases
helm list -n qtodo

# Rollback to previous version
helm rollback qtodo 1 -n qtodo

# Or uninstall completely
helm uninstall qtodo -n qtodo
```

---

## Monitoring & Observability

### Minikube Dashboard
```bash
minikube dashboard
```

### Resource Monitoring
```bash
# CPU and Memory usage
kubectl top pods -n qtodo
kubectl top nodes

# Using Kagent
kagent "show resource utilization trends"
```

---

## Troubleshooting Guide

| Issue | Command | Solution |
|-------|---------|----------|
| Pods not starting | `kubectl-ai "check why pods are failing"` | Check resource limits, image pull |
| Service not accessible | `kubectl-ai "debug service connectivity"` | Verify service selectors |
| Ingress not working | `minikube addons enable ingress` | Enable ingress addon |
| Image pull errors | `eval $(minikube docker-env)` | Use Minikube's Docker daemon |
| OOM errors | `kagent "optimize resource allocation"` | Increase memory limits |

---

## Security Considerations

1. **Secrets Management**: All sensitive data stored in Kubernetes Secrets
2. **Network Policies**: Restrict pod-to-pod communication
3. **Non-root Containers**: All containers run as non-root user
4. **Resource Limits**: Prevent resource exhaustion attacks
5. **Image Security**: Multi-stage builds to minimize attack surface

---

## Files to Create

| File | Location | Purpose |
|------|----------|---------|
| Dockerfile | frontend/Dockerfile | Frontend container |
| Dockerfile | backend/Dockerfile | Backend container |
| .dockerignore | frontend/.dockerignore | Exclude files |
| .dockerignore | backend/.dockerignore | Exclude files |
| docker-compose.yml | ./docker-compose.yml | Local testing |
| Chart.yaml | helm/qtodo/Chart.yaml | Helm chart metadata |
| values.yaml | helm/qtodo/values.yaml | Default values |
| _helpers.tpl | helm/qtodo/templates/_helpers.tpl | Template helpers |
| deployment.yaml | helm/qtodo/templates/frontend/deployment.yaml | Frontend deployment |
| service.yaml | helm/qtodo/templates/frontend/service.yaml | Frontend service |
| configmap.yaml | helm/qtodo/templates/frontend/configmap.yaml | Frontend config |
| hpa.yaml | helm/qtodo/templates/frontend/hpa.yaml | Frontend autoscaling |
| deployment.yaml | helm/qtodo/templates/backend/deployment.yaml | Backend deployment |
| service.yaml | helm/qtodo/templates/backend/service.yaml | Backend service |
| configmap.yaml | helm/qtodo/templates/backend/configmap.yaml | Backend config |
| secret.yaml | helm/qtodo/templates/backend/secret.yaml | Backend secrets |
| hpa.yaml | helm/qtodo/templates/backend/hpa.yaml | Backend autoscaling |
| ingress.yaml | helm/qtodo/templates/ingress.yaml | Ingress rules |
| NOTES.txt | helm/qtodo/templates/NOTES.txt | Post-install notes |

---

## Expected Outcome

After completing Phase IV:
- ✅ Frontend and Backend containerized with optimized Docker images
- ✅ Helm charts created for declarative deployment
- ✅ Application deployed on Minikube with 2+ replicas each
- ✅ Horizontal Pod Autoscaler configured
- ✅ Ingress configured for external access
- ✅ Network policies for security
- ✅ AI-assisted operations with kubectl-ai and Kagent
- ✅ Full functionality preserved (auth, tasks, AI chatbot)
