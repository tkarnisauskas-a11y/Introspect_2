# Infrastructure as Code (IaC)

CloudFormation templates for deploying AWS resources for the Introspect2 Claims API.

## Prerequisites

- AWS CLI configured with appropriate permissions
- PowerShell (for Windows deployment scripts)
- IAM permissions for EKS, DynamoDB, S3, VPC, API Gateway, CodeBuild, and CodeDeploy resources

## Deployment Order

Deploy stacks in this order due to dependencies:

### 1. VPC and Networking
Deploy VPC with public and private subnets:

```cmd
aws cloudformation create-stack --stack-name claims-vpc --template-body file://iac\vpc.yaml
```

### 2. Storage Resources
Deploy DynamoDB table and S3 bucket:

```cmd
aws cloudformation create-stack --stack-name claims-storage --template-body file://iac\claims-storage.yaml
```

### 3. EKS Cluster
Deploy the EKS cluster using existing VPC:

```cmd
aws cloudformation create-stack --stack-name introspect-2-cluster --template-body file://iac\eks-cluster.yaml --capabilities CAPABILITY_IAM
```

### 4. Setup Network Load Balancer in EKS

After EKS cluster is ready, deploy NLB service only (application will be deployed via CI/CD):

```cmd
# Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name introspect-2-cluster

# Deploy NLB service only
kubectl apply -f k8s\nlb-service.yaml

# Get NLB ARN (wait for NLB to be provisioned)
kubectl get svc claims-api-nlb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

### 5. CI/CD Pipeline
Deploy CodeBuild and CodeDeploy for automated builds and deployments:

**Option A - Complete CI/CD Pipeline (Recommended):**
```cmd
aws cloudformation create-stack --stack-name introspect2-cicd --template-body file://iac\codebuild-codedeploy.yaml --parameters ParameterKey=GitHubRepo,ParameterValue=https://github.com/tkarnisauskas-a11y/Introspect_2.git ParameterKey=UsePublicRepo,ParameterValue=true --capabilities CAPABILITY_NAMED_IAM
```

**Option B - Standalone CodeDeploy only:**
```cmd
aws cloudformation create-stack --stack-name claims-api-codedeploy --template-body file://iac\codedeploy-eks.yaml --capabilities CAPABILITY_NAMED_IAM --parameters ParameterKey=EKSClusterName,ParameterValue=introspect-2-cluster
```

### 6. API Gateway with VPC Link
Deploy API Gateway using the NLB ARN:

```cmd
aws cloudformation create-stack --stack-name claims-api-gateway --template-body file://iac\api-gateway.yaml --parameters ParameterKey=LoadBalancerArn,ParameterValue=<NLB_ARN>
```

**Note**: Application deployment is handled automatically by the CI/CD pipeline when code is pushed to the GitHub repository.

## CI/CD Pipeline Components

**CodeBuild**: 
- Builds Docker image from source
- Runs tests with pytest
- Pushes image to ECR
- Creates deployment artifacts

**CodeDeploy**:
- Deployed via CloudFormation templates
- Uses Server platform (not native EKS support)
- Custom deployment scripts for Kubernetes
- AllAtOnce deployment strategy for simplicity

**CloudFormation Templates**:
- `iac/codebuild-codedeploy.yaml` - Complete CI/CD pipeline with CodeBuild + CodeDeploy
- `iac/codedeploy-eks.yaml` - Standalone CodeDeploy for manual deployments
- Uses Server platform with custom scripts for Kubernetes deployment
- Auto-generated resource names to avoid conflicts

## Check Deployment Status

```cmd
aws cloudformation describe-stacks --stack-name claims-vpc
aws cloudformation describe-stacks --stack-name claims-storage
aws cloudformation describe-stacks --stack-name introspect-2-cluster
aws cloudformation describe-stacks --stack-name claims-api-gateway
aws cloudformation describe-stacks --stack-name introspect2-cicd
```

## Clean Up

Delete stacks in reverse order:

```cmd
aws cloudformation delete-stack --stack-name introspect2-cicd
aws cloudformation delete-stack --stack-name claims-api-gateway
aws cloudformation delete-stack --stack-name introspect-2-cluster
aws cloudformation delete-stack --stack-name claims-storage
aws cloudformation delete-stack --stack-name claims-vpc
```

## Stack Outputs

- **claims-vpc**: VPC ID, Public/Private subnet IDs
- **claims-storage**: DynamoDB table name, S3 bucket name
- **introspect-2-cluster**: EKS cluster name, cluster endpoint
- **claims-api-gateway**: API Gateway URL, VPC Link ID
- **introspect2-cicd**: ECR repository URI, S3 bucket, CodeBuild/CodeDeploy names