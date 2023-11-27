from flask import Flask, jsonify, request, abort
import logging
import sys
import slack_sdk
import boto3
from botocore.exceptions import ClientError
import requests
import json
import re
from werkzeug.exceptions import HTTPException
import urllib.parse
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
# from db_util import DbUtils
from app.db_util import DbUtils


app = Flask(__name__)
load_dotenv()

# Set the desired log level
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

server_type = ""

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
     
    if(os.getenv('TEST_ENV') == "local"):
        secret_name = os.getenv('AWS_SECRET_NAME')
        region_name = os.getenv('AWS_REGION_NAME')

    # TODO: secret_name and region_name
    secret_name = os.environ.get('SECRET_NAME')
    region_name = os.environ.get('REGION_NAME')

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
    github_token=os.getenv('GITHUB_TOKEN')
    github_repo_owner=os.getenv('GITHUB_REPO_OWNER')
    github_repo_name=os.getenv('GITHUB_REPO_NAME')
    github_ka_repo_name=os.getenv('GITHUB_KA_REPO_NAME')
    jira_base_url=os.getenv('JIRA_BASE_URL')
    jira_api_token=os.getenv('JIRA_API_TOKEN')
    jira_service_desk_id=os.getenv('JIRA_SERVICE_DESK_ID_DEV')
    jira_request_type_id=os.getenv('JIRA_REQUEST_TYPE_ID_DEV')
else:
    data = json.loads(get_secret())
    server_type = os.environ.get('SERVER_TYPE')
    if server_type == "DEV":
        slack_bot_token = data["SLACK_BOT_TOKEN_DEV"]
        github_repo_name = data['GITHUB_REPO_NAME_DEV']
        jira_service_desk_id = data['JIRA_SERVICE_DESK_ID_DEV']
        jira_request_type_id = data['JIRA_REQUEST_TYPE_ID_DEV']
    else:
        slack_bot_token=data["SLACK_BOT_TOKEN"]
        github_repo_name=data['GITHUB_REPO_NAME']
        jira_service_desk_id = data['JIRA_SERVICE_DESK_ID']
        jira_request_type_id = data['JIRA_REQUEST_TYPE_ID']
    jira_base_url=data['JIRA_BASE_URL']
    jira_api_token=data['JIRA_API_TOKEN']
    github_token=data['GITHUB_TOKEN']
    github_repo_owner=data['GITHUB_REPO_OWNER']  
    github_ka_repo_name=data['GITHUB_KA_REPO_NAME']

# Instantiate DbUtils
db_utils = DbUtils()


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
        thread_ts = request_data['event'].get('thread_ts', request_data['event']['ts'])
        channel_id = request_data['event']['channel']
       
        if 'user' in request_data['event']:
            user_id = request_data['event']['user']
            user_email = get_userEmail(user_id)

            try:
                is_excluded = db_utils.is_user_excluded(user_email)
            except (TypeError, IndexError) as e:
                app.logger.debug(f"Error: {e}")
                is_excluded = True
            
            if is_excluded:
                if not is_thread_responded(channel_id, thread_ts):
                    # Extract ticket_keys
                    ticket_keys = set(re.findall(r'(DOTSD-\d+|DSDS-\d+)', event_text, re.IGNORECASE))
                    formatted_ticket_keys = '\n'.join([f"-{key}" for key in sorted(ticket_keys)])
                    msg = f"We've found Jira Tickets that matched your query.\n{formatted_ticket_keys}\nChecking their status ..."

                    if ticket_keys: 
                        send_slack_jira_response(
                            channel_id,
                            user_id,  
                            thread_ts,
                            ":information_desk_person:",
                            msg,
                            None
                        )   
                        handle_jira_tickets(ticket_keys, user_id, thread_ts, channel_id)
                    else:               
                        handle_knowledge_articles(event_text, user_id, thread_ts, channel_id)
                        
                return jsonify({'success': True})  # Return early if user is excluded
            
    return jsonify({'success': True})


