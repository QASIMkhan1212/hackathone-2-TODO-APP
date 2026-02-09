#!/usr/bin/env python3
"""Generate Alembic configuration for Neon PostgreSQL."""

import argparse
from pathlib import Path


def generate_alembic_ini() -> str:
    """Generate alembic.ini configuration."""
    return '''[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -q

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
'''


def generate_env_py(async_mode: bool = True) -> str:
    """Generate alembic/env.py for Neon."""
    if async_mode:
        return '''"""Alembic environment configuration for Neon (async)."""

import asyncio
from logging.config import fileConfig
import os

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from sqlmodel import SQLModel

# Import all models to register them with SQLModel.metadata
# from app.models import *  # noqa
# from app.vector_models import *  # noqa

config = context.config

# Set database URL from environment
# Use direct URL (not pooled) for migrations
database_url = os.environ.get("DATABASE_URL_DIRECT") or os.environ.get("DATABASE_URL")
if database_url:
    # Convert to async driver
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
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
    """Run migrations with connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
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
        return '''"""Alembic environment configuration for Neon (sync)."""

from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

from sqlmodel import SQLModel

# Import all models to register them
# from app.models import *  # noqa

config = context.config

# Set database URL from environment
database_url = os.environ.get("DATABASE_URL_DIRECT") or os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

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
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''


def generate_script_mako() -> str:
    """Generate alembic/script.py.mako template."""
    return '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''


def generate_initial_migration() -> str:
    """Generate initial migration template."""
    return '''"""Initial migration

Revision ID: 001_initial
Revises:
Create Date: 2025-01-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Example: Create users table
    # op.create_table(
    #     'users',
    #     sa.Column('id', sa.Integer(), nullable=False),
    #     sa.Column('email', sa.String(255), nullable=False),
    #     sa.Column('name', sa.String(100), nullable=False),
    #     sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    #     sa.PrimaryKeyConstraint('id'),
    # )
    # op.create_index('ix_users_email', 'users', ['email'], unique=True)
    pass


def downgrade() -> None:
    # op.drop_index('ix_users_email')
    # op.drop_table('users')
    pass
'''


def generate_branch_migration_helper() -> str:
    """Generate helper script for branch-based migrations."""
    return '''#!/usr/bin/env python3
"""Branch-based migration workflow helper."""

import asyncio
import os
import subprocess
import sys

import httpx

NEON_API_KEY = os.getenv("NEON_API_KEY")
NEON_PROJECT_ID = os.getenv("NEON_PROJECT_ID")
API_BASE = "https://console.neon.tech/api/v2"


async def create_migration_branch(name: str) -> dict:
    """Create a branch for testing migrations."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE}/projects/{NEON_PROJECT_ID}/branches",
            headers={
                "Authorization": f"Bearer {NEON_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "branch": {"name": f"migration/{name}"},
                "endpoints": [{"type": "read_write"}],
            },
        )
        response.raise_for_status()
        return response.json()


async def delete_migration_branch(branch_id: str) -> bool:
    """Delete a migration branch."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{API_BASE}/projects/{NEON_PROJECT_ID}/branches/{branch_id}",
            headers={"Authorization": f"Bearer {NEON_API_KEY}"},
        )
        return response.status_code == 204


async def test_migration(migration_name: str) -> bool:
    """
    Test a migration on a temporary branch.

    1. Create migration branch
    2. Run migration upgrade
    3. Run migration downgrade
    4. Run migration upgrade again
    5. Delete branch

    Returns True if all steps succeed.
    """
    print(f"Testing migration: {migration_name}")
    print("=" * 50)

    # Create branch
    print("Creating migration branch...")
    branch_data = await create_migration_branch(migration_name)
    branch_id = branch_data["branch"]["id"]
    conn_uri = branch_data["connection_uris"][0]["connection_uri"]

    # Convert to async URL
    if conn_uri.startswith("postgresql://"):
        conn_uri = conn_uri.replace("postgresql://", "postgresql+asyncpg://")

    print(f"Branch created: {branch_id}")

    try:
        # Set environment for migrations
        env = os.environ.copy()
        env["DATABASE_URL_DIRECT"] = conn_uri

        # Run upgrade
        print("\\nRunning: alembic upgrade head")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Upgrade failed: {result.stderr}")
            return False
        print("Upgrade successful")

        # Run downgrade
        print("\\nRunning: alembic downgrade -1")
        result = subprocess.run(
            ["alembic", "downgrade", "-1"],
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Downgrade failed: {result.stderr}")
            return False
        print("Downgrade successful")

        # Run upgrade again
        print("\\nRunning: alembic upgrade head (verification)")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"Re-upgrade failed: {result.stderr}")
            return False
        print("Re-upgrade successful")

        print("\\n" + "=" * 50)
        print("Migration test PASSED")
        return True

    finally:
        # Cleanup
        print(f"\\nDeleting migration branch: {branch_id}")
        await delete_migration_branch(branch_id)
        print("Branch deleted")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python branch_migration.py <migration_name>")
        print("Example: python branch_migration.py add_users_table")
        sys.exit(1)

    if not NEON_API_KEY or not NEON_PROJECT_ID:
        print("Error: NEON_API_KEY and NEON_PROJECT_ID required")
        sys.exit(1)

    migration_name = sys.argv[1]
    success = await test_migration(migration_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
'''


def setup_alembic(
    output_path: Path,
    async_mode: bool = True,
) -> None:
    """Set up Alembic configuration for Neon."""
    print("Setting up Alembic migrations for Neon")
    print(f"  Mode: {'async' if async_mode else 'sync'}")
    print("=" * 50)

    # Create directories
    alembic_path = output_path / "alembic"
    versions_path = alembic_path / "versions"
    alembic_path.mkdir(parents=True, exist_ok=True)
    versions_path.mkdir(exist_ok=True)

    # Generate files
    files = [
        (output_path / "alembic.ini", generate_alembic_ini()),
        (alembic_path / "env.py", generate_env_py(async_mode)),
        (alembic_path / "script.py.mako", generate_script_mako()),
        (versions_path / "001_initial.py", generate_initial_migration()),
        (output_path / "branch_migration.py", generate_branch_migration_helper()),
    ]

    for file_path, content in files:
        file_path.write_text(content, encoding="utf-8")
        print(f"  Created: {file_path}")

    # Create .gitkeep in versions
    (versions_path / ".gitkeep").touch()

    print("\n" + "=" * 50)
    print("Alembic setup complete!")
    print("\nUsage:")
    print("  # Create new migration")
    print("  alembic revision --autogenerate -m 'Add users table'")
    print("")
    print("  # Test migration on branch")
    print("  python branch_migration.py add_users_table")
    print("")
    print("  # Apply to production")
    print("  alembic upgrade head")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Alembic configuration for Neon"
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

    args = parser.parse_args()
    setup_alembic(args.output, async_mode=not args.sync)


if __name__ == "__main__":
    main()
