"""Script to wake up Neon database by making a simple connection."""
import os
import sys
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment")
    sys.exit(1)

print("Attempting to wake up Neon database...")
print(f"Connecting to: {DATABASE_URL.split('@')[1].split('/')[0]}")

try:
    # Make a simple connection to wake up the database
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=30)
    print("✓ Successfully connected to database!")

    # Execute a simple query
    cur = conn.cursor()
    cur.execute("SELECT 1")
    result = cur.fetchone()
    print(f"✓ Query executed successfully: {result}")

    cur.close()
    conn.close()
    print("✓ Database is awake and ready!")
    sys.exit(0)

except psycopg2.OperationalError as e:
    print(f"✗ Connection failed: {e}")
    print("\nPossible solutions:")
    print("1. Check if your Neon database is still active in the Neon dashboard")
    print("2. Wait a few seconds and try again (database might be waking up)")
    print("3. Verify your DATABASE_URL is correct")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)
