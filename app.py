from flask import Flask, jsonify, request, abort
import logging
import sys
import slack_sdk
import boto3
from botocore.exceptions import ClientError
import requests
import json
from werkzeug.exceptions import HTTPException
import urllib.parse
import os

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)  # Set the desired log level

@app.errorhandler(HTTPException)
def handle_http_exception(e):
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    app.logger.error('An HTTPException occurred: %s', e)
    app.logger.error('Response: %s', str(response.data))
    return response

def get_secret():
    secret_name = "slack-ka-bot-secrets"
    region_name = "us-gov-west-1"

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
    
if(os.getenv('TEST_ENV') == "local"):
    slack_bot_token=os.getenv("SLACK_BOT_TOKEN")
    slack_signing_secret=os.getenv('SLACK_SIGNING_SECRET')
    slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL')
    github_token=os.getenv('GITHUB_TOKEN')
    github_repo_owner=os.getenv('GITHUB_REPO_OWNER')
    github_repo_name=os.getenv('GITHUB_REPO_NAME')
    github_request_url=os.getenv('GITHUB_REQUEST_URL')
    okta_request_url=os.getenv('OKTA_REQUEST_URL')
else: 
    data = json.loads(get_secret())
    slack_bot_token=data["SLACK_BOT_TOKEN"]
    slack_webhook_url=data['SLACK_WEBHOOK_URL']
    github_token=data['GITHUB_TOKEN']
    github_repo_owner=data['GITHUB_REPO_OWNER']
    github_repo_name=data['GITHUB_REPO_NAME']
    github_url = f"https://api.github.com/repos/{github_repo_owner}/{github_repo_name}/issues"
    github_request_url=data['GITHUB_REQUEST_URL']
    okta_request_url=data['OKTA_REQUEST_URL']

# Initialize the Slack API client
slack_client = slack_sdk.WebClient(token=slack_bot_token)
bot_id = slack_client.api_call("auth.test")['user_id']

class OriginalThread:
    text = ""
    user = ""

# Slack Event API endpoint
@app.route('/slack/events', methods=['POST'])
def slack_event():
    # Check the request's content type
    if request.headers.get('Content-Type') != 'application/json':
        abort(400, 'Content-Type must be application/json')
        
    # Get the request data
    request_data = request.get_json()
    
    # Check if the request is a Slack event URL verification challenge
    if "challenge" in request_data:
        return request_data["challenge"], 200

    if 'event' in request_data and 'text' in request_data['event']:
        event_text = request_data['event']['text']
        
        if 'user' in request_data['event']:
            user_id = request_data['event']['user']
            thread_ts = request_data['event'].get('thread_ts', request_data['event']['ts'])
            channel_id = request_data['event']['channel']
            
            if user_id != bot_id:
                            
                if not is_thread_responded(channel_id, thread_ts):

                    KA_List = []
                    KA_List.append({"JIRA": f"For JIRA access please request an Okta account: <{okta_request_url}|Okta Request> \nIf you are unable to request for yourself have a supervisor request for you."})
                    KA_List.append({"GITHUB": f"For Department of Veteran Affairs GitHub access please follow this link: <{github_request_url}| VA GitHub Steps>"})
                    KA_List.append({"SLACK": f"For Slack help please use this link: *Slack_Instruction* <https://probable-dollop-19qk3nl.pages.github.io/pages/Slack_Troubleshooting_Instructions/Slack_Troubleshooting_Instructions|here>."})
                    KA_List.append({"MURAL": f"For Mural Access please use this link: *Mural_Access* <https://probable-dollop-19qk3nl.pages.github.io/pages/Get_Access_to_Mural/Get_Access_to_Mural|here>."})
            
                    matching_values = [list(entry.values())[0] for entry in KA_List if list(entry.keys())[0].lower() in event_text.lower()]
                    formatted_output = "\n\n".join(f"• {value}" for value in matching_values)
                    
                    if matching_values:
                        send_slack_response(channel_id, user_id, thread_ts, ":information_desk_person:", formatted_output)
                    else:
                        send_slack_response(channel_id, user_id, thread_ts, ":information_desk_person:", "I'm sorry I could not find any matching keywords. Please click the I need further assistance button if you still require help.")
                   
    return jsonify({'success': True})

