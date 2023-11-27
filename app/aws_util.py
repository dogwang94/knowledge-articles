import os
import logging
import sys
import json
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

class AWSUtil:
    def __init__(self):
        self.aws_region_name = os.environ.get('AWS_REGION_NAME', 'us-west-1')
        self.secret_name = os.environ.get('SECRET_NAME', 'default_secret_name')

    def get_secret(self):
        if os.getenv('TEST_ENV') == "local":
            secret_name = os.getenv('AWS_SECRET_NAME')
            region_name = os.getenv('AWS_REGION_NAME')
        else:
            secret_name = os.environ.get('SECRET_NAME', 'default_secret_name')
            region_name = os.environ.get('REGION_NAME', 'us-west-1')

        session = boto3.session.Session()
        
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name,
        )
        
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            raise e

        # Decrypts secret using the associated KMS key.
        secret = get_secret_value_response['SecretString']
        return secret

    def load_db_credentials(self):
        if(os.getenv('TEST_ENV') == "local"):
            db_name=os.getenv('DB_NAME')
            db_user=os.getenv('DB_USER')
            db_password=os.getenv('DB_PWD')
            db_host=os.getenv('DB_HOST')
            db_port=os.getenv('DB_PORT')
        else:
            secret_data = json.loads(self.get_secret())
            db_name = secret_data['DB_NAME']
            db_user = secret_data['DB_USER']
            db_password = secret_data['DB_PWD']
            db_host = secret_data['DB_HOST']
            db_port = secret_data['DB_PORT']
        return db_name, db_user, db_password, db_host, db_port

    def load_jira_credentials(self):
        if(os.getenv('TEST_ENV') == "local"):
            jira_base_url=os.getenv('JIRA_BASE_URL')
            jira_api_token=os.getenv('JIRA_API_TOKEN')
            jira_service_desk_id=os.getenv('JIRA_SERVICE_DESK_ID_DEV')
            jira_request_type_id=os.getenv('JIRA_REQUEST_TYPE_ID_DEV')
        else:
            secret_data = json.loads(self.get_secret())
            SERVER_TYPE = os.getenv('SERVER_TYPE')
            if SERVER_TYPE == "DEV":
                jira_service_desk_id = secret_data['JIRA_SERVICE_DESK_ID_DEV']
                jira_request_type_id = secret_data['JIRA_REQUEST_TYPE_ID_DEV']
            else:
                jira_service_desk_id = secret_data['JIRA_SERVICE_DESK_ID']
                jira_request_type_id = secret_data['JIRA_REQUEST_TYPE_ID']
            jira_base_url=secret_data['JIRA_BASE_URL']
            jira_api_token=secret_data['JIRA_API_TOKEN']
        
        return jira_base_url, jira_api_token, jira_service_desk_id, jira_request_type_id

    def get_db_and_jira_credentials(self):
        db_credentials = self.load_db_credentials()
        jira_credentials = self.load_jira_credentials()
        return db_credentials, jira_credentials

if __name__ == "__main__":
    logger.debug(f"==> in aws_util\n")
    # python -m app.aws_util
