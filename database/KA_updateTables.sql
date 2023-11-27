/*******************************************************
CREATED BY : DevOps Support
CREATION DATE : 08/05/2023

**** MODIFICATION HISTORY *****
LAST MODIFIED DATE LAST MODIFIED BY DESCRIPTION 
08/05/2023         LW               Initial Draft
 
DESCRIPTION: Script to update data to tables
*********************************************************/

-- update data in 'resource_url' table on 2023-08-31
UPDATE kabot.resource_url
SET url = 'https://{GITHUB_REPO_OWNER}.github.io/{GITHUB_KA_REPO_NAME}/pages/Slack_Troubleshooting_Instructions/Slack_Troubleshooting_Instructions'
WHERE key = 'slack_instruction_url';

UPDATE kabot.resource_url
SET url = 'https://{GITHUB_REPO_OWNER}.github.io/{GITHUB_KA_REPO_NAME}/pages/Get_Access_to_Mural/Get_Access_to_Mural'
WHERE key = 'mural_access_url';


-- update data in 'resource_url' table on 2023-08-21
UPDATE kabot.resource_url
SET url = 'https://jira.devops.va.gov/servicedesk/customer/portal/1/create/961'
WHERE key = 'okta_request_url';

UPDATE kabot.resource_url
SET url = 'https://{GITHUB_REPO_OWNER}.github.io/github-handbook/guides/onboarding/getting-access#step-3-access-to-the-{GITHUB_REPO_OWNER}-organization'
WHERE key = 'github_request_url';

select  * from kabot.resource_url


-- update data in 'knowledge_article' table on 2023-08-22
UPDATE kabot.knowledge_article
SET content = 'For Mural Access, please use the following link *<{mural_access_url}|here>*'
WHERE key = 'MURAL';

UPDATE kabot.knowledge_article
SET content = 'For Slack help, please use the following link *<{slack_instruction_url}|here>*'
WHERE key = 'SLACK';

UPDATE kabot.knowledge_article
SET content = 'For JIRA access, please request an Okta account by using the DOTS Service Desk link *<{okta_request_url}|here>*. If you are unable to request for yourself have a supervisor request for you.'
WHERE key = 'JIRA';

UPDATE kabot.knowledge_article
SET content = 'For Department of Veteran Affairs GitHub access, please use the following link *<{github_request_url}|here>*'
WHERE key = 'GITHUB';



select  * from kabot.knowledge_article

