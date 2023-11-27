# kabot DB                                                                                                        
### This README explains how to Create kabot with pgAdmin 4 (or any DB client, like Azure Data Studio). 


### General Prerequisites

Instructions for install pgAdmin 4 for local environment
  
  *  https://www.pgadmin.org/download/
  

### Setup kabot Database

Setup kabot Database by running the following scripts from the root/database directory of the knowledge-articles repo

#### Create kabot Schema
  
	1. Execute KA_createDB.sql to create kabot Database


#### Create Tables
  
	1. Execute KA_createTables.sql to create all tables in the kabot schema

	
#### Insert Data

	1. Execute KA_insertTables.sql to insert data into all tables in the kabot schema

#### Create Function

	1. Execute func_replace_urls.sql for replacing URLs and setting GitHub varibles

	2. Execute func_excluded_user.sql for checking if user in devops_user 
	
	
#### Perform Updates ONLY if any data need to be changed in kabot tables
		
	1. Modify KA_updateTables.sql with requirement
   
	2. Execute KA_updateTables.sql for data changes
		

### Refresh kabot Database
	
#### Refresh kabot Database by running the scripts from the root/database directory of the knowledge-articles repo
  
	1. Execute KA_dropDB.sql to remove kabot Database and kabot schema

	2. Execute KA_createDB.sql to create kabot Database

	3. Run the steps listed above to Create Tables, Insert Data, Create Function and Perform Updates


#### Refresh KA related tables and data in kabot DB
  
	1. Follow https://www.pgadmin.org/docs/pgadmin4/development/backup_and_restore.html# to back up kabot DB

	NOTE: Only in exceptional situations, if needed to rollback to the original state of DB, run restore process from pgAdmin.
	