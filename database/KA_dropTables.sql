/*******************************************************
CREATED BY : DevOps Support
CREATION DATE : 08/05/2023

**** MODIFICATION HISTORY *****
LAST MODIFIED DATE LAST MODIFIED BY DESCRIPTION 
08/05/2023         LW               Initial Draft
 
DESCRIPTION: Script to drop tables
*********************************************************/

-- drop the table 'resource_url' in the 'kabot' schema
DROP TABLE kabot.resource_url;

SELECT table_name, table_schema
FROM information_schema.tables
WHERE table_name = 'resource_url';

-- drop the table 'knowledge_article' in the 'kabot' schema
DROP TABLE kabot.knowledge_article;


SELECT table_name, table_schema
FROM information_schema.tables
WHERE table_name = 'knowledge_article';


