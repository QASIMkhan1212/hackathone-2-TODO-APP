#!/bin/bash
# ============================================
# Q.TODO App - Kubernetes Deployment Script
# ============================================
# This script deploys the Q.TODO application to Minikube
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="qtodo"
RELEASE_NAME="qtodo"
CHART_PATH="./helm/qtodo"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Q.TODO App - Kubernetes Deployment${NC}"
echo -e "${BLUE}============================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi

    # Check Minikube
    if ! command -v minikube &> /dev/null; then
        print_error "Minikube is not installed"
        exit 1
    fi

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        exit 1
    fi

    # Check Helm
    if ! command -v helm &> /dev/null; then
        print_error "Helm is not installed"
        exit 1
    fi

    print_status "All prerequisites satisfied!"
}

# Start Minikube
start_minikube() {
    print_status "Starting Minikube..."

    if minikube status | grep -q "Running"; then
        print_status "Minikube is already running"
    else
        minikube start --cpus=4 --memory=8192 --driver=docker
    fi

    # Enable addons
    print_status "Enabling Minikube addons..."
    minikube addons enable ingress
    minikube addons enable metrics-server

    print_status "Minikube is ready!"
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."

    # Set Docker environment to Minikube
    eval $(minikube docker-env)

    # Build frontend
    print_status "Building frontend image..."
    docker build -t qtodo-frontend:latest ./frontend \
        --build-arg NEXT_PUBLIC_API_URL=http://qtodo-backend:8000 \
        --build-arg NEXT_PUBLIC_APP_URL=http://localhost:3000

    # Build backend
    print_status "Building backend image..."
    docker build -t qtodo-backend:latest ./backend

    print_status "Docker images built successfully!"
}

# Create namespace and secrets
setup_namespace() {
    print_status "Setting up namespace and secrets..."

    # Create namespace if it doesn't exist
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

    # Check for environment variables
    if [ -z "$DATABASE_URL" ]; then
        print_warning "DATABASE_URL is not set. Using placeholder."
        DATABASE_URL="postgresql://user:pass@localhost:5432/db"
    fi

    if [ -z "$BETTER_AUTH_SECRET" ]; then
        print_warning "BETTER_AUTH_SECRET is not set. Using placeholder."
        BETTER_AUTH_SECRET="your-secret-here"
    fi

    if [ -z "$GROQ_API_KEY" ]; then
        print_warning "GROQ_API_KEY is not set. Using placeholder."
        GROQ_API_KEY="your-api-key-here"
    fi

    print_status "Namespace and secrets configured!"
}

# Deploy with Helm
deploy_helm() {
    print_status "Deploying with Helm..."

    # Lint the chart first
    helm lint $CHART_PATH

    # Install or upgrade the release
    helm upgrade --install $RELEASE_NAME $CHART_PATH \
        --namespace $NAMESPACE \
        --set backend.secrets.databaseUrl="$DATABASE_URL" \
        --set backend.secrets.betterAuthSecret="$BETTER_AUTH_SECRET" \
        --set backend.secrets.groqApiKey="$GROQ_API_KEY" \
        --wait \
        --timeout 5m

    print_status "Helm deployment successful!"
}

# Verify deployment
verify_deployment() {
    print_status "Verifying deployment..."

    echo ""
    echo -e "${BLUE}Pods:${NC}"
    kubectl get pods -n $NAMESPACE

    echo ""
    echo -e "${BLUE}Services:${NC}"
    kubectl get svc -n $NAMESPACE

    echo ""
    echo -e "${BLUE}Ingress:${NC}"
    kubectl get ingress -n $NAMESPACE

    echo ""
    echo -e "${BLUE}HPA:${NC}"
    kubectl get hpa -n $NAMESPACE

    print_status "Deployment verified!"
}

# Print access instructions
print_access_info() {
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  Deployment Complete!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "Minikube IP: $(minikube ip)"
    echo ""
    echo -e "To access the application:"
    echo -e "  1. Add to /etc/hosts: $(minikube ip) qtodo.local"
    echo -e "  2. Or run: minikube tunnel"
    echo ""
    echo -e "Access URLs:"
    echo -e "  Frontend: http://qtodo.local"
    echo -e "  Backend:  http://qtodo.local/api"
    echo ""
    echo -e "Dashboard: minikube dashboard"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    start_minikube
    build_images
    setup_namespace
    deploy_helm
    verify_deployment
    print_access_info
}

# Run main function
main "$@"
