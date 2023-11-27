import requests
import time

# Your Slack workspace's API token
slack_token = 'xoxb-5457216889457-5444476616851-cAU3awudKWz2LUtl28vOleon'

def make_slack_request(url, headers):

  response = requests.get(url, headers=headers)

  # Handle rate limiting
  if response.status_code == 429:
    retry_after = int(response.headers['Retry-After'])  
    print(f"Rate limited. Retrying in {retry_after} seconds")
    time.sleep(retry_after)
    return make_slack_request(url, headers)

  # Check rate limit headers
  rate_limit = response.headers.get('X-RateLimit-Limit') or "Unknown"
  remaining = response.headers.get('X-RateLimit-Remaining') or "Unknown"
  reset_time = response.headers.get('X-RateLimit-Reset') or "Unknown"

  print(f"Rate Limit: {rate_limit}")
  print(f"Remaining: {remaining}") 
  print(f"Reset Time: {reset_time}")

  # Additional error handling  
  if not response.ok:
    print(f"Error: {response.text}")

  return response


headers = {'Authorization': f'Bearer {slack_token}'}

url = 'https://slack.com/api/channels.list'

response = make_slack_request(url, headers)