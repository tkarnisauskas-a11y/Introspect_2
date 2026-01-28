import os

class Config:
    def __init__(self):
        self.environment = os.getenv('ENVIRONMENT', 'local')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        self.dynamodb_table_name = os.getenv('DYNAMODB_TABLE_NAME', 'claims')
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
    def is_local(self):
        return self.environment == 'local'