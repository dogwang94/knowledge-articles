/*******************************************************
CREATED BY : DevOps Support
CREATION DATE : 08/05/2023

**** MODIFICATION HISTORY *****
LAST MODIFIED DATE    LAST MODIFIED BY      DESCRIPTION 
08/05/2023            LW                    Initial Draft
08/22/2023            LW                    updated link here
08/22/2023            LW                    updated GITHUB_REPO_NAME to GITHUB_KA_REPO_NAME
09/29/2023            LW                    inserted data in devops_user

DESCRIPTION: Script to insert data to tables
*********************************************************/

-- insert data into 'resource_url' table
INSERT INTO kabot.resource_url ("key", "url")
VALUES 
('okta_request_url', 'https://jira.devops.va.gov/servicedesk/customer/portal/1/create/961'),
('github_request_url', 'https://{GITHUB_REPO_OWNER}.github.io/github-handbook/guides/onboarding/getting-access#step-3-access-to-the-{GITHUB_REPO_OWNER}-organization'),
('slack_instruction_url', 'https://{GITHUB_REPO_OWNER}.github.io/{GITHUB_KA_REPO_NAME}/pages/Slack_Troubleshooting_Instructions/Slack_Troubleshooting_Instructions'),
('mural_access_url', 'https://{GITHUB_REPO_OWNER}.github.io/{GITHUB_KA_REPO_NAME}/pages/Get_Access_to_Mural/Get_Access_to_Mural');

select  *
from kabot.resource_url


-- insert data into 'knowledge_article' table
INSERT INTO kabot.knowledge_article ("resource_id", "key", "content")
VALUES
    (1, 'JIRA', 'For JIRA access, please request an Okta account by using the DOTS Service Desk link *<{okta_request_url}|here>*. If you are unable to request for yourself have a supervisor request for you.'),
    (2, 'GITHUB', 'For Department of Veteran Affairs GitHub access, please use the following link *<{github_request_url}|here>*'),
    (3, 'SLACK', 'For Slack help, please use the following link *<{slack_instruction_url}|here>*'),
    (4, 'MURAL', 'For Mural Access, please use the following link *<{mural_access_url}|here>*');

select  *
from kabot.knowledge_article

-- insert data into 'devops_user' table
INSERT INTO kabot.devops_user ("username", "email")
VALUES 
('Aile Oleghe', 'Aile.Oleghe@va.gov'),
('Andrew Zimmerman', 'Andrew.Zimmerman3@va.gov'),
('Anu Datta', 'anuradha.datta@va.gov'),
('Austin Larkin', 'austin.larkin@va.gov)'),
('Brian Lang', 'Brian.Lang3@va.gov'),
('Chris Patterson', 'Christopher.Patterson14@va.gov'),
('Curtis Kruger', 'Curtis.Kruger@va.gov'),
('Ernest Vazquez', 'Ernest.Vazquez@va.gov'),
('Idris Lawal', 'Idris.Lawal@va.gov'),
('Jeffrey Gamble', 'Jeffrey.Gamble2@va.gov'),
('John Gill', 'JOHN.GILL1@va.gov'),
('Karen King', 'Karen.King1@va.gov'),
('Laconia De Wet', 'Laconia.DeWet@va.gov'),
('Liping Wang', 'liping.wang2@va.gov'),
('Lyle Rosdahl', 'Lyle.Rosdahl@va.gov'),
('Mandi Woodroof', 'sophia.woodroof@va.gov'),
('Nathan Herrmann', 'NATHAN.HERRMANN@va.gov'),
('Sarah Adtani', 'Sarah.Adtani@va.gov'),
('Scott Blair', 'Scott.Blair@va.gov'),
('Seung Park', 'Seung.Park@va.gov'),
('Tinu Ogunbiyi', 'atinuke.ogunbiyi@va.gov'),
('Yida Li', 'Yida.Li@va.gov'),
('Zach Gibson', 'Zachary.Gibson@va.gov'),
('Zachary Blanchette', 'Zachary.Blanchette@va.gov')

select  *
from kabot.devops_user
