#!/usr/bin/env python3
"""Set up SQLModel database configuration for a project."""

import argparse
from pathlib import Path


def generate_sync_database(db_type: str) -> str:
    """Generate synchronous database configuration."""
    if db_type == "sqlite":
        url = 'sqlite:///./database.db'
        connect_args = ', connect_args={"check_same_thread": False}'
    elif db_type == "postgresql":
        url = 'postgresql://user:password@localhost:5432/dbname'
        connect_args = ''
    elif db_type == "mysql":
        url = 'mysql+pymysql://user:password@localhost:3306/dbname'
        connect_args = ''
    else:
        url = 'sqlite:///./database.db'
        connect_args = ', connect_args={"check_same_thread": False}'

    return f'''"""Database configuration (synchronous)."""

import os
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

# Database URL from environment or default
DATABASE_URL = os.getenv("DATABASE_URL", "{url}")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True{connect_args},
)


def create_db_and_tables() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def drop_db_and_tables() -> None:
    """Drop all database tables."""
    SQLModel.metadata.drop_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session (FastAPI dependency)."""
    with Session(engine) as session:
        yield session


# For scripts and testing
def get_session_context() -> Session:
    """Get session for use in context manager."""
    return Session(engine)
'''


def generate_async_database(db_type: str) -> str:
    """Generate asynchronous database configuration."""
    if db_type == "sqlite":
        url = 'sqlite+aiosqlite:///./database.db'
    elif db_type == "postgresql":
        url = 'postgresql+asyncpg://user:password@localhost:5432/dbname'
    elif db_type == "mysql":
        url = 'mysql+aiomysql://user:password@localhost:3306/dbname'
    else:
        url = 'sqlite+aiosqlite:///./database.db'

    return f'''"""Database configuration (asynchronous)."""

import os
from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Database URL from environment or default
DATABASE_URL = os.getenv("DATABASE_URL", "{url}")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_and_tables() -> None:
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def drop_db_and_tables() -> None:
    """Drop all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (FastAPI dependency)."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# For scripts and testing
async def get_session_context() -> AsyncSession:
    """Get session for use in async context manager."""
    return async_session_maker()
'''


def generate_models_init() -> str:
    """Generate models __init__.py template."""
    return '''"""SQLModel models."""

# Import all models here to register them with SQLModel.metadata
# This is required for Alembic migrations to detect all tables

from .user import User, UserCreate, UserRead, UserUpdate

__all__ = [
    "User",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]
'''


def generate_sample_model() -> str:
    """Generate a sample User model."""
    return '''"""User model."""

from datetime import datetime
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    """User base schema with shared fields."""
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)


class User(UserBase, table=True):
    """User database model."""
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(min_length=8)


class UserRead(UserBase):
    """Schema for reading a user."""
    id: int
    created_at: datetime


class UserUpdate(SQLModel):
    """Schema for updating a user. All fields optional."""
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8)
'''


def generate_alembic_env(async_mode: bool) -> str:
    """Generate Alembic env.py content."""
    if async_mode:
        return '''"""Alembic environment configuration (async)."""

import asyncio
from logging.config import fileConfig
import os

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from sqlmodel import SQLModel

# Import all models to register them
from app.models import *  # noqa

config = context.config

# Set database URL from environment
config.set_main_option(
    "sqlalchemy.url",
    os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./database.db")
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
    else:
        return '''"""Alembic environment configuration (sync)."""

from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

from sqlmodel import SQLModel

# Import all models to register them
from app.models import *  # noqa

config = context.config

# Set database URL from environment
config.set_main_option(
    "sqlalchemy.url",
    os.environ.get("DATABASE_URL", "sqlite:///./database.db")
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''


def setup_database(
    output_path: Path,
    db_type: str = "sqlite",
    async_mode: bool = True,
) -> None:
    """Set up database configuration files."""

    print(f"Setting up SQLModel database configuration")
    print(f"  Database: {db_type}")
    print(f"  Mode: {'async' if async_mode else 'sync'}")
    print("=" * 50)

    # Create directories
    app_path = output_path / "app"
    models_path = app_path / "models"
    alembic_path = output_path / "alembic"

    app_path.mkdir(parents=True, exist_ok=True)
    models_path.mkdir(exist_ok=True)
    alembic_path.mkdir(exist_ok=True)

    # Generate database.py
    if async_mode:
        db_content = generate_async_database(db_type)
    else:
        db_content = generate_sync_database(db_type)

    db_file = app_path / "database.py"
    db_file.write_text(db_content, encoding="utf-8")
    print(f"  Created: {db_file}")

    # Generate models/__init__.py
    models_init = models_path / "__init__.py"
    models_init.write_text(generate_models_init(), encoding="utf-8")
    print(f"  Created: {models_init}")

    # Generate sample model
    user_model = models_path / "user.py"
    user_model.write_text(generate_sample_model(), encoding="utf-8")
    print(f"  Created: {user_model}")

    # Generate app/__init__.py
    app_init = app_path / "__init__.py"
    app_init.write_text('"""Application package."""\n', encoding="utf-8")
    print(f"  Created: {app_init}")

    # Generate Alembic env.py
    alembic_env = alembic_path / "env.py"
    alembic_env.write_text(generate_alembic_env(async_mode), encoding="utf-8")
    print(f"  Created: {alembic_env}")

    # Create versions directory
    versions_path = alembic_path / "versions"
    versions_path.mkdir(exist_ok=True)
    (versions_path / ".gitkeep").touch()
    print(f"  Created: {versions_path}")

    print("\n" + "=" * 50)
    print("Database setup complete!")
    print("\nNext steps:")
    print("  1. Install dependencies:")
    print(f"     pip install sqlmodel alembic", end="")
    if async_mode:
        if db_type == "sqlite":
            print(" aiosqlite")
        elif db_type == "postgresql":
            print(" asyncpg")
        elif db_type == "mysql":
            print(" aiomysql")
    else:
        if db_type == "postgresql":
            print(" psycopg2-binary")
        elif db_type == "mysql":
            print(" pymysql")
        else:
            print()

    print("  2. Set DATABASE_URL environment variable")
    print("  3. Initialize Alembic: alembic init alembic (if not done)")
    print("  4. Create migration: alembic revision --autogenerate -m 'Initial'")
    print("  5. Apply migration: alembic upgrade head")


def main():
    parser = argparse.ArgumentParser(
        description="Set up SQLModel database configuration"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path.cwd(),
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--db",
        choices=["sqlite", "postgresql", "mysql"],
        default="sqlite",
        help="Database type (default: sqlite)"
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Generate synchronous code (default: async)"
    )

    args = parser.parse_args()
    setup_database(args.output, args.db, not args.sync)


if __name__ == "__main__":
    main()
