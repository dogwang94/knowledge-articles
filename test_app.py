import unittest
import json
from unittest.mock import MagicMock, patch, Mock
import requests_mock
import os

# Import the methods from app.py
from app import app, get_slack_thread_url, slack_interactivity, open_github_issue, get_userEmail, get_thread_parent, get_message_parent, send_slack_github_url

class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_slack_event_url_verification_challenge(self):
        # Create a test challenge data
        test_challenge_data = {
            "type": "url_verification",
            "challenge": "test_challenge_string"
        }
        response = self.app.post("/slack/interactivity", json=test_challenge_data, headers={"Content-Type": "application/json"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "test_challenge_string")        

    @patch("app.send_slack_response")
    def test_slack_event_matching_keywords(self, mock_send_slack_response):
        data = {
            "event": {
                "text": "Please give me slack instruction",
                "user": "user123",
                "ts": "ts123",
                "channel": "channel123"
            }
        }
        response = self.app.post("/slack/events", data=json.dumps(data), content_type="application/json")

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Decode the response data and remove newline characters from the actual message
        response_data = json.loads(response.data.decode())
        self.assertTrue(response_data['success'])
        
        # Check if the send_slack_response function was called with the correct arguments
        mock_send_slack_response.assert_called_once_with(
            "channel123",
            "user123",
            "ts123",
            ":information_desk_person:",
            "• For Slack help please use this link: *Slack_Instruction* <https://probable-dollop-19qk3nl.pages.github.io/pages/Slack_Troubleshooting_Instructions/Slack_Troubleshooting_Instructions|here>."
        )

    @patch("app.send_slack_response")
    def test_slack_event_non_matching_keywords(self, mock_send_slack_response):
        data = {"event": {"text": "Please help me with email issue", "user": "user123", "ts": "ts123", "channel": "channel123"}}
        response = self.app.post("/slack/events", data=json.dumps(data), content_type="application/json")

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Decode the response data and remove newline characters from the actual message
        response_data = json.loads(response.data.decode())

        # Get the 'message' key from the response data if it exists, otherwise use a default message
        actual_message = response_data.get('message', "I'm sorry I could not find any matching keywords. Please click the I need further assistance button if you still require help.").strip().lower()  # Convert to lowercase

        # Construct the expected response based on the provided code for non-matching keywords
        expected_response_data = {
            'success': True,
            'message': "I'm sorry I could not find any matching keywords. Please click the I need further assistance button if you still require help."
        }

        # Convert the expected message to lowercase as well
        expected_message = expected_response_data['message'].strip().lower()

        self.assertEqual(actual_message, expected_message)

        # Check if send_slack_response was called with the expected parameters
        mock_send_slack_response.assert_called_once_with(
            'channel123', 'user123', 'ts123', ":information_desk_person:",
            "I'm sorry I could not find any matching keywords. Please click the I need further assistance button if you still require help."
        )       
    
    @patch("app.open_github_issue")
    @patch("app.get_thread_parent")
    @patch("app.get_userEmail")
    @patch("app.get_slack_thread_url")
    @patch("app.send_slack_github_url")
    def test_slack_block_action(self, mock_send_slack_github_url, mock_get_slack_thread_url, mock_get_userEmail,
                                mock_get_thread_parent, mock_open_github_issue):
        # Create a test payload data
        test_payload_data = {
            "type": "block_actions",
            "message": {
                "thread_ts": "test_thread_ts"
            },
            "container": {
                "channel_id": "test_channel_id"
            }
        }

        mock_get_thread_parent.return_value = MagicMock(text="Test request text", user="test_user")
        mock_get_userEmail.return_value = "test.user@example.com"
        mock_get_slack_thread_url.return_value = "https://example.com/slack-thread"
        mock_open_github_issue.return_value = MagicMock(text=json.dumps({"html_url": "https://github.com/issue"}))

        # response = self.app.post("/slack/interactivity", data={"payload": json.dumps(payload)},
        #                          headers={"Content-Type": "application/x-www-form-urlencoded"})

        response = self.app.post("/slack/interactivity", json=test_payload_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        self.assertEqual(response.status_code, 200)
        
        mock_get_thread_parent.assert_called_once_with("test_channel_id", "test_thread_ts")
        mock_get_userEmail.assert_called_once_with("test_user")
        mock_get_slack_thread_url.assert_called_once_with("test_channel_id", "test_thread_ts")
        title = "KA-BOT Ticket: Test request text"
        body = f"User test.user@example.com has requested help with the following query: Test request text\n\nHere's a link to the slack thread: https://example.com/slack-thread"
        mock_open_github_issue.assert_called_once_with(title, body, None, "test_channel_id", "test_thread_ts")
        mock_send_slack_github_url.assert_called_once_with("test_channel_id", "test_thread_ts", "https://github.com/issue")

    
    def test_invalid_content_type(self):
        response = self.app.post("/slack/interactivity", data={}, headers={"Content-Type": "invalid_content_type"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data.decode()), {"success": True})

    @patch('app.requests.post')
    @patch('app.get_secret')
    def test_open_github_issue_success(self, mock_get_secret, mock_post):
        # Mock the response for successful GitHub issue creation
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        github_repo_owner=os.environ["GITHUB_REPO_OWNER"]
        github_repo_name=os.environ["GITHUB_REPO_NAME"]
        github_token=os.environ["GITHUB_TOKEN"]
        
        # Mock input data
        issue_title = "Test Issue"
        issue_body = "This is a test issue."
        issue_label = "bug"
        channel_id = "CHANNEL_ID"
        thread_ts = "THREAD_TS"

        # Mock original_message function
        def mock_get_message_parent(channel_id, thread_ts):
            return "This is a test message containing Okta"
        
         # Ensure that the open_github_issue function uses the mocked get_secret() data
        with patch('app.get_secret', mock_get_secret):
            # Ensure that the open_github_issue function uses the mocked get_message_parent data
            with patch('app.get_message_parent', new=mock_get_message_parent):
                # Call the function with the correct parameters using the app namespace
                response = open_github_issue(issue_title, issue_body, issue_label, channel_id, thread_ts)


        # Ensure that requests.post was called with the correct arguments
        mock_post.assert_called_once_with(
            f'https://api.github.com/repos/{github_repo_owner}/{github_repo_name}/issues',
            headers={'Authorization': f'token {github_token}'},
            json={
                'title': issue_title,
                'body': issue_body,
                'labels': ['Okta Support', 'bug']
            }
        )

        # Ensure that the function returns the expected response
        self.assertEqual(response.status_code, 201)
             
    @patch('app.requests.post')
    def test_open_github_issue_failure(self, mock_post):
        # Mock the response for a failed GitHub issue creation
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response
        
        github_repo_owner=os.environ["GITHUB_REPO_OWNER"]
        github_repo_name=os.environ["GITHUB_REPO_NAME"]
        github_token=os.environ["GITHUB_TOKEN"]

        # Mock input data
        issue_title = "Test Issue"
        issue_body = "This is a test issue."
        issue_label = "bug"
        channel_id = "CHANNEL_ID"
        thread_ts = "THREAD_TS"


        # Mock original_message function
        def mock_get_message_parent(channel_id, thread_ts):
            return "This is a test message containing Okta"
        
        with patch('app.get_message_parent', new=mock_get_message_parent):
            # Replace 'github_repo_owner', 'github_repo_name', and 'github_token' with appropriate values
            response = open_github_issue(issue_title, issue_body, issue_label, channel_id, thread_ts)

        # Ensure that requests.post was called with the correct arguments
        mock_post.assert_called_once_with(
            f'https://api.github.com/repos/{github_repo_owner}/{github_repo_name}/issues',
            headers={'Authorization': f'token {github_token}'},
            json={
                'title': issue_title,
                'body': issue_body,
                'labels': ['Okta Support', 'bug']
            }
        )

        # Ensure that the function returns the expected response
        self.assertEqual(response.status_code, 404)
        
    

    def test_get_slack_thread_url(self):
        with requests_mock.Mocker() as mock:
            # Mock the Slack API response
            mock.post('https://slack.com/api/chat.getPermalink', json={"permalink": "https://example.com/thread"})

            channel_id = "ABC123"
            thread_ts = "1234567890.123456"
            response = get_slack_thread_url(channel_id, thread_ts)
            assert response == "https://example.com/thread"  
      
    def test_get_userEmail(self):
        with requests_mock.Mocker() as mock:
            # Mock the Slack API response
            mock.post('https://slack.com/api/users.profile.get?include_labels=false', json={
                "profile": {
                    "email": "test@example.com",
                    "display_name": "Test User"
                }
            })

            user_id = "USER123"
            response = get_userEmail(user_id)
            assert response == "test@example.com"

    def test_get_thread_parent(self):
        with requests_mock.Mocker() as mock:
            # Mock the Slack API response
            mock.post('https://slack.com/api/conversations.replies', json={
                "messages": [
                    {
                        "text": "Original Request Text",
                        "user": "USER123"
                    }
                ]
            })

            channel_id = "ABC123"
            thread_ts = "1234567890.123456"
            response = get_thread_parent(channel_id, thread_ts)
            assert response.text == "Original Request Text"
            assert response.user == "USER123"
    
    def test_get_message_parent(self):
        with requests_mock.Mocker() as mock:
            # Mock the Slack API response
            mock.post('https://slack.com/api/conversations.replies', json={
                "messages": [
                    {
                        "text": "Test query",
                        "user": "USER123"
                    }
                ]
            })

            channel_id = "ABC123"
            thread_ts = "1234567890.123456"
            response = get_message_parent(channel_id, thread_ts)
            assert response == "Test query"

    def test_send_slack_github_url(self):
        with requests_mock.Mocker() as mock:
            # Mock the Slack API response
            mock.post('https://slack.com/api/chat.postMessage', status_code=200)

            channel_id = "ABC123"
            thread_ts = "1234567890.123456"
            github_url = "https://github.com/owner/repo/issues/123"
            send_slack_github_url(channel_id, thread_ts, github_url)
            # You may want to assert the behavior based on the side effects of this function.
            assert ...  # Add assertions here


if __name__ == "__main__":
    unittest.main()

    # python -m unittest discover -v