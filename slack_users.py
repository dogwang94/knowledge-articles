import requests
import json 

# Your Slack workspace's API token
slack_token = 'xoxb-5457216889457-5925154782769-szX7uK5XVX8AS4AWTiqpaP30'

excluded_users = ["Yida.Li@cernerfederal.com", "Ernest.Vazquez@cernerfederal.com", "Liping.Wang@cernerfederal.com"]


def get_user_email(user_id, slack_bot_token):
    user_profile_url = "https://slack.com/api/users.profile.get?include_labels=false"
    headers = {'Authorization': f'Bearer {slack_bot_token}'}
    payload = {'user': user_id}

    try:
        response = requests.post(user_profile_url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        response_json = response.json()

        if "profile" in response_json and "email" in response_json["profile"]:
            return response_json["profile"]["email"]
        elif "profile" in response_json and "display_name" in response_json["profile"]:
            return response_json["profile"]["display_name"]
        else:
            return None  # Handle the case when neither email nor display_name is available

    except requests.exceptions.RequestException as e:
        print(f'Error occurred while fetching user profile: {e}')
        return None  # Handle the error case gracefully, return None or a default value

# Example usage

user_email = get_user_email('U05CZK3230V', slack_token)

if user_email:
    print(f"The email address of user U05CZK3230V is: {user_email}")
else:
    print(f"Failed to retrieve email address for user U05CZK3230V")


# def get_userId_byEmail(excluded_users):
# # Define a list of email addresses


# # Initialize a dictionary to store email-to-user ID mappings
# # email_to_user_id = {}

#     # List to store user IDs
#     user_ids = []

#     url = "https://slack.com/api/users.lookupByEmail"
#     headers={"Authorization": f"Bearer {slack_token}"}


#     for email in excluded_users:
#         # Make a request to the Slack API to lookup the user by email
#         params = {"email": email}
#         response = requests.get(url, headers=headers, params=params)
        
#     # Parse the response
#         data = response.json()
        
#         if data["ok"]:
#             user_id = data["user"]["id"]
#             user_ids.append(user_id)  # Append the user ID to the list
#             # email_to_user_id[email] = user_id
#         else:
#             print(f"Error for email {email}: {data.get('error', 'Unknown error')}")
            

#     # Print the mapping of email addresses to user IDs
#     # print(email_to_user_id[email])

#     return user_ids
# print("User IDs:", get_userId_byEmail(excluded_users))













# user_email = "liping_wang_qwest_com@yahoo.com" 
# url = "https://slack.com/api/users.lookupByEmail"
# headers={"Authorization": f"Bearer {slack_token}"}
# params = {"email": user_email}

# response = requests.get(url, headers=headers, params=params)
# # print("res===> ", response.json())
# if "user" not in response.json():
#     print("User not found")
# else:
#     user_id = response.json()["user"]["id"]
#     print("user_id===> ", user_id)

# if response.status_code != 200:
#     print(f"Error: {response.text}")
# else:
#     user_id = response.json()["user"]["id"]
#     print(user_id)

# # User ID for which you want to retrieve the email address
# user_id = "U05STPP061H" # liping_wang_qwest_com@yahoo.com
# # user_id = "U05D2DNH1QT"
# url = "https://slack.com/api/users.info"
# headers={"Authorization": f"Bearer {slack_token}"}
# params = {"user": user_id}

# response = requests.get(url, headers=headers, params=params)
# user_info = response.json()
# user_email = user_info["user"]["profile"]["email"]
# print(user_email)

# Make a request to the users.list API method
# response = requests.get(
#     'https://slack.com/api/users.list',
#     headers={'Authorization': f'Bearer {slack_token}'}
# )

# data = response.json()

# if data['ok']:
#     users = data['members']
#     for user in users:
#         print(json.dumps(user, indent=2))  # Print user data