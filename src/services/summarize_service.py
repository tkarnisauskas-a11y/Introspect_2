import json
import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class SummarizeService:
    def __init__(self, config):
        self.config = config
        if not config.is_local():
            self.s3 = boto3.client('s3', region_name=config.aws_region)
            self.bedrock = boto3.client('bedrock-runtime', region_name=config.aws_region)
    
    def _get_notes_from_s3(self, claim_id):
        logger.info(f"Getting notes for claim {claim_id}, environment: {self.config.environment}")
        
        if self.config.is_local():
            import os
            mock_file = os.path.join(os.path.dirname(__file__), '..', '..', 'mocks', 'notes.json')
            logger.info(f"Reading from mock file: {mock_file}")
            with open(mock_file, 'r') as f:
                data = json.load(f)
                for note in data['notes']:
                    if note['claimId'] == claim_id:
                        logger.info(f"Found {len(note['entries'])} notes for claim {claim_id}")
                        return note['entries']
                logger.warning(f"No notes found for claim {claim_id} in mock data")
                return []
        
        try:
            key = "notes.json"
            logger.info(f"Reading from S3: bucket={self.config.s3_bucket_name}, key={key}")
            response = self.s3.get_object(Bucket=self.config.s3_bucket_name, Key=key)
            data = json.loads(response['Body'].read())
            for note in data['notes']:
                if note['claimId'] == claim_id:
                    logger.info(f"Found {len(note['entries'])} notes for claim {claim_id}")
                    return note['entries']
            logger.warning(f"No notes found for claim {claim_id} in S3")
            return []
        except ClientError as e:
            logger.error(f"S3 error for claim {claim_id}: {e}")
            return []
    
    def _invoke_bedrock(self, notes):
        notes_text = "\n\n".join([f"[{n['timestamp']}] {n['author']} ({n['type']}): {n['content']}" for n in notes])
        
        prompt = f"""Analyze these insurance claim notes and provide:
1. Overall summary
2. Customer-facing summary
3. Adjuster-focused summary
4. Recommended next step

Notes:
{notes_text}

Respond in JSON format:
{{"overallSummary": "...", "customerSummary": "...", "adjusterSummary": "...", "nextStep": "..."}}"""
        
        if self.config.is_local():
            return {
                "overallSummary": "Mock summary of claim notes",
                "customerSummary": "Mock customer-facing summary",
                "adjusterSummary": "Mock adjuster-focused summary",
                "nextStep": "Mock recommended next step"
            }
        
        logger.info(f"Invoking Bedrock model: {self.config.bedrock_model_id}")
        response = self.bedrock.converse(
            modelId=self.config.bedrock_model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 1000, "temperature": 0.7}
        )
        
        logger.info(f"Bedrock response: {json.dumps(response)[:500]}")
        content = response['output']['message']['content'][0]['text']
        logger.info(f"Extracted content: {content[:200]}")
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "overallSummary": content,
                "customerSummary": "See overall summary",
                "adjusterSummary": "See overall summary",
                "nextStep": "Review claim details"
            }
    
    def summarize_claim(self, claim_id):
        notes = self._get_notes_from_s3(claim_id)
        if not notes:
            raise Exception("No notes found for claim")
        return self._invoke_bedrock(notes)
