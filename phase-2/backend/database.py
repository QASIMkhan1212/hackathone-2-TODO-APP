import os
import logging
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel

from models import Task

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Validate required environment variable
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is required")

# PostgreSQL configuration with extended timeouts for Neon wake-up
engine = create_engine(
    database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=3,
    max_overflow=2,
    pool_recycle=3600,
    connect_args={
        "connect_timeout": 30,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)


def create_db_and_tables() -> None:
    """Create database tables if they don't exist."""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to create database tables: {type(e).__name__}")
        raise


def get_session() -> Generator[Session, None, None]:
    """Get a database session."""
    with Session(engine) as session:
        yield session
