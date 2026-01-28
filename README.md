# Claims API

A Flask-based REST API for managing insurance claims with DynamoDB integration.

## Features

- GET /claims/{id} - Retrieve claim information
- Local development with mock data
- AWS DynamoDB integration for production
- Docker support

## Local Development

### Prerequisites
- Python 3.9+
- pip

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (optional for local):
```bash
copy .env.example .env
```

3. Run the application:
```bash
python -m src.app
```

Or alternatively:
```bash
set PYTHONPATH=%cd%
python src/app.py
```

The API will be available at http://localhost:5000

### Testing

Run tests using pytest:
```bash
pytest tests/
```

## Docker

### Build and run:
```bash
docker build -t claims-api .
docker run -p 5000:5000 claims-api
```

## API Endpoints

### GET /claims/{id}
Returns claim information for the specified ID.

**Response:**
```json
{
  "id": "CLM-2024-001",
  "status": "open",
  "policyNumber": "POL-123456",
  "claimType": "auto",
  "dateReported": "2024-01-15T10:30:00Z",
  "estimatedAmount": 5500.00
}
```

## Configuration

- `ENVIRONMENT=local` - Uses mock data from mocks/claims.json
- `ENVIRONMENT=production` - Uses AWS DynamoDB
- `AWS_REGION` - AWS region for DynamoDB
- `DYNAMODB_TABLE_NAME` - DynamoDB table name
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key

## AWS Deployment

### Deploy CodeDeploy for EKS:
```bash
aws cloudformation deploy --template-file iac/codedeploy-eks.yaml --stack-name claims-api-codedeploy --capabilities CAPABILITY_NAMED_IAM --parameter-overrides EKSClusterName=introspect-2-cluster
```

### Deploy full CI/CD pipeline:
```bash
aws cloudformation deploy --template-file iac/codebuild-codedeploy.yaml --stack-name claims-api-pipeline --capabilities CAPABILITY_NAMED_IAM --parameter-overrides EKSClusterName=introspect-2-cluster
```