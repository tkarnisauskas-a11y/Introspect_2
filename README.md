# Claims API

A Flask-based REST API for managing insurance claims with DynamoDB integration.

## Features

- GET /claims/{id} - Retrieve claim information
- POST /claims/{id}/summarize - Generate AI summary of claim notes
- Local development with mock data
- AWS DynamoDB integration for production
- AWS Bedrock integration for AI summaries
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

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

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

### POST /claims/{id}/summarize
Generates AI-powered summary of claim notes using AWS Bedrock.

**Response:**
```json
{
  "claimId": "CLM-2024-001",
  "overallSummary": "Summary of all claim activities...",
  "customerSummary": "Customer-facing summary...",
  "adjusterSummary": "Internal adjuster summary...",
  "nextStep": "Recommended next action..."
}
```

## Configuration

- `ENVIRONMENT=local` - Uses mock data from mocks/claims.json and mocks/notes.json
- `ENVIRONMENT=production` - Uses AWS DynamoDB, S3, and Bedrock
- `AWS_REGION` - AWS region (default: us-east-1)
- `DYNAMODB_TABLE_NAME` - DynamoDB table name for claims
- `S3_BUCKET_NAME` - S3 bucket name for claim notes
- `BEDROCK_MODEL_ID` - Bedrock model ID for AI summaries (default: anthropic.claude-3-sonnet-20240229-v1:0)
- `AWS_ACCESS_KEY_ID` - AWS access key (not needed with IAM roles)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (not needed with IAM roles)

## AWS Deployment

See [iac/README.md](iac/README.md) for complete AWS infrastructure deployment instructions.