"""
Initialize Better Auth tables in the database.
This script creates all the necessary tables for Better Auth authentication.
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

def init_tables():
    """Create Better Auth tables."""
    print("Connecting to database...")

    # Parse the connection string for psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    print("Creating Better Auth tables...\n")

    # Create user table
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
    print("[OK] user table created")

    # Create session table
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
    print("[OK] session table created")

    # Create account table
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
    print("[OK] account table created")

    # Create verification table
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
    print("[OK] verification table created")

    # Create jwks table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS "jwks" (
            "id" TEXT PRIMARY KEY,
            "publicKey" TEXT NOT NULL,
            "privateKey" TEXT NOT NULL,
            "createdAt" TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)
    print("[OK] jwks table created")

    cur.close()
    conn.close()

    print("\n[SUCCESS] All Better Auth tables created successfully!")

if __name__ == "__main__":
    try:
        init_tables()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
