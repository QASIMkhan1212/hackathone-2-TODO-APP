# ============================================
# Q.TODO App - Kubernetes Deployment Script (PowerShell)
# ============================================
# This script deploys the Q.TODO application to Minikube
# ============================================

$ErrorActionPreference = "Stop"

# Configuration
$NAMESPACE = "qtodo"
$RELEASE_NAME = "qtodo"
$CHART_PATH = "./helm/qtodo"

Write-Host "============================================" -ForegroundColor Blue
Write-Host "  Q.TODO App - Kubernetes Deployment" -ForegroundColor Blue
Write-Host "============================================" -ForegroundColor Blue

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."

    # Check Docker
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker is not installed"
        exit 1
    }

    # Check Minikube
    if (-not (Get-Command minikube -ErrorAction SilentlyContinue)) {
        Write-Error "Minikube is not installed"
        exit 1
    }

    # Check kubectl
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        Write-Error "kubectl is not installed"
        exit 1
    }

    # Check Helm
    if (-not (Get-Command helm -ErrorAction SilentlyContinue)) {
        Write-Error "Helm is not installed"
        exit 1
    }

    Write-Status "All prerequisites satisfied!"
}

# Start Minikube
function Start-MinikubeCluster {
    Write-Status "Starting Minikube..."

    $status = minikube status 2>$null
    if ($status -match "Running") {
        Write-Status "Minikube is already running"
    } else {
        minikube start --cpus=4 --memory=8192 --driver=docker
    }

    # Enable addons
    Write-Status "Enabling Minikube addons..."
    minikube addons enable ingress
    minikube addons enable metrics-server

    Write-Status "Minikube is ready!"
}

# Build Docker images
function Build-DockerImages {
    Write-Status "Building Docker images..."

    # Set Docker environment to Minikube
    & minikube -p minikube docker-env --shell powershell | Invoke-Expression

    # Build frontend
    Write-Status "Building frontend image..."
    docker build -t qtodo-frontend:latest ./frontend `
        --build-arg NEXT_PUBLIC_API_URL=http://qtodo-backend:8000 `
        --build-arg NEXT_PUBLIC_APP_URL=http://localhost:3000

    # Build backend
    Write-Status "Building backend image..."
    docker build -t qtodo-backend:latest ./backend

    Write-Status "Docker images built successfully!"
}

# Create namespace and secrets
function Initialize-Namespace {
    Write-Status "Setting up namespace and secrets..."

    # Create namespace if it doesn't exist
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

    # Check for environment variables
    $DATABASE_URL = $env:DATABASE_URL
    $BETTER_AUTH_SECRET = $env:BETTER_AUTH_SECRET
    $GROQ_API_KEY = $env:GROQ_API_KEY

    if (-not $DATABASE_URL) {
        Write-Warning "DATABASE_URL is not set. Using placeholder."
        $script:DATABASE_URL = "postgresql://user:pass@localhost:5432/db"
    } else {
        $script:DATABASE_URL = $DATABASE_URL
    }

    if (-not $BETTER_AUTH_SECRET) {
        Write-Warning "BETTER_AUTH_SECRET is not set. Using placeholder."
        $script:BETTER_AUTH_SECRET = "your-secret-here"
    } else {
        $script:BETTER_AUTH_SECRET = $BETTER_AUTH_SECRET
    }

    if (-not $GROQ_API_KEY) {
        Write-Warning "GROQ_API_KEY is not set. Using placeholder."
        $script:GROQ_API_KEY = "your-api-key-here"
    } else {
        $script:GROQ_API_KEY = $GROQ_API_KEY
    }

    Write-Status "Namespace and secrets configured!"
}

# Deploy with Helm
function Deploy-HelmChart {
    Write-Status "Deploying with Helm..."

    # Lint the chart first
    helm lint $CHART_PATH

    # Install or upgrade the release
    helm upgrade --install $RELEASE_NAME $CHART_PATH `
        --namespace $NAMESPACE `
        --set backend.secrets.databaseUrl="$script:DATABASE_URL" `
        --set backend.secrets.betterAuthSecret="$script:BETTER_AUTH_SECRET" `
        --set backend.secrets.groqApiKey="$script:GROQ_API_KEY" `
        --wait `
        --timeout 5m

    Write-Status "Helm deployment successful!"
}

# Verify deployment
function Test-Deployment {
    Write-Status "Verifying deployment..."

    Write-Host ""
    Write-Host "Pods:" -ForegroundColor Blue
    kubectl get pods -n $NAMESPACE

    Write-Host ""
    Write-Host "Services:" -ForegroundColor Blue
    kubectl get svc -n $NAMESPACE

    Write-Host ""
    Write-Host "Ingress:" -ForegroundColor Blue
    kubectl get ingress -n $NAMESPACE

    Write-Host ""
    Write-Host "HPA:" -ForegroundColor Blue
    kubectl get hpa -n $NAMESPACE

    Write-Status "Deployment verified!"
}

# Print access instructions
function Show-AccessInfo {
    $minikubeIP = minikube ip

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  Deployment Complete!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Minikube IP: $minikubeIP"
    Write-Host ""
    Write-Host "To access the application:"
    Write-Host "  1. Add to C:\Windows\System32\drivers\etc\hosts:"
    Write-Host "     $minikubeIP qtodo.local"
    Write-Host "  2. Or run: minikube tunnel"
    Write-Host ""
    Write-Host "Access URLs:"
    Write-Host "  Frontend: http://qtodo.local"
    Write-Host "  Backend:  http://qtodo.local/api"
    Write-Host ""
    Write-Host "Dashboard: minikube dashboard"
    Write-Host ""
}

# Main execution
function Main {
    Test-Prerequisites
    Start-MinikubeCluster
    Build-DockerImages
    Initialize-Namespace
    Deploy-HelmChart
    Test-Deployment
    Show-AccessInfo
}

# Run main function
Main
