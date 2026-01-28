import json
import os
import boto3
from botocore.exceptions import ClientError

class ClaimsService:
    def __init__(self, config):
        self.config = config
        if not config.is_local():
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=config.aws_region,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key
            )
            self.table = self.dynamodb.Table(config.dynamodb_table_name)
        else:
            self._load_mock_data()
    
    def _load_mock_data(self):
        mock_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'mocks', 'claims.json')
        with open(mock_file_path, 'r') as f:
            data = json.load(f)
            self.mock_claims = {claim['id']: claim for claim in data['claims']}
    
    def get_claim(self, claim_id):
        if self.config.is_local():
            return self.mock_claims.get(claim_id)
        
        try:
            response = self.table.get_item(Key={'id': claim_id})
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"DynamoDB error: {e.response['Error']['Message']}")