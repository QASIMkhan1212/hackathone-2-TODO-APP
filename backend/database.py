import os
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel

from models import Task # Import your models here

load_dotenv() # Load environment variables from .env

database_url = os.getenv("DATABASE_URL")

print(f"Using Neon PostgreSQL database")

# PostgreSQL configuration with extended timeouts for Neon wake-up
engine = create_engine(
    database_url,
    echo=False,  # Disable verbose logging
    pool_pre_ping=True,
    pool_size=3,  # Keep a few connections warm
    max_overflow=2,
    pool_recycle=3600,  # Recycle after 1 hour
    connect_args={
        "connect_timeout": 30,  # Initial connection timeout
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)

def create_db_and_tables():
    """Create database tables."""
    try:
        print("Creating database tables (waiting for Neon to wake up if needed)...")
        SQLModel.metadata.create_all(engine)
        print("SUCCESS: Database tables created!")
        return
    except Exception as e:
        print(f"ERROR creating database tables: {e}")
        print("The application will start, but database operations may fail.")

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