# Slack Interactivity API endpoint
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

        request_data = request.get_data()
        request_decoded_data = urllib.parse.unquote(request_data)

        # Remove the payload= from the form
        request_decoded_data = request_decoded_data.strip("payload=")
        request_payload = json.loads(request_decoded_data)

        # Check if user clicked block action
        if "block_actions" in request_payload.get("type", []):
            for action in request_payload.get("actions", []):
                if action.get("type") == "button":
                    action_id = action.get("action_id")
                    user_id = request_payload["user"]["id"]
                    thread_ts = request_payload['message']['thread_ts']
                    channel_id = request_payload['container']['channel_id']
                    original_request = get_thread_parent(channel_id, thread_ts)
                    
                    if action_id == "need_further_assistance":
                        title = "KA-BOT Ticket: " + original_request.text
                        user_email = get_userEmail(original_request.user)
                        slack_thread_url = get_slack_thread_url(channel_id, thread_ts)
                        body = f"User {user_email} has requested help with the following query: {original_request.text}\n\nHere's a link to the slack thread: {slack_thread_url}"
                                    
                        # Create Issue in Jira
                        response = open_jira_issue(title, body, channel_id, user_id, thread_ts)

                        # Sends a confirmation message to the slack channel
                        send_slack_jira_confirmation(channel_id, thread_ts, response["issueKey"])

                    elif action_id.startswith("bump_"):
                        button_ticket_key = action_id.split("_")[-1]
                        user_email = get_userEmail(user_id)
                        msg = f'{user_email} has bumped {button_ticket_key}.'
                        send_slack_jira_response(
                            channel_id,
                            user_id,
                            thread_ts,
                            ":information_desk_person:",
                            msg,
                            None
                        )        
                        add_comment_to_jira_ticket(button_ticket_key, user_email, channel_id, user_id, thread_ts)                     
    return jsonify({'success': True})

# Creates a new Jira Issue
def open_jira_issue(issue_title, issue_body, channel_id, user_id, thread_ts):
    url = f"{jira_base_url}/rest/servicedeskapi/request/"
    headers = {
        'Authorization': f'Bearer {jira_api_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'serviceDeskId': jira_service_desk_id,
        'requestTypeId': jira_request_type_id,
        'requestFieldValues': {
            'summary':issue_title,
            'description':issue_body,
        }
    }
    response = jira_api_call(url, channel_id, user_id, thread_ts, method='POST', headers=headers, payload=payload)

    if response is not None and response.status_code == 201:
        return response.json()
    else:
        app.logger.debug(f"Jira API request failed with status code: {response.status_code}")
        return None

# Add comment to exsist Jira ticket
def add_comment_to_jira_ticket(ticket_number, user_email, channel_id, user_id, thread_ts):
    url = f"{jira_base_url}/rest/api/2/issue/{ticket_number}/comment"
    comment = f'{user_email} has bumped this ticket.'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {jira_api_token}'  
    }
    payload = {
        'body': comment
    }
    response = jira_api_call(url, channel_id, user_id, thread_ts, method='POST', headers=headers, payload=payload)

    if response is not None and response.status_code == 201:
        return response.json()
    else:
        app.logger.debug(f"Jira API request failed with status code: {response.status_code}")
        return None
    
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
    print("get_thread_parent function called!") 
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

# Send the jira issue link to slack
def send_slack_jira_confirmation(channel_id, thread_ts, jira_ticket_ref):
    slack_post_url = 'https://slack.com/api/chat.postMessage'
    jira_ticket_ref_url = f"{jira_base_url}/browse/{jira_ticket_ref}"
    text = f'Your request has been received and an Analyst will be assigned as soon as possible to help! You can review your ticket with reference ID: *<{jira_ticket_ref_url}|{jira_ticket_ref}>*.'
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
                    "text": text
                }
            }
        ]}
    requests.post(slack_post_url, headers=headers, json=payload)
    
# Check if the thread is in message
def is_thread_responded(channel_id, thread_ts):
    for message in channel_messages(channel_id, thread_ts):
        if 'thread_ts' in message and message['thread_ts'] == thread_ts:
            return True
    return False

# Check the channel message
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

# Send a response message to Slack
def send_slack_response(channel_id, user_id, thread_ts, icon_emoji, message): 
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
                  "text": text
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
                    },
                    "action_id": "need_further_assistance"
                  }
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if server_type == 'DEV':
        app.logger.debug('SlackToken: %s', slack_bot_token)
        app.logger.debug('SlackResponse: %s', response)
    if response.status_code == 200:
        app.logger.debug('Slack response sent successfully.')
    else:
        app.logger.debug(f'Failed to send Slack response. Status code: {response.status_code}')    
        
# Send a response message to Slack for jira
def send_slack_jira_response(channel_id, user_id, thread_ts, icon_emoji, messages, button_ticket_keys):
    text = f'Hello <@{user_id}>. \n{messages}'

    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': f'Bearer {slack_bot_token}'}
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    ]

    # Add buttons to blocks if there are any older than two weeks tickets
    if button_ticket_keys:
        button_elements = []
        for button_ticket_key in button_ticket_keys:
            button_elements.append(
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": f"Bump {button_ticket_key}"
                    },
                    "action_id": f"bump_{button_ticket_key}"
                }
            )
        blocks.append({
            "type": "actions",
            "elements": button_elements
        })

    payload = {
        'channel': channel_id,
        'text': text,
        'thread_ts': thread_ts,
        'icon_emoji': icon_emoji,
        "blocks": blocks
    }
    response = requests.post(url, headers=headers, json=payload)

    if server_type == 'DEV':
        app.logger.debug('SlackToken: %s', slack_bot_token)
        app.logger.debug('SlackResponse: %s', response)
    if response.status_code == 200:
        app.logger.debug('Slack response sent successfully.')
    else:
        app.logger.debug(f'Failed to send Slack response. Status code: {response.status_code}')   

