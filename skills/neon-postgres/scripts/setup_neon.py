#!/usr/bin/env python3
"""Set up Neon PostgreSQL project and database configuration."""

import argparse
from pathlib import Path


def generate_database_config(async_mode: bool = True) -> str:
    """Generate database configuration file."""
    if async_mode:
        return '''"""Neon PostgreSQL database configuration (async)."""

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

# =============================================================================
# Engine Configuration
# =============================================================================

# For serverless: Use NullPool, let Neon handle pooling
engine = create_async_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
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


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions (scripts/testing).

    Usage:
        async with get_session_context() as session:
            result = await session.exec(select(User))
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
'''
    else:
        return '''"""Neon PostgreSQL database configuration (sync)."""

import os
from typing import Generator
from contextlib import contextmanager

from sqlmodel import SQLModel, Session, create_engine

# =============================================================================
# Configuration
# =============================================================================

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_DIRECT = os.getenv("DATABASE_URL_DIRECT", DATABASE_URL)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# =============================================================================
# Engine Configuration
# =============================================================================

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    pool_pre_ping=True,
)

# =============================================================================
# Database Management
# =============================================================================


def create_db_and_tables() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def drop_db_and_tables() -> None:
    """Drop all database tables (use with caution!)."""
    SQLModel.metadata.drop_all(engine)


# =============================================================================
# Session Dependencies
# =============================================================================


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    with Session(engine) as session:
        yield session


# =============================================================================
# Health Check
# =============================================================================


def check_database_connection() -> bool:
    """Check if database is accessible."""
    try:
        with Session(engine) as session:
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
'''


def generate_env_template() -> str:
    """Generate .env template."""
    return '''# Neon PostgreSQL Configuration

# Pooled connection (for application - serverless)
# Format: postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require
DATABASE_URL=

# Direct connection (for migrations)
# Format: postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
DATABASE_URL_DIRECT=

# Neon API (for branching)
NEON_API_KEY=
NEON_PROJECT_ID=

# OpenAI (for embeddings)
OPENAI_API_KEY=

# Debug
DB_ECHO=false
'''


def generate_neon_client() -> str:
    """Generate Neon API client."""
    return '''"""Neon API client for branch management."""

import os
from typing import Optional
import httpx

NEON_API_KEY = os.getenv("NEON_API_KEY")
NEON_PROJECT_ID = os.getenv("NEON_PROJECT_ID")
API_BASE = "https://console.neon.tech/api/v2"


class NeonClient:
    """Client for Neon Management API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        self.api_key = api_key or NEON_API_KEY
        self.project_id = project_id or NEON_PROJECT_ID

        if not self.api_key:
            raise ValueError("NEON_API_KEY is required")
        if not self.project_id:
            raise ValueError("NEON_PROJECT_ID is required")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def list_branches(self) -> list[dict]:
        """List all branches in the project."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/projects/{self.project_id}/branches",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()["branches"]

    async def create_branch(
        self,
        name: str,
        parent_id: Optional[str] = None,
        parent_timestamp: Optional[str] = None,
    ) -> dict:
        """Create a new branch."""
        payload = {
            "branch": {"name": name},
            "endpoints": [{"type": "read_write"}],
        }

        if parent_id:
            payload["branch"]["parent_id"] = parent_id
        if parent_timestamp:
            payload["branch"]["parent_timestamp"] = parent_timestamp

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/projects/{self.project_id}/branches",
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def delete_branch(self, branch_id: str) -> bool:
        """Delete a branch."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{API_BASE}/projects/{self.project_id}/branches/{branch_id}",
                headers=self.headers,
            )
            return response.status_code == 204

    async def get_branch(self, branch_id: str) -> dict:
        """Get branch details."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/projects/{self.project_id}/branches/{branch_id}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_connection_string(
        self,
        branch_id: str,
        pooled: bool = True,
    ) -> str:
        """Get connection string for a branch."""
        branch = await self.get_branch(branch_id)
        conn_uri = branch.get("connection_uris", [{}])[0].get("connection_uri", "")

        if pooled and conn_uri:
            conn_uri = conn_uri.replace(".neon.tech", "-pooler.neon.tech")

        return conn_uri


# Convenience functions
_client: Optional[NeonClient] = None


def get_neon_client() -> NeonClient:
    """Get or create Neon client singleton."""
    global _client
    if _client is None:
        _client = NeonClient()
    return _client


async def create_branch(name: str, **kwargs) -> dict:
    """Create a new branch."""
    return await get_neon_client().create_branch(name, **kwargs)


async def delete_branch(branch_id: str) -> bool:
    """Delete a branch."""
    return await get_neon_client().delete_branch(branch_id)


async def list_branches() -> list[dict]:
    """List all branches."""
    return await get_neon_client().list_branches()
'''


def setup_neon_project(
    output_path: Path,
    async_mode: bool = True,
    include_neon_client: bool = True,
) -> None:
    """Set up Neon project files."""
    print("Setting up Neon PostgreSQL project")
    print(f"  Mode: {'async' if async_mode else 'sync'}")
    print("=" * 50)

    # Create directories
    app_path = output_path / "app"
    app_path.mkdir(parents=True, exist_ok=True)

    # Generate database.py
    db_file = app_path / "database.py"
    db_file.write_text(generate_database_config(async_mode), encoding="utf-8")
    print(f"  Created: {db_file}")

    # Generate .env.example
    env_file = output_path / ".env.example"
    env_file.write_text(generate_env_template(), encoding="utf-8")
    print(f"  Created: {env_file}")

    # Generate neon_client.py
    if include_neon_client:
        client_file = app_path / "neon_client.py"
        client_file.write_text(generate_neon_client(), encoding="utf-8")
        print(f"  Created: {client_file}")

    # Generate app/__init__.py
    init_file = app_path / "__init__.py"
    init_file.write_text('"""Application package."""\n', encoding="utf-8")
    print(f"  Created: {init_file}")

    print("\n" + "=" * 50)
    print("Neon setup complete!")
    print("\nNext steps:")
    print("  1. Copy .env.example to .env and fill in values")
    print("  2. Install dependencies:")
    print("     pip install sqlmodel asyncpg sqlalchemy[asyncio] httpx")
    print("  3. Create your models in app/models.py")
    print("  4. Initialize Alembic: alembic init alembic")
    print("  5. Configure alembic/env.py for async migrations")


def main():
    parser = argparse.ArgumentParser(
        description="Set up Neon PostgreSQL project"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path.cwd(),
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Generate synchronous code (default: async)"
    )
    parser.add_argument(
        "--no-client",
        action="store_true",
        help="Skip Neon API client generation"
    )

    args = parser.parse_args()
    setup_neon_project(
        args.output,
        async_mode=not args.sync,
        include_neon_client=not args.no_client,
    )


if __name__ == "__main__":
    main()
