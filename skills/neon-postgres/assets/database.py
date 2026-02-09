"""Neon PostgreSQL database configuration (async).

Production-ready database setup for serverless applications.
"""

import os
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# =============================================================================
# Configuration
# =============================================================================

# Use pooled URL for serverless, direct URL for migrations
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_DIRECT = os.getenv("DATABASE_URL_DIRECT", DATABASE_URL)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")


def get_async_url(url: str) -> str:
    """Convert standard URL to asyncpg URL."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


# =============================================================================
# Engine Configuration
# =============================================================================

# For serverless: Use NullPool, let Neon handle pooling
engine = create_async_engine(
    get_async_url(DATABASE_URL),
    poolclass=NullPool,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
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


async def dispose_engine() -> None:
    """Dispose of the engine (call on shutdown)."""
    await engine.dispose()


# =============================================================================
# Session Dependencies
# =============================================================================


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session.

    Usage:
        @app.get("/users/")
        async def get_users(session: AsyncSession = Depends(get_session)):
            result = await session.exec(select(User))
            return result.all()
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions (scripts/testing).

    Usage:
        async with get_session_context() as session:
            result = await session.exec(select(User))
            users = result.all()
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# =============================================================================
# Health Check
# =============================================================================


async def check_database_connection() -> bool:
    """Check if database is accessible."""
    try:
        async with async_session_maker() as session:
            from sqlalchemy import text
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False


async def get_database_info() -> dict:
    """Get database connection info."""
    try:
        async with async_session_maker() as session:
            from sqlalchemy import text
            result = await session.execute(text("""
                SELECT
                    current_database() as database,
                    current_user as user,
                    version() as version,
                    pg_size_pretty(pg_database_size(current_database())) as size
            """))
            row = result.fetchone()
            return {
                "connected": True,
                "database": row.database,
                "user": row.user,
                "version": row.version,
                "size": row.size,
            }
    except Exception as e:
        return {"connected": False, "error": str(e)}


# =============================================================================
# FastAPI Lifespan
# =============================================================================


@asynccontextmanager
async def lifespan(app):
    """
    FastAPI lifespan context manager.

    Usage:
        app = FastAPI(lifespan=lifespan)
    """
    # Startup
    connected = await check_database_connection()
    if not connected:
        raise RuntimeError("Cannot connect to database")

    yield

    # Shutdown
    await dispose_engine()


# =============================================================================
# Transaction Helpers
# =============================================================================


@asynccontextmanager
async def transaction():
    """
    Explicit transaction context manager.

    Usage:
        async with transaction() as session:
            session.add(user)
            session.add(profile)
            # Commits on exit, rolls back on exception
    """
    async with async_session_maker() as session:
        async with session.begin():
            yield session
