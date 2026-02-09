"""
Fix the user_id column in the task table to be TEXT instead of INTEGER.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def fix_user_id_column():
    """Change user_id column from INTEGER to TEXT."""
    print("Connecting to database...")

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    print("Checking current task table schema...")

    # Check if task table exists
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'task' AND column_name = 'user_id'
    """)

    result = cur.fetchone()
    if result:
        print(f"Current user_id type: {result[1]}")

        if result[1] != 'text':
            print("\nDropping and recreating task table with correct schema...")

            # Drop the existing task table
            cur.execute("DROP TABLE IF EXISTS task CASCADE")
            print("[OK] Dropped old task table")

            # Create new task table with correct schema
            cur.execute("""
                CREATE TABLE task (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT FALSE,
                    user_id TEXT NOT NULL
                )
            """)
            print("[OK] Created new task table with user_id as TEXT")

            # Create index on user_id
            cur.execute("CREATE INDEX ix_task_user_id ON task (user_id)")
            print("[OK] Created index on user_id")

            # Create index on content
            cur.execute("CREATE INDEX ix_task_content ON task (content)")
            print("[OK] Created index on content")

        else:
            print("[OK] user_id is already TEXT type, no changes needed")
    else:
        print("\n[INFO] task table doesn't exist yet, creating it...")

        # Create task table with correct schema
        cur.execute("""
            CREATE TABLE task (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT FALSE,
                user_id TEXT NOT NULL
            )
        """)
        print("[OK] Created task table with user_id as TEXT")

        # Create index on user_id
        cur.execute("CREATE INDEX ix_task_user_id ON task (user_id)")
        print("[OK] Created index on user_id")

        # Create index on content
        cur.execute("CREATE INDEX ix_task_content ON task (content)")
        print("[OK] Created index on content")

    cur.close()
    conn.close()

    print("\n[SUCCESS] Database schema fixed! user_id is now TEXT.")

if __name__ == "__main__":
    try:
        fix_user_id_column()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
