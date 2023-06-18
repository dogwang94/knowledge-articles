import os
from flask import Flask, jsonify, request, abort
import slack_sdk
from github import Github
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
import requests
import json
import sys
import logging

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)  # Set the desired log level

# Initialize the Github API client
github_token = os.environ["GITHUB_TOKEN"]
github_client = Github(github_token)
github_repo_owner = os.environ["GITHUB_REPO_OWNER"]
github_repo_name = os.environ["GITHUB_REPO_NAME"]
github_url = f"https://api.github.com/repos/{github_repo_owner}/{github_repo_name}/issues"

# Define the Slack Bot token and the GitHub API token
slack_bot_token = os.environ["SLACK_BOT_TOKEN"]
slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
slack_channel_id=os.environ['SLACK_CHANNEL_ID']
app.logger.debug("slack_bot_token: %s", slack_bot_token)
app.logger.debug("slack_signing_secret: %s", slack_signing_secret)
app.logger.debug("slack_channel_id: %s", slack_channel_id)

# Initialize the Slack API client
slack_client = slack_sdk.WebClient(token=slack_bot_token)

# Initialize a new Slack app
# slack_app = App(
#     token=slack_bot_token,
#     signing_secret=slack_signing_secret
# )

BOT_ID = slack_client.api_call("auth.test")['user_id']
app.logger.debug("BOT_ID: %s", BOT_ID)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Check the request's content type
    if request.headers.get('Content-Type') != 'application/json':
        abort(400, 'Content-Type must be application/json')
        
    # Get the request data
    request_data = request.get_json()
    app.logger.debug("request_data: %s", request_data)
    
    # Check if the request is a Slack event URL verification challenge
    if "challenge" in request_data:
        return request_data["challenge"], 200
    
    # Check if the request is a Slack event
    if "event" in request_data and "type" in request_data["event"]:
        event_type = request_data["event"]["type"]
        # Handle message events
        if event_type == "message" and "text" in request_data["event"] and "user" in request_data["event"]:
            user_id = request_data["event"]["user"]
            channel_id = request_data["event"]["channel"]
            message_text = request_data["event"]["text"]

            # Check if the message is from the specified channel   
            if channel_id == slack_channel_id and user_id != BOT_ID:
                # Check if the bot has already responded
                if "thread_ts" not in request_data["event"]:
                    # Start a new thread for the user's response
                    thread_ts_initial = request_data["event"]["ts"]
                    app.logger.debug("thread_ts_initial: %s", thread_ts_initial)
                    # Send a message to the channel asking for a keyword
                    slack_message_thread(f"*I am KA_Support_Bot.* \n *Please provide me a keyword for searching*", channel_id, thread_ts_initial, ":information_desk_person:")

        # Handle message thread events
        if event_type == "message" and "text" in request_data["event"] and "user" in request_data["event"] and "thread_ts" in request_data["event"]:
            user_id = request_data["event"]["user"]
            channel_id = request_data["event"]["channel"]
            message_text = request_data["event"]["text"]
            thread_ts = request_data["event"]["thread_ts"]
            app.logger.debug("message_text: %s", message_text)
            app.logger.debug("thread_ts: %s", thread_ts)
            # Check if the message is a response to the bot's initial message
            if thread_ts and message_text and user_id != BOT_ID:
                # Create a GitHub issue with the keyword as the title
                github_title = message_text.strip()
                github_headers = {
                    "Authorization": "Bearer {}".format(github_token),
                    "Content-Type": "application/json"
                }
                github_data = {
                    "title": github_title
                }
                github_response = requests.post(github_url, headers=github_headers, data=json.dumps(github_data))

                # Send a message to the thread confirming the issue creation
                if github_response.ok:
                    slack_message_thread(f"*Searching for keyword \"{github_title}\"...*", channel_id, thread_ts, ":information_desk_person:")
                else:
                    slack_message_thread("Error creating issue", channel_id, thread_ts, ":information_desk_person:")

    # Return a response
    return "", 200

def slack_message(message, channel, icon_emoji):
    slack_data = {
        "token": slack_bot_token,
        "channel": channel,
        "text": message,
        "icon_emoji": icon_emoji
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {slack_bot_token}"
    }
    slack_response = requests.post("https://slack.com/api/chat.postMessage", data=slack_data, headers=headers)
    return slack_response

def slack_message_thread(message, channel, thread_ts, icon_emoji):
    slack_data = {
        "token": slack_bot_token,
        "channel": channel,
        "text": message,
        "thread_ts": thread_ts,
        "icon_emoji": icon_emoji
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {slack_bot_token}"
    }
    slack_response = requests.post("https://slack.com/api/chat.postMessage", data=json.dumps(slack_data), headers=headers)
    return slack_response

@app.route("/", methods=["GET", "POST"])
def index():   
    if request.method == 'POST':
        # Get the request data
        #request_data = request.json
        request_data = request.get_json()
        app.logger.debug("request_data: %s", request_data)
        # Process the request data
        return "Received POST request successfully", 200
    else:
        app.logger.debug("return: %s", "Health Checking")
        return "Health Checking", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)