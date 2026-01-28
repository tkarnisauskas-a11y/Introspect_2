#!/bin/bash
set -e

echo "Building CodeDeploy artifacts..."

# Create artifacts directory
mkdir -p artifacts

# Copy required files for CodeDeploy
cp appspec.yml artifacts/
cp -r k8s/ artifacts/
cp -r scripts/ artifacts/
cp imageDetail.json artifacts/ 2>/dev/null || echo "imageDetail.json not found, skipping"

# Create deployment package
cd artifacts
zip -r ../codedeploy-package.zip .
cd ..

# Upload to S3 for CodeDeploy
aws s3 cp codedeploy-package.zip s3://$CODEDEPLOY_BUCKET/claims-api-$(date +%Y%m%d-%H%M%S).zip

echo "CodeDeploy artifacts created and uploaded to S3"