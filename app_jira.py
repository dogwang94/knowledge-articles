import re
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_ticket_metadata(ticket_key):
    # Your Jira configuration
    jira_base_url = "https://jira.devops.va.gov/"
    jira_api_token = "YpWAsyQwQFsEN07o3OnRp5DScsvn55wyJkFCbY"

    # Construct the Jira issue URL
    jira_issue_url = f"{jira_base_url}/rest/api/2/issue/{ticket_key}"

    # Set up headers for basic authentication
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {jira_api_token}'
    }
    

    # Send the Jira issue request
    response = requests.get(jira_issue_url, headers=headers)

    if response.status_code == 200:
        # Parse the JSON response
        issue_data = response.json()
        return issue_data
    else:
        # Handle error cases
        print("Error:", response.text)
        return None


def get_open_tickets_before(ticket_key, labels):
    # Your Jira configuration
    jira_base_url = "https://jira.devops.va.gov/"
    jira_api_token = "YpWAsyQwQFsEN07o3OnRp5DScsvn55wyJkFCbY"

    # Construct the Jira search URL
    jira_search_url = f"{jira_base_url}/rest/api/2/search"
    jql_query = (
        f'project = "Your Project Key" '
        f'AND status = Open '
        f'AND labels IN ({",".join(labels)}) '
        f'AND created < "{ticket_key}"'
    )

    # Set up headers for basic authentication
    headers = {
        "Content-Type": "application/json",
        'Authorization': f'Bearer {jira_api_token}'
    }


    # Send the Jira search request
    response = requests.get(jira_search_url, params={"jql": jql_query}, headers=headers)

    if response.status_code == 200:
        # Parse the JSON response
        search_results = response.json()
        total_open_tickets = search_results.get("total", 0)
        return total_open_tickets
    else:
        # Handle error cases
        print("Error:", response.text)
        return 0

@app.route('/slack/events', methods=['POST'])
def slack_event():
    # Parse the Slack event data
    request_data = request.get_json()
    event_text = request_data['event']['text']

    # Use regular expression to find ticket IDs like DOTSD-12345 in the message
    ticket_keys = re.findall(r'DOTSD-[0-9]+', event_text)

    if not ticket_keys:
        return jsonify({'message': "No valid ticket keys found in the input."})

    response_message = ""

    for ticket_key in ticket_keys:
        # Get ticket metadata from Jira
        ticket_metadata = get_ticket_metadata(ticket_key)
        
        if ticket_metadata:
            labels = ticket_metadata.get("fields", {}).get("labels", [])
            total_open_tickets = get_open_tickets_before(ticket_key, labels)
            
            response_message += f"{ticket_key} is the {total_open_tickets+1}th ticket in queue. We will get to your ticket as soon as we can.\n"

    return jsonify({'message': response_message})

if __name__ == '__main__':
    app.run(debug=True)
