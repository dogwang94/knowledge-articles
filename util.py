import psycopg2 
import json

conn = psycopg2.connect(
  dbname="kabot",
  user="dots", 
  password="Happy123!",
  host="ka-bot-rds.cluster-cqvenmjmecmn.us-gov-west-1.rds.amazonaws.com",
  port="5432"
)

cur = conn.cursor()

cur.execute("""
  SELECT json_agg(result)
  FROM (
    SELECT * FROM kabot.func_select_ka()
  ) AS result
""")

result = cur.fetchone()[0]

print(json.dumps(result, indent=4))

cur.close()
conn.close()