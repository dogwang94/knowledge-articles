# Import necessary modules and set up the environment
import os
from flask import Flask
from github import Github
import logging
import sys

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)  # Set the desired log level

# Set up the GitHub client
github_token = "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"
github_client = Github(github_token)



# Define the function
def send_notification_to_slack(issue_number, github_repo_owner, github_repo_name):
    issue = github_client.get_repo(f'{github_repo_owner}/{github_repo_name}').get_issue(issue_number)
    if issue.comments:
        thread_ts = issue.comments[0].body.split('\n')[0].split(': ')[1]
        app.logger.debug("issue: %s", issue)
        app.logger.debug("thread_ts: %s", thread_ts)
    else:
        thread_ts = "None"
        app.logger.debug("No comments found for the issue. Setting thread_ts to None.")
    
    os.environ['THREAD_TS'] = thread_ts
    # Rest of your notification sending logic
    return thread_ts


# Test the function
sample_issue_number = 48  # Replace with the actual issue number
sample_repo_owner = "dogwang94"  # Replace with the actual repository owner
sample_repo_name = "knowledge-articles"  # Replace with the actual repository name

result = send_notification_to_slack(sample_issue_number, sample_repo_owner, sample_repo_name)
print(f"Thread timestamp: {result}")

