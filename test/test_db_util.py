import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from app.db_util import DbUtils


class TestDbUtils(unittest.TestCase):

    def setUp(self):
        self.db_instance = DbUtils()

    @patch('app.db_util.aws_util')
    def test_get_ka_list(self, mock_aws_util):
        mock_aws_util.load_db_credentials.return_value = ('db_name', 'db_user', 'db_password', 'db_host', 'db_port')

        with patch.object(self.db_instance, 'execute_query', return_value=([{'ka1': 'content1'}, {'ka2': 'content2'}], None)):
            ka_list, error = self.db_instance.get_ka_list("github_owner", "ka_repo_name")
            self.assertIsNone(error)
            self.assertEqual(ka_list, [{'ka1': 'content1'}, {'ka2': 'content2'}])

        with patch.object(self.db_instance, 'execute_query', return_value=(None, 'Error fetching KA list')):
            ka_list, error = self.db_instance.get_ka_list("github_owner", "ka_repo_name")
            self.assertEqual(error, 'Error fetching KA list')
            self.assertIsNone(ka_list)
            

    @patch('app.db_util.aws_util')
    def test_is_user_excluded(self, mock_aws_util):
        # Mocking load_db_credentials method to return mock database credentials
        mock_aws_util.load_db_credentials.return_value = ('db_name', 'db_user', 'db_password', 'db_host', 'db_port')

        # Scenario 1: User not excluded (result set with a single row containing False)
        with patch.object(self.db_instance, 'execute_query', return_value=((False,), None)):
            is_excluded = self.db_instance.is_user_excluded("excluded_user@gmail.com")
            self.assertFalse(is_excluded)

        # Scenario 2: User excluded (result set with a single row containing True)
        with patch.object(self.db_instance, 'execute_query', return_value=([(True,)], None)):
            is_excluded = self.db_instance.is_user_excluded("excluded_user@gmail.com")
            self.assertTrue(is_excluded)

        # Scenario 3: Error occurred while checking excluded user
        with patch.object(self.db_instance, 'execute_query', return_value=(None, 'Error checking excluded user')):
            is_excluded = self.db_instance.is_user_excluded("invalid_email")
            self.assertFalse(is_excluded)

if __name__ == '__main__':
    unittest.main()
    # python -m unittest test.test_db_util    
    # python -m unittest discover -s test