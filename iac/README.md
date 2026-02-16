# Infrastructure as Code (IaC)

CloudFormation templates for deploying AWS resources for the Introspect2 Claims API.

## Prerequisites

- AWS CLI configured with appropriate permissions
- eksctl installed
- kubectl installed
- helm installed
- IAM permissions for EKS, DynamoDB, S3, VPC, CodeBuild resources

## Deployment Order

### 1. VPC and Networking
```cmd
aws cloudformation create-stack --stack-name claims-vpc --template-body file://iac\vpc.yaml
```

### 2. Storage Resources
```cmd
aws cloudformation create-stack --stack-name claims-storage --template-body file://iac\claims-storage.yaml
```

### 3. EKS Cluster
```cmd
aws cloudformation create-stack --stack-name introspect-2-cluster --template-body file://iac\eks-cluster.yaml --capabilities CAPABILITY_IAM
```

Install EKS addons:
```cmd
iac\install-eks-addons.bat
```

### 4. EKS Service Account IAM Role

Create IAM OIDC Provider:
```cmd
eksctl utils associate-iam-oidc-provider --cluster=introspect-2-cluster --region=us-east-1 --approve
```

Get OIDC Provider ID:
```cmd
aws eks describe-cluster --name introspect-2-cluster --query "cluster.identity.oidc.issuer" --output text
```

Update `iac\eks-irsa-simple.yaml` with the OIDC Provider ID, then create the role:
```cmd
aws cloudformation create-stack --stack-name claims-api-service-role --template-body file://iac\eks-irsa-simple.yaml --capabilities CAPABILITY_NAMED_IAM
```

### 5 CI/CD
#### Pipeline with CodeBuild
```cmd
aws cloudformation create-stack --stack-name introspect2-cicd --template-body file://pipelines\codebuild.yaml --parameters ParameterKey=GitHubRepo,ParameterValue=https://github.com/tkarnisauskas-a11y/Introspect_2 ParameterKey=UsePublicRepo,ParameterValue=true --capabilities CAPABILITY_NAMED_IAM
```

#### Automated CI/CD Pipeline

For fully automated deployments, create CodePipeline:

**Prerequisites:**
- Store GitHub token in AWS Secrets Manager:
```cmd
aws secretsmanager create-secret --name github-token --secret-string "{\"token\":\"YOUR_GITHUB_TOKEN\"}"
```

**Deploy Pipeline:**
```cmd
aws cloudformation create-stack --stack-name claims-pipeline --template-body file://pipelines\codepipeline.yaml --parameters ParameterKey=GitHubRepo,ParameterValue=https://github.com/tkarnisauskas-a11y/Introspect_2 ParameterKey=GitHubBranch,ParameterValue=main --capabilities CAPABILITY_NAMED_IAM
```

This pipeline will:
1. Monitor GitHub repository for changes
2. Trigger CodeBuild to build and push Docker image to ECR
3. Automatically deploy the new image to EKS
4. Perform rolling update with zero downtime

### 6. Deploy Application to EKS

Configure kubectl:
```cmd
aws eks update-kubeconfig --region us-east-1 --name introspect-2-cluster
```

**Initial deployment** (one-time setup):
```cmd
kubectl apply -f k8s\service-account.yaml
kubectl apply -f k8s\deployment.yaml
kubectl apply -f k8s\nlb-service.yaml
```

Check deployment:
```cmd
kubectl rollout status deployment/claims-api -n default
kubectl get pods -n default -l app=claims-api
kubectl get svc claims-api-nlb -n default
```

**Note:** If you set up CodePipeline in step 5a, subsequent deployments will be automatic on git push.

### 7. AWS Load Balancer Controller

Set environment variables:
```cmd
set AGW_AWS_REGION=us-east-1
set AGW_EKS_CLUSTER_NAME=introspect-2-cluster
```

For full setup, run:
```bash
# On Linux/Mac, use the commands in iac/load-balancer.yaml
# This installs AWS Load Balancer Controller for advanced routing
```

### 8. API Gateway with ACK Controller

Install ACK API Gateway controller:
```bash
# Set environment variables
export AGW_AWS_REGION=us-east-1
export AGW_ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
export AGW_EKS_CLUSTER_NAME=introspect-2-cluster

# Create IAM policy
aws iam create-policy --policy-name ACKIAMPolicy --policy-document file://apigw/ack-trust-policy.json

# Create service account
eksctl create iamserviceaccount \
  --attach-policy-arn=arn:aws:iam::${AGW_ACCOUNT_ID}:policy/ACKIAMPolicy \
  --cluster=$AGW_EKS_CLUSTER_NAME \
  --namespace=kube-system \
  --name=ack-apigatewayv2-controller \
  --override-existing-serviceaccounts \
  --region $AGW_AWS_REGION \
  --approve

# Install ACK controller
export SERVICE=apigatewayv2
export RELEASE_VERSION=$(curl -sL https://api.github.com/repos/aws-controllers-k8s/${SERVICE}-controller/releases/latest | jq -r '.tag_name | ltrimstr("v")')

aws ecr-public get-login-password --region us-east-1 | helm registry login --username AWS --password-stdin public.ecr.aws

helm install -n kube-system ack-$SERVICE-controller \
  oci://public.ecr.aws/aws-controllers-k8s/$SERVICE-chart \
  --version=$RELEASE_VERSION \
  --set serviceAccount.create=false \
  --set=aws.region=$AGW_AWS_REGION
```

## Architecture

- **VPC**: Public and private subnets with NAT Gateway for internet access
- **EKS**: Kubernetes cluster with managed node group (t3.medium)
- **DynamoDB**: Claims data storage
- **S3**: Claim notes storage
- **ECR**: Docker image repository
- **CodeBuild**: CI/CD pipeline for building and pushing images
- **CodePipeline**: Automated deployment pipeline (optional)
- **NLB**: Network Load Balancer for external access

## Check Deployment Status

```cmd
aws cloudformation describe-stacks --stack-name claims-vpc
aws cloudformation describe-stacks --stack-name claims-storage
aws cloudformation describe-stacks --stack-name introspect-2-cluster
aws cloudformation describe-stacks --stack-name claims-api-service-role
aws cloudformation describe-stacks --stack-name introspect2-cicd
aws cloudformation describe-stacks --stack-name claims-pipeline
```

## Clean Up

Delete resources in reverse order:

```cmd
kubectl delete -f k8s\nlb-service.yaml
kubectl delete -f k8s\deployment.yaml
kubectl delete -f k8s\service-account.yaml
aws cloudformation delete-stack --stack-name claims-pipeline
aws cloudformation delete-stack --stack-name introspect2-cicd
aws cloudformation delete-stack --stack-name claims-api-service-role
aws cloudformation delete-stack --stack-name introspect-2-cluster
aws cloudformation delete-stack --stack-name claims-storage
aws cloudformation delete-stack --stack-name claims-vpc
```