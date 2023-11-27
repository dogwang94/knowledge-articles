import requests

# Define a list of email addresses
email_addresses = ["Yida.Li@cernerfederal.com", "Ernest.Vazquez@cernerfederal.com", "Liping.Wang@cernerfederal.com"]

# Initialize a dictionary to store email-to-user ID mappings
email_to_user_id = {}

# Your Slack API token (replace with your own token)
slack_token = "xoxb-5457216889457-5925154782769-szX7uK5XVX8AS4AWTiqpaP30"

for email in email_addresses:
    # Make a request to the Slack API to lookup the user by email
    response = requests.post(
        "https://slack.com/api/users.lookupByEmail",
        headers={"Authorization": f"Bearer {slack_token}"},
        json={"email": email}
    )

    # Parse the response
    data = response.json()
    
    if data["ok"]:
        user_id = data["user"]["id"]
        email_to_user_id[email] = user_id
    else:
        print(f"Error for email {email}: {data.get('error', 'Unknown error')}")

# Print the mapping of email addresses to user IDs
print(email_to_user_id)
