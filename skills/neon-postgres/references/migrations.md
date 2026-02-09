# Database Migrations Reference

## Overview

Database migrations with Neon leverage branching for safe schema changes. Test migrations on branches before applying to production.

## Alembic Setup

### Installation

```bash
pip install alembic asyncpg sqlmodel
```

### Initialize Alembic

```bash
alembic init alembic
```

### Configure for Async

```python
# alembic/env.py
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
    os.environ.get("DATABASE_URL_DIRECT", "")  # Use direct URL for migrations
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
```

### alembic.ini Configuration

```ini
[alembic]
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
```

## Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Add users table"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history

# Generate SQL without applying
alembic upgrade head --sql > migration.sql
```

## Branch-Based Migration Workflow

### 1. Create Migration Branch

```python
import httpx
import os

async def create_migration_branch(migration_name: str) -> dict:
    """Create a branch for testing migrations."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://console.neon.tech/api/v2/projects/{os.getenv('NEON_PROJECT_ID')}/branches",
            headers={"Authorization": f"Bearer {os.getenv('NEON_API_KEY')}"},
            json={
                "branch": {"name": f"migration/{migration_name}"},
                "endpoints": [{"type": "read_write"}],
            },
        )
        return response.json()
```

### 2. Test Migration on Branch

```bash
# Set branch connection URL
export DATABASE_URL_DIRECT="postgresql://user:pass@ep-xxx.neon.tech/db"

# Run migration on branch
alembic upgrade head

# Verify migration
psql $DATABASE_URL_DIRECT -c "\dt"  # List tables
psql $DATABASE_URL_DIRECT -c "\d users"  # Describe table

# Run application tests against branch
pytest tests/
```

### 3. Apply to Production

```bash
# Switch to production URL
export DATABASE_URL_DIRECT="postgresql://user:pass@ep-main.neon.tech/db"

# Apply migration
alembic upgrade head

# Delete migration branch
neonctl branches delete migration/add-users-table
```

## Migration Script Patterns

### Create Table

```python
# alembic/versions/001_create_users.py
"""Create users table

Revision ID: 001
Revises:
Create Date: 2025-01-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_email')
    op.drop_table('users')
```

### Add Column

```python
"""Add avatar_url to users

Revision ID: 002
Revises: 001
"""
from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: str = '001'


def upgrade() -> None:
    op.add_column('users', sa.Column('avatar_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'avatar_url')
```

### Add pgvector Column

```python
"""Add embedding column to documents

Revision ID: 003
Revises: 002
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = '003'
down_revision: str = '002'


def upgrade() -> None:
    # Ensure pgvector extension exists
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Add vector column
    op.add_column(
        'documents',
        sa.Column('embedding', Vector(1536), nullable=True)
    )

    # Create HNSW index for fast similarity search
    op.execute('''
        CREATE INDEX documents_embedding_idx
        ON documents
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    ''')


def downgrade() -> None:
    op.drop_index('documents_embedding_idx')
    op.drop_column('documents', 'embedding')
```

### Data Migration

```python
"""Migrate legacy status to new format

Revision ID: 004
Revises: 003
"""
from alembic import op
import sqlalchemy as sa

revision: str = '004'
down_revision: str = '003'


def upgrade() -> None:
    # Add new column
    op.add_column('orders', sa.Column('status_v2', sa.String(50), nullable=True))

    # Migrate data
    op.execute("""
        UPDATE orders SET status_v2 = CASE
            WHEN status = 0 THEN 'pending'
            WHEN status = 1 THEN 'processing'
            WHEN status = 2 THEN 'completed'
            WHEN status = 3 THEN 'cancelled'
            ELSE 'unknown'
        END
    """)

    # Make new column non-nullable
    op.alter_column('orders', 'status_v2', nullable=False)

    # Drop old column
    op.drop_column('orders', 'status')

    # Rename new column
    op.alter_column('orders', 'status_v2', new_column_name='status')


def downgrade() -> None:
    # Reverse the process
    op.alter_column('orders', 'status', new_column_name='status_v2')
    op.add_column('orders', sa.Column('status', sa.Integer(), nullable=True))
    op.execute("""
        UPDATE orders SET status = CASE
            WHEN status_v2 = 'pending' THEN 0
            WHEN status_v2 = 'processing' THEN 1
            WHEN status_v2 = 'completed' THEN 2
            WHEN status_v2 = 'cancelled' THEN 3
            ELSE 0
        END
    """)
    op.alter_column('orders', 'status', nullable=False)
    op.drop_column('orders', 'status_v2')
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/migrations.yml
name: Database Migrations

on:
  push:
    branches: [main]
    paths:
      - 'alembic/**'

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install alembic asyncpg sqlmodel pgvector

      - name: Create migration branch
        env:
          NEON_API_KEY: ${{ secrets.NEON_API_KEY }}
          NEON_PROJECT_ID: ${{ secrets.NEON_PROJECT_ID }}
        run: |
          # Create test branch
          BRANCH_RESPONSE=$(curl -s -X POST \
            "https://console.neon.tech/api/v2/projects/$NEON_PROJECT_ID/branches" \
            -H "Authorization: Bearer $NEON_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{"branch": {"name": "ci/migration-test-${{ github.sha }}"}, "endpoints": [{"type": "read_write"}]}')

          echo "MIGRATION_BRANCH_ID=$(echo $BRANCH_RESPONSE | jq -r '.branch.id')" >> $GITHUB_ENV
          echo "DATABASE_URL_DIRECT=$(echo $BRANCH_RESPONSE | jq -r '.connection_uris[0].connection_uri')" >> $GITHUB_ENV

      - name: Test migration on branch
        run: |
          alembic upgrade head
          alembic downgrade -1
          alembic upgrade head

      - name: Apply to production
        env:
          DATABASE_URL_DIRECT: ${{ secrets.DATABASE_URL_DIRECT }}
        run: |
          alembic upgrade head

      - name: Cleanup migration branch
        if: always()
        env:
          NEON_API_KEY: ${{ secrets.NEON_API_KEY }}
          NEON_PROJECT_ID: ${{ secrets.NEON_PROJECT_ID }}
        run: |
          curl -X DELETE \
            "https://console.neon.tech/api/v2/projects/$NEON_PROJECT_ID/branches/$MIGRATION_BRANCH_ID" \
            -H "Authorization: Bearer $NEON_API_KEY"
```

## Best Practices

1. **Always test on branch first**: Never migrate production without testing
2. **Keep migrations small**: One logical change per migration
3. **Make migrations reversible**: Always implement `downgrade()`
4. **Use transactions**: Migrations run in transactions by default
5. **Avoid data loss**: Be careful with `DROP` operations
6. **Document breaking changes**: Note in commit message if migration is breaking
7. **Version control**: Commit migration files with related code changes
8. **Backup before major migrations**: Create a branch as backup point

## Troubleshooting

### Migration fails on branch

```bash
# Reset branch to parent state
neonctl branches reset migration/feature --parent main

# Or delete and recreate
neonctl branches delete migration/feature
neonctl branches create --name migration/feature
```

### Conflict with existing data

```python
# Use batch processing for large data migrations
def upgrade() -> None:
    connection = op.get_bind()

    # Process in batches
    batch_size = 1000
    offset = 0

    while True:
        result = connection.execute(
            sa.text(f"SELECT id FROM users LIMIT {batch_size} OFFSET {offset}")
        )
        rows = result.fetchall()

        if not rows:
            break

        for row in rows:
            connection.execute(
                sa.text("UPDATE users SET status = 'active' WHERE id = :id"),
                {"id": row[0]}
            )

        offset += batch_size
```
