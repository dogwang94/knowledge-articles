import psycopg2
import re
import json

def get_replaced_value(content, replacements):
    for key, url in replacements.items():
        content = content.replace('<{' + key + '}|', '<{' + url + '}|')
    return content

conn = psycopg2.connect(
    dbname="kabot",
    user="dots",
    password="Happy123!",
    host="ka-bot-rds.cluster-cqvenmjmecmn.us-gov-west-1.rds.amazonaws.com",
    port="5432"
)

cur = conn.cursor()

cur.execute("SELECT key, content FROM kabot.knowledge_article")
knowledge_articles = cur.fetchall()

cur.execute("SELECT key, url FROM kabot.resource_url")
resource_urls = cur.fetchall()

replacements = {key: url for key, url in resource_urls}

result = []
for key, content in knowledge_articles:
    replaced_value = get_replaced_value(content, replacements)
    result.append({"key": key, "content": replaced_value})

print(json.dumps(result, indent=4))

cur.close()
conn.close()