import unittest
from unittest.mock import patch
from app import get_secret


####  AWS - Configuration #### 
AWS_SECRET_NAME='slack-ka-bot-secrets'
AWS_REGION_NAME='us-gov-west-1'

class TestGetSecretFunction(unittest.TestCase):

    @patch('app.os.getenv')
    @patch('app.boto3.client')
    def test_get_secret_with_default_values(self, mock_boto3_client, mock_os_getenv):
        # Mock environment variables
        mock_os_getenv.side_effect = lambda x: {'AWS_SECRET_NAME': AWS_SECRET_NAME, 'AWS_REGION_NAME': AWS_REGION_NAME}.get(x)

        # Mock boto3 client
        mock_client = mock_boto3_client.return_value
        mock_client.get_secret_value.return_value = {'SecretString': '{"key": "value"}'}

        # Call the function with default values from environment variables
        secret_data = get_secret()

        # Assert that the function returns the expected secret data
        self.assertEqual(secret_data, '{"key": "value"}')

        # Assert that os.getenv was called with the correct environment variable names
        mock_os_getenv.assert_any_call(AWS_SECRET_NAME)
        mock_os_getenv.assert_any_call(AWS_REGION_NAME)

        # Assert that boto3 client was called with the correct parameters
        mock_boto3_client.assert_called_once_with(service_name='secretsmanager', region_name=AWS_REGION_NAME)

        # Assert that get_secret_value was called with the correct parameters
        mock_client.get_secret_value.assert_called_once_with(SecretId='slack-ka-bot-secrets')

if __name__ == '__main__':
    unittest.main()
