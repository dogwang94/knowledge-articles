import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Jira configuration
jira_base_url = os.environ.get('JIRA_BASE_URL')
jira_api_token = os.environ.get('JIRA_API_TOKEN')
jira_project_key = os.environ.get('JIRA_PROJECT_KEY')


def get_jira_ticket_request_type(ticket_key):
  # Your Jira configuration
  jira_base_url = "https://jira.devops.va.gov/"
  jira_api_token = "YpWAsyQwQFsEN07o3OnRp5DScsvn55wyJkFCbY"
  
  # Construct the Jira issue URL
  jira_issue_url = f"{jira_base_url}rest/api/2/issue/{ticket_key}"

  # Set up headers for basic authentication
  headers = {
      "Content-Type": "application/json",
      'Authorization': f'Bearer {jira_api_token}'
  }

  # Send the Jira issue request
  response = requests.get(jira_issue_url, headers=headers)

  if response.status_code == 200:
    result = response.json()
    request_type = result['fields']['customfield_10708']['requestType']
    return request_type['name']
  else:
    print("Error:", response.text)
    return None
  
# Usage example
ticket_key = "DOTSD-31486"
request_type_name = get_jira_ticket_request_type(ticket_key)
print("request_type_name: ", request_type_name)

# def get_request_type_name(jira_response):
#   request_type = jira_response['fields']['customfield_10708']['requestType']
#   return request_type['name']


# Usage example
# ticket_key = "DOTSD-31006"
# jira_response = get_jira_ticket(ticket_key)
# name = get_request_type_name(jira_response)
# print(name)
