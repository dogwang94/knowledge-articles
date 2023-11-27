import unittest
from unittest.mock import patch
from app.aws_util import AWSUtil

class TestAWSUtil(unittest.TestCase):
    @patch('os.getenv')
    @patch('app.aws_util.boto3')
    def test_load_db_credentials_for_local_environment(self, mock_boto3, mock_getenv):
        # Set environment variables for the test case
        mock_getenv.side_effect = lambda x, default=None: {
            'TEST_ENV': 'local',
            'DB_NAME': 'local_db',
            'DB_USER': 'local_user',
            'DB_PWD': 'local_password',
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'SECRET_NAME': 'your_secret_name_here'
        }.get(x, default)  # Note: Updated lambda function to return correct values
        
        # Mock the boto3 client and its get_secret_value method
        mock_client_instance = mock_boto3.session.Session.return_value.client.return_value
        mock_client_instance.get_secret_value.return_value = {
            'SecretString': '{"DB_NAME": "local_db", "DB_USER": "local_user", "DB_PWD": "local_password", "DB_HOST": "localhost", "DB_PORT": "5432"}'
        }

        # Create an instance of the AWSUtil class
        util = AWSUtil()

        # Call the load_db_credentials method and get the database credentials
        db_name, db_user, db_password, db_host, db_port = util.load_db_credentials()

        # Assert that the database credentials match the expected values
        self.assertEqual(db_name, 'local_db')
        self.assertEqual(db_user, 'local_user')
        self.assertEqual(db_password, 'local_password')
        self.assertEqual(db_host, 'localhost')
        self.assertEqual(db_port, '5432')

        
    @patch('app.aws_util.boto3')
    @patch('app.aws_util.AWSUtil.get_secret')
    @patch('app.aws_util.os.getenv')
    def test_load_db_credentials_not_local_dev(self, mock_getenv, mock_get_secret, mock_boto3):
        # Set environment variables for the test case
        mock_getenv.side_effect = lambda x, default=None: {
            'TEST_ENV': 'not_local',
            'DB_NAME': 'not_local_db',
            'DB_USER': 'not_local_user',
            'DB_PWD': 'not_local_password',
            'DB_HOST': 'remote_host',
            'DB_PORT': '5432',
            'SECRET_NAME': 'default_secret_name',
            'AWS_REGION_NAME': 'us-west-1'
        }.get(x, default)

        #Mock the get_secret method to return the expected secret string
        mock_get_secret.return_value = '{"DB_NAME": "not_local_db", "DB_USER": "not_local_user", "DB_PWD": "not_local_password", "DB_HOST": "remote_host", "DB_PORT": "5432"}'

        # Mock the boto3 client and its get_secret_value method
        mock_client_instance = mock_boto3.session.Session.return_value.client
        mock_client_instance.return_value.get_secret_value.return_value = {
                'SecretString': '{"DB_NAME": "not_local_db", "DB_USER": "not_local_user", "DB_PWD": "not_local_password", "DB_HOST": "remote_host", "DB_PORT": "5432"}'
        }
        
        # Create an instance of the AWSUtil class
        util = AWSUtil()

        # Call the load_db_credentials method and get the database credentials
        db_name, db_user, db_password, db_host, db_port = util.load_db_credentials()

        # Assert that the database credentials match the expected values
        self.assertEqual(db_name, 'not_local_db')
        self.assertEqual(db_user, 'not_local_user')
        self.assertEqual(db_password, 'not_local_password')
        self.assertEqual(db_host, 'remote_host')
        self.assertEqual(db_port, '5432')
    
    
    @patch('app.aws_util.boto3')
    @patch('app.aws_util.os.getenv')
    def test_load_jira_credentials_for_local_environment(self, mock_getenv, mock_boto3):
        # Set environment variables for the test case
        mock_getenv.side_effect = lambda x, default=None: {
            'TEST_ENV': 'local',
            'JIRA_BASE_URL': 'http://localhost:8080',
            'JIRA_API_TOKEN': 'your_api_token_here',
            'JIRA_SERVICE_DESK_ID_DEV': 'dev_service_desk_id',
            'JIRA_REQUEST_TYPE_ID_DEV': 'dev_request_type_id',
            'JIRA_SERVICE_DESK_ID': 'service_desk_id',
            'JIRA_REQUEST_TYPE_ID': 'request_type_id'
        }.get(x, default)

        # Mock the boto3 client and its get_secret_value method
        mock_client_instance = mock_boto3.session.Session.return_value.client.return_value
        mock_client_instance.get_secret_value.return_value = {
            'SecretString': '{"JIRA_BASE_URL": "http://localhost:8080", "JIRA_API_TOKEN": "your_api_token_here", "JIRA_SERVICE_DESK_ID_DEV": "dev_service_desk_id", "JIRA_REQUEST_TYPE_ID_DEV": "dev_request_type_id", "JIRA_SERVICE_DESK_ID": "service_desk_id", "JIRA_REQUEST_TYPE_ID": "request_type_id"}'
        }

        # Create an instance of the AWSUtil class
        util = AWSUtil()

        # Call the load_jira_credentials method and get the Jira credentials
        jira_base_url, jira_api_token, jira_service_desk_id, jira_request_type_id = util.load_jira_credentials()

        # Assert that the Jira credentials match the expected values
        self.assertEqual(jira_base_url, 'http://localhost:8080')
        self.assertEqual(jira_api_token, 'your_api_token_here')
        self.assertEqual(jira_service_desk_id, 'dev_service_desk_id')
        self.assertEqual(jira_request_type_id, 'dev_request_type_id')

    
    @patch('app.aws_util.boto3')
    @patch('app.aws_util.AWSUtil.get_secret')
    @patch('app.aws_util.os.getenv')
    def test_load_jira_credentials_not_local_dev(self, mock_getenv, mock_get_secret, mock_boto3):
        # Set environment variables for the test case
        mock_getenv.side_effect = {
            'TEST_ENV': 'not_local',
            'SERVER_TYPE': 'DEV',
            'JIRA_BASE_URL': 'http://dev-jira.com',
            'JIRA_API_TOKEN': 'dev_api_token',
            'JIRA_SERVICE_DESK_ID_DEV': 'dev_service_desk_id',
            'JIRA_REQUEST_TYPE_ID_DEV': 'dev_request_type_id',
            'JIRA_SERVICE_DESK_ID': 'service_desk_id',
            'JIRA_REQUEST_TYPE_ID': 'request_type_id'
        }.get

        # Mock the get_secret method to return the expected secret string
        mock_get_secret.return_value = '{"JIRA_BASE_URL": "http://dev-jira.com", "JIRA_API_TOKEN": "dev_api_token", "JIRA_SERVICE_DESK_ID_DEV": "dev_service_desk_id", "JIRA_REQUEST_TYPE_ID_DEV": "dev_request_type_id", "JIRA_SERVICE_DESK_ID": "service_desk_id", "JIRA_REQUEST_TYPE_ID": "request_type_id"}'

        # Mock the boto3 client and its get_secret_value method
        mock_client_instance = mock_boto3.session.Session.return_value.client
        mock_client_instance.return_value.get_secret_value.return_value = {
            'SecretString': '{"JIRA_BASE_URL": "http://dev-jira.com", "JIRA_API_TOKEN": "dev_api_token", "JIRA_SERVICE_DESK_ID_DEV": "dev_service_desk_id", "JIRA_REQUEST_TYPE_ID_DEV": "dev_request_type_id", "JIRA_SERVICE_DESK_ID": "service_desk_id", "JIRA_REQUEST_TYPE_ID": "request_type_id"}'
        }

        # Create an instance of the AWSUtil class
        util = AWSUtil()

        # Call the load_jira_credentials method and get the Jira credentials
        jira_base_url, jira_api_token, jira_service_desk_id, jira_request_type_id = util.load_jira_credentials()

        # Assert that the Jira credentials match the expected values
        self.assertEqual(jira_base_url, 'http://dev-jira.com')
        self.assertEqual(jira_api_token, 'dev_api_token')
        self.assertEqual(jira_service_desk_id, 'dev_service_desk_id')
        self.assertEqual(jira_request_type_id, 'dev_request_type_id')


    @patch('app.aws_util.boto3')
    @patch('app.aws_util.AWSUtil.get_secret')
    @patch('app.aws_util.os.getenv')
    def test_load_jira_credentials_not_local_prod(self, mock_getenv, mock_get_secret, mock_boto3):
        mock_getenv.side_effect = lambda x, default=None: {
            'TEST_ENV': 'not_local',
            'JIRA_BASE_URL': 'http://prod-jira.com',
            'JIRA_API_TOKEN': 'api_token',
            'JIRA_SERVICE_DESK_ID_DEV': 'dev_service_desk_id',
            'JIRA_REQUEST_TYPE_ID_DEV': 'dev_request_type_id',
            'JIRA_SERVICE_DESK_ID': 'service_desk_id',
            'JIRA_REQUEST_TYPE_ID': 'request_type_id'
        }.get(x, default)

        # Mock the get_secret method to return the expected secret string
        mock_get_secret.return_value = '{"JIRA_BASE_URL": "http://prod-jira.com", "JIRA_API_TOKEN": "api_token", "JIRA_SERVICE_DESK_ID_DEV": "dev_service_desk_id", "JIRA_REQUEST_TYPE_ID_DEV": "dev_request_type_id", "JIRA_SERVICE_DESK_ID": "service_desk_id", "JIRA_REQUEST_TYPE_ID": "request_type_id"}'

        # Mock the boto3 client and its get_secret_value method
        mock_client_instance = mock_boto3.session.Session.return_value.client
        mock_client_instance.return_value.get_secret_value.return_value = {
            'SecretString': '{"JIRA_BASE_URL": "http://prod-jira.com", "JIRA_API_TOKEN": "api_token", "JIRA_SERVICE_DESK_ID_DEV": "dev_service_desk_id", "JIRA_REQUEST_TYPE_ID_DEV": "dev_request_type_id", "JIRA_SERVICE_DESK_ID": "service_desk_id", "JIRA_REQUEST_TYPE_ID": "request_type_id"}'
        }

        # Create an instance of the AWSUtil class
        util = AWSUtil()

        # Call the load_jira_credentials method and get the Jira credentials
        jira_base_url, jira_api_token, jira_service_desk_id, jira_request_type_id = util.load_jira_credentials()

        # Assert that the Jira credentials match the expected values
        self.assertEqual(jira_base_url, 'http://prod-jira.com')
        self.assertEqual(jira_api_token, 'api_token')
        self.assertEqual(jira_service_desk_id, 'service_desk_id')
        self.assertEqual(jira_request_type_id, 'request_type_id')


if __name__ == '__main__':
    unittest.main()
    # python -m unittest test.test_aws_util


