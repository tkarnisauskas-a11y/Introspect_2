#!/bin/bash
set -e

echo "Deploying Claims API to EKS..."

# Get S3 bucket name from CloudFormation
S3_BUCKET=$(aws cloudformation describe-stacks --stack-name introspect2-cicd --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' --output text)

# Download updated Kubernetes manifests from CodeBuild
echo "Downloading updated manifests from S3..."
aws s3 sync s3://$S3_BUCKET/introspect2-claims-build/k8s/ ./k8s-updated/

# Configure kubectl for EKS
echo "Configuring kubectl..."
aws eks update-kubeconfig --region us-east-1 --name introspect-2-cluster

# Deploy to EKS
echo "Applying Kubernetes manifests..."
kubectl apply -f ./k8s-updated/deployment.yaml
kubectl apply -f ./k8s-updated/service.yaml

# Wait for deployment to complete
echo "Waiting for deployment to complete..."
kubectl rollout status deployment/claims-api --timeout=300s

# Show deployment status
echo "Deployment completed successfully!"
kubectl get pods -l app=claims-api
kubectl get svc claims-api-service

echo "Claims API deployed to EKS cluster"