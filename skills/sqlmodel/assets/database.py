"""Database configuration template for SQLModel (async)."""

import os
from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# =============================================================================
# Configuration
# =============================================================================

# Database URL from environment
# SQLite:     sqlite+aiosqlite:///./database.db
# PostgreSQL: postgresql+asyncpg://user:password@localhost:5432/dbname
# MySQL:      mysql+aiomysql://user:password@localhost:3306/dbname

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./database.db"
)

# =============================================================================
# Engine Configuration
# =============================================================================

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    future=True,
    # Connection pool settings (for PostgreSQL/MySQL)
    # pool_size=20,
    # max_overflow=10,
    # pool_timeout=30,
    # pool_recycle=1800,
    # pool_pre_ping=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# =============================================================================
# Database Management
# =============================================================================


async def create_db_and_tables() -> None:
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_db_and_tables() -> None:
    """Drop all database tables (use with caution!)."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


# =============================================================================
# Session Dependencies
# =============================================================================


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session.

    Usage:
        @app.get("/users/")
        async def get_users(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# =============================================================================
# Context Manager (for scripts/testing)
# =============================================================================


class DatabaseSession:
    """Async context manager for database sessions."""

    async def __aenter__(self) -> AsyncSession:
        self.session = async_session_maker()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.session.close()


# Usage:
# async with DatabaseSession() as session:
#     result = await session.exec(select(User))
