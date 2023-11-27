import logging
import sys
from datetime import datetime, timedelta
from .app import jira_api_call, app
from app.aws_util import AWSUtil

# Configure logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

aws_util = AWSUtil()
jira_base_url, jira_api_token, jira_service_desk_id, jira_request_type_id = aws_util.load_jira_credentials()


class JIRAUtils:
    def __init__(self, ticket_key, channel_id=None, user_id=None, thread_ts=None):
        self.ticket_key = ticket_key
        self.channel_id = channel_id
        self.user_id = user_id
        self.thread_ts = thread_ts
        self.ticket_data = self.get_ticket_data()

    def get_ticket_data(self):
        issue_url = f"{jira_base_url}/rest/api/2/issue/{self.ticket_key}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jira_api_token}"
        }

        response = jira_api_call(
            issue_url, self.channel_id, self.user_id, self.thread_ts, method='GET', headers=headers)

        if response:
            if response.status_code == 200:
                return response.json()
        else:
            return None

    def get_ticket_creation_date_range(self):
        if self.ticket_data:
            created_date_str = self.ticket_data.get("fields", {}).get("created")
            try:
                created_date = datetime.strptime(
                    created_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')

                # Calculate one month before
                one_month_before = created_date - timedelta(days=30)

                return created_date.strftime('%Y-%m-%d %H:%M'), one_month_before.strftime('%Y-%m-%d %H:%M')
            except ValueError:
                app.logger.error("Error parsing date:", created_date_str)
                return None, None
        else:
            app.logger.error("Error getting Jira issue")
            return None, None

    def get_ticket_creation_date(self):
        if self.ticket_data:
            created_date_str = self.ticket_data.get("fields", {}).get("created")
            try:
                created_date = datetime.strptime(
                    created_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
                return created_date.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                app.logger.error("Error parsing date:", created_date_str)
        else:
            app.logger.error("Error getting Jira issue")
        return None

    def get_request_type(self):
        try:
            if self.ticket_data:
                if self.ticket_data['fields']['customfield_10708']:
                    if self.ticket_data['fields']['customfield_10708']['requestType']:
                        request_type = self.ticket_data['fields']['customfield_10708']['requestType']
                        return request_type['name']
                else:
                    app.logger.error("ERROR Jira issue missing customfield")
                    return None
            else:
                app.logger.error("Error getting Jira issue")
                return None
        except KeyError:
            app.logger.error(
                "Error getting custom fields for %s", self.ticket_key)

    def get_current_status(self):
        try:
            if self.ticket_data:
                if self.ticket_data['fields']['customfield_10708']:
                    if self.ticket_data['fields']['customfield_10708']['currentStatus']:
                        current_status = self.ticket_data['fields']['customfield_10708']['currentStatus']
                        return current_status['status']
                    else:
                        return None
                else:
                    app.logger.error("ERROR Jira issue missing customfield")
                    return None
            else:
                app.logger.error("Error getting Jira issue")
                return None
        except KeyError:
            app.logger.error(
                "Error getting custom fields for %s", self.ticket_key)

# Entry point of the script
if __name__ == "__main__":
    logger.debug(f"==> in jira_uti\n")
    # command: python -m app.jira_util