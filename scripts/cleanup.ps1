# ============================================
# Q.TODO App - Cleanup Script (PowerShell)
# ============================================

$ErrorActionPreference = "Stop"

$NAMESPACE = "qtodo"
$RELEASE_NAME = "qtodo"

Write-Host "============================================" -ForegroundColor Blue
Write-Host "  Q.TODO App - Cleanup" -ForegroundColor Blue
Write-Host "============================================" -ForegroundColor Blue

# Uninstall Helm release
Write-Host "[INFO] Uninstalling Helm release..." -ForegroundColor Green
try {
    helm uninstall $RELEASE_NAME -n $NAMESPACE 2>$null
    Write-Host "[INFO] Helm release uninstalled" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Release not found or already removed" -ForegroundColor Yellow
}

# Delete namespace
Write-Host "[INFO] Deleting namespace..." -ForegroundColor Green
try {
    kubectl delete namespace $NAMESPACE 2>$null
    Write-Host "[INFO] Namespace deleted" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Namespace not found or already removed" -ForegroundColor Yellow
}

# Optionally delete Docker images
$response = Read-Host "Delete Docker images? (y/n)"
if ($response -match "^[Yy]$") {
    Write-Host "[INFO] Deleting Docker images..." -ForegroundColor Green
    & minikube -p minikube docker-env --shell powershell | Invoke-Expression
    docker rmi qtodo-frontend:latest 2>$null
    docker rmi qtodo-backend:latest 2>$null
    Write-Host "[INFO] Docker images deleted" -ForegroundColor Green
}

Write-Host "[INFO] Cleanup complete!" -ForegroundColor Green
