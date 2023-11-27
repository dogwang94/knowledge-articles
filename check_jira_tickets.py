
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Jira configuration
jira_base_url = os.environ.get('JIRA_BASE_URL')
jira_api_token = os.environ.get('JIRA_API_TOKEN')
jira_project_key = os.environ.get('JIRA_PROJECT_KEY')

# print("==== jira_base_url " + jira_base_url)
# print("==== jira_api_token " + jira_api_token)
# print("==== jira_project_key " + jira_project_key)


def get_ticket_creation_date(ticket_key):
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
        # Parse the JSON response
        issue_data = response.json()
        created_date_str = issue_data.get("fields", {}).get("created", "")
        try:
            created_date = datetime.strptime(created_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            return created_date.strftime('%Y-%m-%d %H:%M')
        except ValueError:
            print("Error parsing date:", created_date_str)
            return None
    else:
        # Handle error cases
        print("Error:", response.text)
        return None

# Usage example
# ticket_key = "DOTSD-30650"
# create_date = get_ticket_creation_date(ticket_key)
# print("create date: ", create_date)
     
     
def get_open_tickets_before(ticket_key):
  # Your Jira configuration
  jira_base_url = "https://jira.devops.va.gov/"
  jira_api_token = "YpWAsyQwQFsEN07o3OnRp5DScsvn55wyJkFCbY"


  # Get creation date of the specific ticket
  created_date = get_ticket_creation_date(ticket_key)
  if not created_date:
    return 0

  # Construct the Jira search URL
  jira_search_url = f"{jira_base_url}rest/api/2/search"

  
  jql_query = (
    f'created < "{created_date}" '
    f'AND status != "Closed" '
    f'AND status != "Done" '
    f'AND status != "Canceled" '
    f'AND project = "DOTS Service Desk" '
    f'AND "DOTS Request Type Identifier" ~ "Request Access"'
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

# Usage example
# ticket_key = "DOTSD-30650"
# jira_ticket_count = get_open_tickets_before(ticket_key)
# print("Number of open tickets created before this: ", jira_ticket_count)


# def get_jira_ticket_status(ticket_key):
#     # Construct the Jira issue URL
#     jira_issue_url = f"{jira_base_url}/rest/api/2/issue/{ticket_key}"

#     # Set up headers for basic authentication
#     headers = {
#         "Content-Type": "application/json",
#         'Authorization': f'Bearer {jira_api_token}'
#     }

#     # Send the Jira issue request
#     response = requests.get(jira_issue_url, headers=headers)

#     if response.status_code == 200:
#         # Parse the JSON response
#         issue_data = response.json()

#         # Get the status from the issue data
#         status = issue_data.get("fields", {}).get("status", {}).get("name", "Unknown")
#         return status
#     else:
#         # Handle error cases
#         print(f"Error: {response.status_code} {response.text}")
#         return "Unknown"

# # Usage example
# ticket_key = "DOTSD-343"
# jira_ticket_status = get_jira_ticket_status(ticket_key)
# print(f"Jira Ticket {ticket_key} Status:", jira_ticket_status)


# def get_jira_ticket_labels(ticket_key):
#     # Construct the Jira issue URL
#     jira_issue_url = f"{jira_base_url}/rest/api/2/issue/{ticket_key}"

#     # Set up headers for basic authentication
#     headers = {
#         "Content-Type": "application/json",
#         'Authorization': f'Bearer {jira_api_token}'
#     }

#     # Send the Jira issue request
#     response = requests.get(jira_issue_url, headers=headers)

#     if response.status_code == 200:
#         # Parse the JSON response
#         issue_data = response.json()

#         # Get the labels from the issue data
#         labels = issue_data.get("fields", {}).get("labels", [])
#         return labels
#     else:
#         # Handle error cases
#         print(f"Error: {response.status_code} {response.text}")
#         return []

# # Usage example
# ticket_key = "DOTSD-31833"
# jira_ticket_labels = get_jira_ticket_labels(ticket_key)
# print(f"Jira Ticket {ticket_key} Labels:", jira_ticket_labels)


# def check_jira_ticket_exists(ticket_key):
#     # Construct the Jira search query
#     jira_search_url = f"{jira_base_url}/rest/api/2/search"
#     # jql_query = f'text ~ "{ticket_key}"'
#     jql_query = f'key = "{ticket_key}"'

#     # Set up headers for basic authentication
#     headers = {
#         "Content-Type": "application/json",
#         'Authorization': f'Bearer {jira_api_token}'
#     }

#     # Send the Jira issue request
#     response = requests.get(jira_search_url, headers=headers, params={"jql": jql_query})

#     # Check for errors
#     if response.status_code != 200:
#         print(f"Error: {response.status_code} {response.text}")
#         return False

#     # Parse response
#     search_results = response.json()

#     # Check if ticket key found
#     if any(issue['key'] == ticket_key for issue in search_results['issues']):
#         return True

#     return False

# # Usage example
# ticket_key = "DOTSD-343"
# jira_ticket_exists = check_jira_ticket_exists(ticket_key)
# print("Jira Ticket Exists:", jira_ticket_exists)



# The bot will query our service desk for the labels associated with the ticket DOTSD-343
# def get_ticket_metadata(ticket_key):

#     # Construct the Jira issue URL
#     jira_issue_url = f"{jira_base_url}/rest/api/2/issue/{ticket_key}"

#     # Set up headers for basic authentication
#     headers = {
#         "Content-Type": "application/json",
#         'Authorization': f'Bearer {jira_api_token}'
#     }
    
#     # Send the Jira issue request
#     response = requests.get(jira_issue_url, headers=headers)

#     if response.status_code == 200:
#         # Parse the JSON response
#         issue_data = response.json()
#         labels = issue_data.get("fields", {}).get("labels", [])

#         return labels
#         # return issue_data
#     else:
#         # Handle error cases
#         print("Error:", response.text)
#         # return None
#         return []
    
# # Usage example
# query = "User's query goes here"
# jira_ticket_exists = get_ticket_metadata("DOTSD-31006")
# print("Jira Ticket Exists:", jira_ticket_exists)



# def get_jira_ticket_request_type(ticket_key):
#     # Construct the Jira issue URL
#     jira_issue_url = f"{jira_base_url}/rest/api/2/issue/{ticket_key}"

#     # Set up headers for basic authentication
#     headers = {
#         "Content-Type": "application/json",
#         'Authorization': f'Bearer {jira_api_token}'
#     }

#     # Send the Jira issue request
#     response = requests.get(jira_issue_url, headers=headers)

#     if response.status_code == 200:
#         # Parse the JSON response
#         issue_data = response.json()

#         # Extract custom field  
#         name = get_request_type_name(issue_data)
#         return name
#     else:
#         # Handle error cases
#         print(f"Error: {response.status_code} {response.text}")
#         return "Unknown"

# # Usage example
# ticket_key = "31006"
# request_typ = get_jira_ticket_request_type(ticket_key)
# print(f"Jira Ticket {ticket_key} request_typ:", request_typ)


# Updated method to query the list of tickets
# def get_open_tickets_before(ticket_key):
#     # Your Jira configuration
#     jira_base_url = "https://jira.devops.va.gov/"
#     jira_api_token = "YpWAsyQwQFsEN07o3OnRp5DScsvn55wyJkFCbY"
#     jira_proj_key = "DOTSD"

#     # Get creation date of the specific ticket
#     created_date = get_ticket_creation_date(ticket_key)
#     if not created_date:
#         return []

#     # Construct the Jira search URL
#     jira_search_url = f"{jira_base_url}rest/api/2/search"

#     jql_query = (
#         f'project = "{jira_proj_key}" '
#         f'AND created < "{created_date}" '
#         f'AND status != "Closed" '
#         f'AND status != "Done" '
#         f'AND status != "Canceled" '
#         f'AND project = "DOTS Service Desk" '
#         f'AND summary ~ "Okta Request"'
#     )

#     # Set up headers for basic authentication
#     headers = {
#         "Content-Type": "application/json",
#         'Authorization': f'Bearer {jira_api_token}'
#     }

#     # Send the Jira search request
#     response = requests.get(jira_search_url, params={"jql": jql_query, "maxResults": 1000}, headers=headers)

#     if response.status_code == 200:
#         # Parse the JSON response
#         search_results = response.json()
#         open_tickets = search_results.get("issues", [])
        
#         total_count = search_results.get("total", 0)
#         print(f"Total Open Tickets: {total_count}\n")
        
#         for ticket in open_tickets:
#             print("Ticket Key:", ticket["key"])
#             print("Summary:", ticket["fields"]["summary"])
#             print("Status:", ticket["fields"]["status"]["name"])  # Print the status
#             # Extract and print other relevant information as needed
#             print()
            
#         return open_tickets
#     else:
#         # Handle error cases
#         print("Error:", response.text)
#         return []

# # Example usage
# ticket_key = "DOTSD-30650"
# get_open_tickets_before(ticket_key)


# def get_jira_ticket(ticket_key):
#   # Your Jira configuration
#   jira_base_url = "https://jira.devops.va.gov/"
#   jira_api_token = "YpWAsyQwQFsEN07o3OnRp5DScsvn55wyJkFCbY"
  
#   # Construct the Jira issue URL
#   jira_issue_url = f"{jira_base_url}rest/api/2/issue/{ticket_key}"

#   # Set up headers for basic authentication
#   headers = {
#       "Content-Type": "application/json",
#       'Authorization': f'Bearer {jira_api_token}'
#   }

#   # Send the Jira issue request
#   response = requests.get(jira_issue_url, headers=headers)

#   if response.status_code == 200:
#     return True  
#   elif response.status_code == 404:
#     return False
#   else:
#     print(f"Failed to get Jira ticket {ticket_key}, status code: {response.status_code}")
#     return None
  
# # Usage example
# ticket_key = "DOTSD-31006"
# is_exist = get_jira_ticket(ticket_key)
# print("is_exist: ", is_exist)

# def get_jira_ticket_status(ticket_key):
#     # Construct the Jira issue URL
#     jira_issue_url = f"{jira_base_url}/rest/api/2/issue/{ticket_key}"

#     # Set up headers for basic authentication
#     headers = {
#         "Content-Type": "application/json",
#         'Authorization': f'Bearer {jira_api_token}'
#     }

#     # Send the Jira issue request
#     response = requests.get(jira_issue_url, headers=headers)

#     if response.status_code == 200:
#         # Parse the JSON response
#         issue_data = response.json()

#         # Get the status from the issue data
#         status = issue_data.get("fields", {}).get("status", {}).get("name", "Unknown")
#         return status
#     else:
#         # Handle error cases
#         app.logger.debug(f"Error: {response.status_code} {response.text}")
#         return "Unknown"

# def get_jira_ticket_labels(ticket_key):
#     # Construct the Jira issue URL
#     jira_issue_url = f"{jira_base_url}/rest/api/2/issue/{ticket_key}"

#     # Set up headers for basic authentication
#     headers = {
#         "Content-Type": "application/json",
#         'Authorization': f'Bearer {jira_api_token}'
#     }

#     # Send the Jira issue request
#     response = requests.get(jira_issue_url, headers=headers)

#     if response.status_code == 200:
#         # Parse the JSON response
#         issue_data = response.json()

#         # Get the labels from the issue data
#         labels = issue_data.get("fields", {}).get("labels", [])
#         # app.logger.debug(f"Labels for {ticket_key}: {labels}")
#         return labels
#     else:
#         # Handle error cases
#         app.logger.debug(f"Error: {response.status_code} {response.text}")
#         return []