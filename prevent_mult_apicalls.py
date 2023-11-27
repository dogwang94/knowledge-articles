import requests
from datetime import datetime

# Define a dictionary to cache Jira ticket responses
jira_ticket_cache = {}

def get_jira_ticket(ticket_key):
    # Check if the ticket response is already in the cache
    if ticket_key in jira_ticket_cache:
        return jira_ticket_cache[ticket_key]

    # Your Jira configuration
    jira_base_url = "https://jira.devops.va.gov/"
    jira_api_token = "YpWAsyQwQFsEN07o3OnRp5DScsvn55wyJkFCbY"
    
    # Construct issue URL
    issue_url = f"{jira_base_url}rest/api/2/issue/{ticket_key}"
    print("issue_url====> %s", issue_url)
    # API headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {jira_api_token}" 
    }

    # Make API call
    response = requests.get(issue_url, headers=headers)

    if response.status_code == 200:
        # Cache the response
        jira_ticket_cache[ticket_key] = response.json()
        return jira_ticket_cache[ticket_key]
    else:
        print("Error:", response.text)
        return None

def get_ticket_creation_date(ticket_key):
    issue = get_jira_ticket(ticket_key)

    if issue:
        created_date_str = issue.get("fields", {}).get("created")
        try:
            created_date = datetime.strptime(created_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            return created_date.strftime('%Y-%m-%d %H:%M')
        except ValueError:
            print("Error parsing date:", created_date_str)
            return None
    else:
        print("Error getting Jira issue")
        return None

def get_jira_ticket_request_type(ticket_key):
    issue = get_jira_ticket(ticket_key)
    if issue:
        request_type = issue['fields']['customfield_10708']['requestType']
        return request_type['name']

# Example usage
ticket_key1 = "DOTSD-31486"
ticket_key2 = "DOTSD-32184"

# Call the functions with the same ticket key
print(get_ticket_creation_date(ticket_key1))
print(get_jira_ticket_request_type(ticket_key1))

# Call the functions with a different ticket key
# print(get_ticket_creation_date(ticket_key2))
# print(get_jira_ticket_request_type(ticket_key2))
