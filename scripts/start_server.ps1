$ErrorActionPreference = "Stop"

Write-Host "Starting application deployment..."

# Read image details
$imageDetail = Get-Content "imageDetail.json" | ConvertFrom-Json
$imageUri = $imageDetail.imageUri
Write-Host "Deploying image: $imageUri"

# Apply Kubernetes manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/nlb-service.yaml

# Wait for deployment to be ready
kubectl rollout status deployment/claims-api --timeout=300s

Write-Host "Application started successfully"