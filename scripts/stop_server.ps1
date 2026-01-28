$ErrorActionPreference = "Stop"

Write-Host "Stopping previous application version..."

# Scale down deployment to 0 replicas for graceful shutdown
try {
    kubectl scale deployment claims-api --replicas=0
} catch {
    Write-Host "Deployment scaling failed, continuing..."
}

# Wait for pods to terminate
try {
    kubectl wait --for=delete pod -l app=claims-api --timeout=120s
} catch {
    Write-Host "Pod deletion wait timed out, continuing..."
}

Write-Host "Application stopped successfully"