@app.route("/slack/interactivity", methods=["POST"])
def slack_interactivity():

    # Check the request's content type
    if request.headers.get('Content-Type') == 'application/json':

        # Get the request data
        request_data = request.get_json()
          
        # Check if the request is a Slack event URL verification challenge
        if "challenge" in request_data:
            return request_data["challenge"], 200

    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':

        # Get the request data
        request_data = request.get_data()
        request_decoded_data = urllib.parse.unquote(request_data)

        # Remove the payload= from the form
        request_decoded_data = request_decoded_data.strip("payload=")
        request_payload = json.loads(request_decoded_data)

        # Check if user clicked block action
        if "block_actions" in request_payload["type"]:

            thread_ts = request_payload['message']['thread_ts']
            channel_id = request_payload['container']['channel_id']
            original_request = get_thread_parent(channel_id, thread_ts)
            title = "KA-BOT Ticket: " + original_request.text
            user_email = get_userEmail(original_request.user)
            slack_thread_url = get_slack_thread_url(channel_id, thread_ts)
            body = f"User {user_email} has requested help with the following query: {original_request.text}\n\nHere's a link to the slack thread: {slack_thread_url}"

            # Create Issue in GitHub
            response = open_github_issue(title, body, None ,channel_id, thread_ts)

            # Grab the github issue from the response
            url = json.loads(response.text)

            # Sends the return github url to the slack channel
            send_slack_github_url(channel_id, thread_ts, url["html_url"])
    return jsonify({'success': True})

# Creates a new GitHub Issue
def open_github_issue(issue_title, issue_body, issue_label,channel_id, thread_ts):
    # Create a new GitHub issue
    url = f'https://api.github.com/repos/{github_repo_owner}/{github_repo_name}/issues'
    headers = {'Authorization': f'token {github_token}'}
    payload = {
        'title': issue_title,
        'body': issue_body,
        'labels': []
    }
    
    original_message = get_message_parent(channel_id, thread_ts)
    LABEL_List = [
        {"OKTA": "Okta Support"},
        {"JIRA": "Jira Support"},
        {"ACCESS": "Jira User Access"},
        {"SLACK": "Slack Support"},
        {"MURAL": "Mural"}
    ]

    matching_values = [list(entry.values())[0] for entry in LABEL_List if list(entry.keys())[0].lower() in original_message.lower()]

    for value in matching_values:
        payload["labels"].append(value)

    # Add additional specified issue_label if provided
    if issue_label:
        payload["labels"].append(issue_label)
        
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        app.logger.debug('GitHub issue created successfully.')
    else:
        app.logger.debug(f'Failed to create GitHub issue. Status code: {response.status_code}')
    return response

# Gets the thread's permalink
def get_slack_thread_url(channel_id, thread_ts):
    permalink_url = "https://slack.com/api/chat.getPermalink"
    headers = {'Authorization': f'Bearer {slack_bot_token}'}
    payload = {
        'channel': channel_id,
        'message_ts': thread_ts
        }
    response = requests.post(permalink_url, headers=headers, data=payload)
    if response.status_code == 200:
        response_json = json.loads(response.text)
        if "permalink" in response_json :
            return response_json["permalink"]
    else:
        app.logger.debug(f'Failed to get Slack permalink. Status code: {response.status_code}')

# Gets the User's email or if not found the user's account name
def get_userEmail(userid):
    userprofile_url = "https://slack.com/api/users.profile.get?include_labels=false"
    headers = {'Authorization': f'Bearer {slack_bot_token}'}
    payload = {
        'user': userid
        }
    response = requests.post(userprofile_url, headers=headers, data=payload)

    if response.status_code == 200:
        app.logger.debug('Slack user profile response sent successfully.')

        # Get the request data
        response_json = json.loads(response.text)
        if "profile" in response_json and "email" in response_json["profile"]:
            return response_json["profile"]["email"]
        else:
            return response_json["profile"]["display_name"]
    else:
        app.logger.debug(f'Failed to send Slack response. Status code: {response.status_code}')

