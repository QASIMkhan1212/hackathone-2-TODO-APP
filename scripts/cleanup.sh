#!/bin/bash
# ============================================
# Q.TODO App - Cleanup Script
# ============================================

set -e

NAMESPACE="qtodo"
RELEASE_NAME="qtodo"

echo "============================================"
echo "  Q.TODO App - Cleanup"
echo "============================================"

# Uninstall Helm release
echo "[INFO] Uninstalling Helm release..."
helm uninstall $RELEASE_NAME -n $NAMESPACE 2>/dev/null || echo "[WARN] Release not found"

# Delete namespace
echo "[INFO] Deleting namespace..."
kubectl delete namespace $NAMESPACE 2>/dev/null || echo "[WARN] Namespace not found"

# Optionally delete Docker images
read -p "Delete Docker images? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "[INFO] Deleting Docker images..."
    eval $(minikube docker-env)
    docker rmi qtodo-frontend:latest 2>/dev/null || true
    docker rmi qtodo-backend:latest 2>/dev/null || true
fi

echo "[INFO] Cleanup complete!"
