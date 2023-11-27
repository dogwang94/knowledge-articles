/*******************************************************
CREATED BY : DevOps Support
CREATION DATE : 08/05/2023

**** MODIFICATION HISTORY *****
LAST MODIFIED DATE LAST MODIFIED BY DESCRIPTION 
08/05/2023         LW               Initial Draft
09/29/2023         LW               added devops_user
 
DESCRIPTION: Script to create tables in the 'kabot' schema
*********************************************************/

-- create the table 'resource_url' in the 'kabot' schema
CREATE TABLE kabot.resource_url (
  id SERIAL PRIMARY KEY,
  "key" VARCHAR(50),
  url VARCHAR(1000) 
);

-- create the table 'knowledge_article' in the 'kabot' schema
CREATE TABLE kabot.knowledge_article (
  id SERIAL PRIMARY KEY,
  resource_id INTEGER,
  "key" VARCHAR(50),
  content VARCHAR(2000)
);

-- establish a foreign key relationship between the tables
ALTER TABLE kabot.knowledge_article 
ADD CONSTRAINT fk_resource
FOREIGN KEY (resource_id) 
REFERENCES kabot.resource_url(id);

-- create the table 'devops_user' in the 'kabot' schema
CREATE TABLE kabot.devops_user (
  id SERIAL PRIMARY KEY,
  "username" VARCHAR(50),
  "email" VARCHAR(1000) 
);