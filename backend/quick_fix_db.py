import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

print("Fixing database...")
conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
conn.autocommit = True
cur = conn.cursor()

# Drop and recreate
cur.execute("DROP TABLE IF EXISTS task CASCADE")
print("Dropped old task table")

cur.execute("""
    CREATE TABLE task (
        id SERIAL PRIMARY KEY,
        content TEXT NOT NULL,
        completed BOOLEAN NOT NULL DEFAULT FALSE,
        user_id TEXT NOT NULL
    )
""")
print("Created new task table")

cur.execute("CREATE INDEX ix_task_user_id ON task (user_id)")
cur.execute("CREATE INDEX ix_task_content ON task (content)")
print("Created indexes")

cur.close()
conn.close()
print("Done!")