# Gets the original query text and the user id
def get_thread_parent(channel_id, thread_ts):
    replies_url = 'https://slack.com/api/conversations.replies'
    headers = {'Authorization': f'Bearer {slack_bot_token}'}
    payload = {
        'channel': channel_id, 
        'ts': thread_ts,
        'limit': '1' }
    
    response = requests.post(replies_url, headers=headers, data=payload)
    if response.status_code == 200:
        response_json = json.loads(response.text)
        messages = response_json["messages"]
        original_query = OriginalThread()
        original_query.text = messages[0]["text"]
        original_query.user = messages[0]["user"]
        return original_query
    else:
        app.logger.error(f'Failed to find original message ts: {thread_ts}')
        
# Gets the original query text
def get_message_parent(channel_id, thread_ts):
    replies_url = 'https://slack.com/api/conversations.replies'
    headers = {'Authorization': f'Bearer {slack_bot_token}'}
    payload = {
        'channel': channel_id, 
        'ts': thread_ts,
        'limit': '1' }
    
    response = requests.post(replies_url, headers=headers, data=payload)
    if response.status_code == 200:
        response_json = json.loads(response.text)
        messages = response_json["messages"]
        original_query = OriginalThread()
        original_query.text = messages[0]["text"]
        original_query.user = messages[0]["user"]
        return original_query.text
    else:
        app.logger.error(f'Failed to find original message.')

def send_slack_github_url(channel_id, thread_ts, github_url):
    slack_post_url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': f'Bearer {slack_bot_token}'}
    payload = {
        'channel': channel_id,
        'thread_ts': thread_ts, 
        'icon_emoji': ":information_desk_person:",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"An Analyst will be assigned as soon as possible to help! <{github_url}|Link to Ticket>"
                }
            }
        ]}
    requests.post(slack_post_url, headers=headers, json=payload)
    
def is_thread_responded(channel_id, thread_ts):
    for message in channel_messages(channel_id, thread_ts):
        if 'thread_ts' in message and message['thread_ts'] == thread_ts:
            return True
    return False

def channel_messages(channel_id, thread_ts):
    url = 'https://slack.com/api/conversations.replies'
    headers = {'Authorization': f'Bearer {slack_bot_token}'}
    params = {
        'channel': channel_id,
        'ts': thread_ts,
        'limit': '1'
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        response_json = response.json()
        if response_json['ok']:
            return response_json['messages']
        elif 'response_metadata' in response_json:
            return response_json['response_metadata']['messages']
    return []

def send_slack_response(channel_id, user_id, thread_ts, icon_emoji, message):
    # Send a response message in Slack
    text = f'Hello <@{user_id}>. \n{message}'
    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': f'Bearer {slack_bot_token}'}
    payload = {
        'channel': channel_id, 
        'text': text, 
        'thread_ts': thread_ts, 
        'icon_emoji': icon_emoji,
        "blocks": [
            {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": text  # Update to use the 'text' variable
                }
            },
            {
                "type": "actions",
                "elements": [
                  {
                    "type": "button",
                    "text": {
                      "type": "plain_text",
                      "text": ":ticket: I need further assistance"
                    }
                  }
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        app.logger.debug('Slack response sent successfully.')
    else:
        app.logger.debug(f'Failed to send Slack response. Status code: {response.status_code}')     

@app.route("/", methods=["GET", "POST"])
def index():   
    if request.method == 'POST':
        # Get the request data
        request_data = request.get_json()
        app.logger.debug("request_data: %s", request_data)
        # Process the request data
        return "Received POST request successfully", 200
    else:
        return "Health Checking", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
