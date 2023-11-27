import requests
from datetime import datetime

# Jira configuration
jira_base_url = "https://jira.devops.va.gov/"
jira_api_token = "YpWAsyQwQFsEN07o3OnRp5DScsvn55wyJkFCbY"

class JiraObject:
    def __init__(self, ticket_key):
        self.ticket_key = ticket_key
        self.issue_data = self.fetch_issue_data()

    def fetch_issue_data(self):
        # Construct issue URL
        issue_url = f"{jira_base_url}rest/api/2/issue/{self.ticket_key}"

        # API headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jira_api_token}" 
        }

        # Make API call
        response = requests.get(issue_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print("Error:", response.text)
            return None

    def get_ticket_creation_date(self):
        if self.issue_data:
            created_date_str = self.issue_data.get("fields", {}).get("created")
            try:
                created_date = datetime.strptime(created_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
                return created_date.strftime('%Y-%m-%d %H:%M')
            except ValueError:
                print("Error parsing date:", created_date_str)
                return None
        else:
            print("Error getting Jira issue")
            return None

    def get_request_type(self):
        if self.issue_data:
            request_type = self.issue_data['fields']['customfield_10708']['requestType']
            return request_type['name']
        else:
            print("Error getting Jira issue")
            return None

# Example usage
ticket_key1 = "ABC-123"
ticket_key2 = "DEF-456"

# Create JiraObject instances
jira_obj1 = JiraObject(ticket_key1)
jira_obj2 = JiraObject(ticket_key2)

# Call the methods on the JiraObject instances
print("Ticket 1 - Created Date:", jira_obj1.get_ticket_creation_date())
print("Ticket 1 - Request Type:", jira_obj1.get_request_type())

print("Ticket 2 - Created Date:", jira_obj2.get_ticket_creation_date())
print("Ticket 2 - Request Type:", jira_obj2.get_request_type())
