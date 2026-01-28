$ErrorActionPreference = "Stop"

Write-Host "Installing dependencies..."

# Install kubectl if not present
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    $kubectlVersion = (Invoke-RestMethod -Uri "https://dl.k8s.io/release/stable.txt").Trim()
    $kubectlUrl = "https://dl.k8s.io/release/$kubectlVersion/bin/windows/amd64/kubectl.exe"
    Invoke-WebRequest -Uri $kubectlUrl -OutFile "kubectl.exe"
    Move-Item "kubectl.exe" "$env:ProgramFiles\kubectl.exe"
    $env:PATH += ";$env:ProgramFiles"
}

# Configure kubectl for EKS
aws eks update-kubeconfig --region $env:AWS_DEFAULT_REGION --name $env:EKS_CLUSTER_NAME

Write-Host "Dependencies installed successfully"