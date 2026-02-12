"""
Complete database setup and verification script.
This will ensure all tables are created correctly and test the setup.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def setup_database():
    """Complete database setup."""
    print("=" * 60)
    print("COMPLETE DATABASE SETUP")
    print("=" * 60)

    print("\n[1/5] Connecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=30)
        conn.autocommit = True
        cur = conn.cursor()
        print("SUCCESS: Connected to database")
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}")
        return False

    print("\n[2/5] Creating Better Auth tables...")
    try:
        # User table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "user" (
                "id" TEXT PRIMARY KEY,
                "name" TEXT NOT NULL,
                "email" TEXT NOT NULL UNIQUE,
                "emailVerified" BOOLEAN NOT NULL DEFAULT FALSE,
                "image" TEXT,
                "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
                "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        # Session table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "session" (
                "id" TEXT PRIMARY KEY,
                "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
                "expiresAt" TIMESTAMP NOT NULL,
                "ipAddress" TEXT,
                "userAgent" TEXT,
                "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
                "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        # Account table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "account" (
                "id" TEXT PRIMARY KEY,
                "userId" TEXT NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
                "accountId" TEXT NOT NULL,
                "providerId" TEXT NOT NULL,
                "accessToken" TEXT,
                "refreshToken" TEXT,
                "idToken" TEXT,
                "expiresAt" TIMESTAMP,
                "password" TEXT,
                "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
                "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        # Verification table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "verification" (
                "id" TEXT PRIMARY KEY,
                "identifier" TEXT NOT NULL,
                "value" TEXT NOT NULL,
                "expiresAt" TIMESTAMP NOT NULL,
                "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
                "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        # JWKS table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "jwks" (
                "id" TEXT PRIMARY KEY,
                "publicKey" TEXT NOT NULL,
                "privateKey" TEXT NOT NULL,
                "createdAt" TIMESTAMP NOT NULL DEFAULT NOW()
            )
        """)

        print("SUCCESS: Better Auth tables created")
    except Exception as e:
        print(f"ERROR: Could not create Better Auth tables: {e}")
        return False

    print("\n[3/5] Creating Task table...")
    try:
        # Drop old task table if it has wrong schema
        cur.execute("DROP TABLE IF EXISTS task CASCADE")

        # Create task table with correct schema
        cur.execute("""
            CREATE TABLE task (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT FALSE,
                user_id TEXT NOT NULL
            )
        """)

        # Create indexes
        cur.execute("CREATE INDEX ix_task_user_id ON task (user_id)")
        cur.execute("CREATE INDEX ix_task_content ON task (content)")

        print("SUCCESS: Task table created with correct schema")
    except Exception as e:
        print(f"ERROR: Could not create task table: {e}")
        return False

    print("\n[4/5] Verifying table schemas...")
    try:
        # Check user table
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'user'
            ORDER BY ordinal_position
        """)
        print("  user table columns:", [row[0] for row in cur.fetchall()])

        # Check task table
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'task'
            ORDER BY ordinal_position
        """)
        task_cols = cur.fetchall()
        print("  task table columns:", [(row[0], row[1]) for row in task_cols])

        # Verify user_id is TEXT
        user_id_type = [row[1] for row in task_cols if row[0] == 'user_id'][0]
        if user_id_type == 'text':
            print("SUCCESS: task.user_id is TEXT (correct)")
        else:
            print(f"ERROR: task.user_id is {user_id_type} (should be TEXT)")
            return False

    except Exception as e:
        print(f"ERROR: Could not verify schemas: {e}")
        return False

    print("\n[5/5] Checking existing data...")
    try:
        cur.execute('SELECT COUNT(*) FROM "user"')
        user_count = cur.fetchone()[0]
        print(f"  Users in database: {user_count}")

        cur.execute("SELECT COUNT(*) FROM task")
        task_count = cur.fetchone()[0]
        print(f"  Tasks in database: {task_count}")

    except Exception as e:
        print(f"WARNING: Could not check data: {e}")

    cur.close()
    conn.close()

    print("\n" + "=" * 60)
    print("DATABASE SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Make sure backend is running on: http://localhost:8000")
    print("2. Make sure frontend is running on: http://localhost:3000")
    print("3. Sign up for a new account")
    print("4. Start using the app!")
    print("\n")

    return True

if __name__ == "__main__":
    try:
        success = setup_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