# Get number of tickets
def get_open_tickets_before(jira_obj):
  created_date, one_month_before = jira_obj.get_ticket_creation_date_range()
  request_type = jira_obj.get_request_type()

  jira_search_url = f"{jira_base_url}/rest/api/2/search"
  
  if created_date and one_month_before:
    jql_query = (
        f'created <= "{created_date}" AND created >= "{one_month_before}" '
        f'AND status != "Closed" '
        f'AND status != "Done" '
        f'AND status != "Canceled" '
        f'AND project = "DOTS Service Desk" '
        f'AND "DOTS Request Type Identifier" ~ "{request_type}" '
    ) 
  else:
    app.logger.debug("Error getting Jira dates.")
    
  headers = {
    "Content-Type": "application/json",
    'Authorization': f'Bearer {jira_api_token}'  
  }

  response = requests.get(jira_search_url, params={"jql": jql_query}, headers=headers)

  if response.status_code == 200:
    search_results = response.json()
    total_open_tickets = search_results.get("total", 0)
    return total_open_tickets
  else:
    app.logger.error("Error:", response.text)  
    return 0

# Event - knowledge articles
def handle_knowledge_articles(event_text, user_id, thread_ts, channel_id):
    KA_List = []  
    matching_values = []
    
    try:
        results = db_utils.get_ka_list(github_repo_owner, github_ka_repo_name)[0][0]  # Access the first element of the tuple
    except (TypeError, IndexError) as e:
        app.logger.debug(f"Error: {e}")
        results = []
    
    for result_set in results:
        for result in result_set:
            inner_obj = result.get('func_select_ka', {}) 
            if inner_obj:
                KA_List.append({inner_obj['key']: inner_obj['content']})
                matching_values.extend([
                    list(entry.values())[0] for entry in KA_List 
                    if list(entry.keys())[0].lower() in event_text.lower()
                ])

    matching_values = list(set(matching_values))

    if not matching_values:
        send_slack_response(
            channel_id,
            user_id,  
            thread_ts,
            ":information_desk_person:",
            "I'm sorry I could not find any matching keywords..."
        )
    else:
        formatted_output = "\n\n".join(f"• {value}" for value in matching_values)
        send_slack_response(
            channel_id,
            user_id,
            thread_ts,
            ":information_desk_person:",
            formatted_output
        )

# Event - jira tickets
def handle_jira_tickets(ticket_keys, user_id, thread_ts, channel_id):
    messages = []
    button_ticket_keys = []

    for ticket_key in ticket_keys:
        jira_obj = JiraObject(ticket_key)

        if jira_obj.ticket_data:
            jira_ticket_status = jira_obj.get_current_status()

            if jira_ticket_status:
                if jira_ticket_status.lower() == 'done':
                    message = f"- {ticket_key} - Status is *Done*."
                else:
                    jira_ticket_type = jira_obj.get_request_type()
                    open_tickets_before = get_open_tickets_before(jira_obj)
                    message = f"- {ticket_key} - There are {open_tickets_before} tickets ahead of you in the current {jira_ticket_type} queue."

                    # Check if the ticket is older than two weeks
                    if is_ticket_older_than_two_weeks(jira_obj):
                        button_ticket_keys.append(ticket_key)
            else:
                message = f"- {ticket_key} - *This JIRA ticket is lacking a status.*"
        else:
            message = f"- {ticket_key} - *We cannot find this ticket in JIRA.*"
            
        messages.append(message)

    # Construct the full message with all non-button messages
    full_message = "\n".join(messages)

    # Send the message with buttons if there are any older than two weeks tickets
    send_slack_jira_response(channel_id, user_id, thread_ts, ":information_desk_person:", full_message, button_ticket_keys) 
    print("\n================= end of handle_jira_tickets\n")
    
# Check a jira ticket older than two weeks
def is_ticket_older_than_two_weeks(jira_obj):
    created_date_str = jira_obj.get_ticket_creation_date()
    
    if created_date_str:
        # Parse the date strings into datetime objects
        created_date = datetime.strptime(created_date_str, '%Y-%m-%d %H:%M:%S')

        # Check if the ticket creation date is older than two weeks from now
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        
        if created_date <= two_weeks_ago:
            return True  # Ticket is older than two weeks
        
    return False  # Ticket is not older than two weeks

