import os
import psycopg2
from psycopg2 import pool
import logging
import sys
# from . import aws_util
from app.aws_util import AWSUtil


# Configure logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

aws_util = AWSUtil()
db_name, db_user, db_password, db_host, db_port = aws_util.load_db_credentials()

class DbUtils:
    def __init__(self):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
        except psycopg2.OperationalError as e:
            logger.error(f"Database error: {e}")
            self.connection_pool = None

    def execute_query(self, query, *params):
        connection = None
        error = None
        results = None
        try:
            connection = self.connection_pool.getconn()
            cursor = connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall() or None  # Return None for an empty result set
            cursor.close()
        except psycopg2.Error as e:
            error = str(e)
            logger.error(f"Error executing query: {e}")
        finally:
            if connection:
                self.connection_pool.putconn(connection)
        return results, error


    def get_ka_list(self, github_repo_owner, github_ka_repo_name):
        query = """
            SELECT json_agg(result)
            FROM (
                SELECT *
                FROM kabot.func_select_ka(%s, %s)
            ) AS result;
        """
        try:
            return self.execute_query(query, github_repo_owner, github_ka_repo_name)
        except Exception as e:
            logger.error(f"Error fetching KA list: {e}")
            return None

    def is_user_excluded(self, new_user_email):
        query_user = """
            SELECT kabot.func_excluded_user(%s);
        """
        try:
            results, error = self.execute_query(query_user, new_user_email)
    
            is_excluded = results[0][0]
            return is_excluded
        except Exception as e:
            logger.error(f"Error checking excluded user: {e}")
            return False


# Entry point of the script
if __name__ == "__main__":
    logger.debug(f"==> in db_uti\n")
    # command: python -m app.db_util
    
    
    # Create an instance of DbUtils with the provided credentials
    db_instance = DbUtils()

    ka_list, error = db_instance.get_ka_list("github_owner", "ka_repo_name")
    if error:
        logger.error(f"Error fetching KA list: {error}")
    else:
        logger.debug(f"== Fetched KA list ==\n {ka_list}\n")

    user_email = "dogwang94@gmail.com"
    is_excluded = db_instance.is_user_excluded(user_email)
    logger.debug(f"== Is user {user_email} excluded? == \n{is_excluded}\n")