def jira_api_call(url, channel_id, user_id, thread_ts, method='GET', headers=None, payload=None):   
    if not jira_base_url:
        app.logger.error(f'Jira API URL is not available.')
        warning_message = f'Jira API is not available. Please try again later.'
        send_slack_jira_response(channel_id, user_id, thread_ts, ":information_desk_person:", warning_message, [])
        return None

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=payload)
        # Add more methods (PUT, DELETE, etc.) if needed
        
        response.raise_for_status()  # Raise an HTTPError for bad requests (4xx and 5xx responses)

        if response.status_code == 200:
            app.logger.debug('Jira API call successful.')
            return response
        elif response.status_code == 201:
            app.logger.debug('Jira API call successful (Created).')
            return response
        elif response.status_code == 404:
            app.logger.debug(f'Jira API call failed. Status code: {response.status_code}')
            return response
        else:
            app.logger.debug(f'Jira API call failed. Status code: {response.status_code}')

    except requests.exceptions.RequestException as e:
        app.logger.error(f'Jira API call failed: {e}')
        print("\nrequests.exceptions.RequestException=> ", {e})
    except Exception as e:
        app.logger.error(f'Jira API call failed: {str(e)}')
        print("\nException=> ", {str(e)})

    error_message = 'The JIRA API is currently experiencing higher than normal queues. We could not process this request at this time.'

    send_slack_jira_response(channel_id, user_id, thread_ts, ":information_desk_person:", error_message, []) 
    return None



# JIRA Object Class
class JiraObject:
    def __init__(self, ticket_key, channel_id=None, user_id=None, thread_ts=None):     
        self.ticket_key = ticket_key
        self.channel_id = channel_id
        self.user_id = user_id
        self.thread_ts = thread_ts
        self.ticket_data = self.get_ticket_data()


    def get_ticket_data(self):
        issue_url = f"{jira_base_url}/rest/api/2/issue/{self.ticket_key}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jira_api_token}" 
        }

        response = jira_api_call(issue_url, self.channel_id, self.user_id, self.thread_ts, method='GET', headers=headers)

        if response:
            if response.status_code == 200:
                return response.json()
        else:
            return None

    def get_ticket_creation_date_range(self):
        if self.ticket_data:
            created_date_str = self.ticket_data.get("fields", {}).get("created")
            try:
                created_date = datetime.strptime(created_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
     
                # Calculate one month before
                one_month_before = created_date - timedelta(days=30) 
                
                return created_date.strftime('%Y-%m-%d %H:%M'), one_month_before.strftime('%Y-%m-%d %H:%M')
            except ValueError:
                app.logger.error("Error parsing date:", created_date_str)
                return None, None
        else:
            app.logger.error("Error getting Jira issue")
            return None, None
        
    def get_ticket_creation_date(self):
        if self.ticket_data:
            created_date_str = self.ticket_data.get("fields", {}).get("created")
            try:
                created_date = datetime.strptime(created_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
                return created_date.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                app.logger.error("Error parsing date:", created_date_str)
        else:
            app.logger.error("Error getting Jira issue")
        return None

    def get_request_type(self):
        try: 
            if self.ticket_data:
                if self.ticket_data['fields']['customfield_10708']:
                    if self.ticket_data['fields']['customfield_10708']['requestType']: 
                        request_type = self.ticket_data['fields']['customfield_10708']['requestType']
                        return request_type['name']
                else:
                    app.logger.error("ERROR Jira issue missing customfield")
                    return None
            else:
                app.logger.error("Error getting Jira issue")
                return None
        except KeyError:
            app.logger.error("Error getting custom fields for %s", self.ticket_key)
    
    def get_current_status(self):
        try: 
            if self.ticket_data:
                if self.ticket_data['fields']['customfield_10708']:
                    if self.ticket_data['fields']['customfield_10708']['currentStatus']:
                        current_status = self.ticket_data['fields']['customfield_10708']['currentStatus']
                        return current_status['status']
                    else:
                        return None
                else:
                    app.logger.error("ERROR Jira issue missing customfield")
                    return None
            else:
                app.logger.error("Error getting Jira issue")
                return None
        except KeyError:
            app.logger.error("Error getting custom fields for %s", self.ticket_key)



@app.route("/", methods=["GET", "POST"])
def index():   
    if request.method == 'POST':
        return "Received POST request successfully", 200
    else:
        return "Health Checking", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    # python -m app.app