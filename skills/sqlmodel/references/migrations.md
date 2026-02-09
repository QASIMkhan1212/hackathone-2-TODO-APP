# SQLModel Migrations with Alembic

## Setup

### Installation

```bash
pip install alembic
```

### Initialize Alembic

```bash
alembic init alembic
```

This creates:
```
alembic/
├── versions/          # Migration scripts
├── env.py             # Environment configuration
├── script.py.mako     # Migration template
└── README
alembic.ini            # Alembic configuration
```

---

## Configuration

### alembic.ini

```ini
[alembic]
script_location = alembic
prepend_sys_path = .

# Use environment variable for database URL
# sqlalchemy.url = driver://user:pass@localhost/dbname

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

### env.py (Sync)

```python
from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from sqlmodel import SQLModel

# Import all models to register them with SQLModel.metadata
from app.models import User, Team, Project  # noqa

config = context.config

# Load database URL from environment
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
```

### env.py (Async)

```python
import asyncio
from logging.config import fileConfig
import os

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from sqlmodel import SQLModel

# Import all models
from app.models import User, Team, Project  # noqa

config = context.config

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
```

---

## Common Commands

### Generate Migration

```bash
# Auto-generate from model changes
alembic revision --autogenerate -m "Add users table"

# Create empty migration
alembic revision -m "Custom migration"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade abc123

# Upgrade one step
alembic upgrade +1
```

### Rollback

```bash
# Downgrade one step
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade abc123

# Downgrade to beginning
alembic downgrade base
```

### View Status

```bash
# Current revision
alembic current

# Migration history
alembic history

# Show pending migrations
alembic history --indicate-current
```

---

## Migration Examples

### Create Table

```python
"""Create users table

Revision ID: abc123
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = 'abc123'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_name'), 'user', ['name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_name'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
```

### Add Column

```python
"""Add avatar_url to user

Revision ID: def456
Revises: abc123
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = 'def456'
down_revision: str = 'abc123'


def upgrade() -> None:
    op.add_column(
        'user',
        sa.Column('avatar_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('user', 'avatar_url')
```

### Add Foreign Key

```python
"""Add team relationship

Revision ID: ghi789
Revises: def456
"""
from alembic import op
import sqlalchemy as sa

revision: str = 'ghi789'
down_revision: str = 'def456'


def upgrade() -> None:
    # Create team table
    op.create_table(
        'team',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # Add foreign key to user
    op.add_column(
        'user',
        sa.Column('team_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_user_team_id',
        'user', 'team',
        ['team_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_user_team_id', 'user', type_='foreignkey')
    op.drop_column('user', 'team_id')
    op.drop_table('team')
```

### Data Migration

```python
"""Migrate user roles

Revision ID: jkl012
Revises: ghi789
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

revision: str = 'jkl012'
down_revision: str = 'ghi789'


def upgrade() -> None:
    # Add new column
    op.add_column(
        'user',
        sa.Column('role', sa.String(50), nullable=True)
    )

    # Migrate data
    bind = op.get_bind()
    session = Session(bind=bind)

    # Update existing users
    session.execute(
        sa.text("UPDATE user SET role = 'member' WHERE is_admin = false")
    )
    session.execute(
        sa.text("UPDATE user SET role = 'admin' WHERE is_admin = true")
    )
    session.commit()

    # Make column non-nullable
    op.alter_column('user', 'role', nullable=False)

    # Drop old column
    op.drop_column('user', 'is_admin')


def downgrade() -> None:
    op.add_column(
        'user',
        sa.Column('is_admin', sa.Boolean(), nullable=True)
    )

    bind = op.get_bind()
    session = Session(bind=bind)

    session.execute(
        sa.text("UPDATE user SET is_admin = true WHERE role = 'admin'")
    )
    session.execute(
        sa.text("UPDATE user SET is_admin = false WHERE role != 'admin'")
    )
    session.commit()

    op.alter_column('user', 'is_admin', nullable=False)
    op.drop_column('user', 'role')
```

---

## Best Practices

### 1. Always Review Auto-generated Migrations

```bash
# Generate
alembic revision --autogenerate -m "Description"

# Review the generated file in alembic/versions/
# Edit if necessary, then apply
alembic upgrade head
```

### 2. Test Migrations Both Ways

```bash
# Apply
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Re-apply
alembic upgrade head
```

### 3. Use Meaningful Revision Messages

```bash
# Good
alembic revision --autogenerate -m "Add user profile with avatar and bio"

# Bad
alembic revision --autogenerate -m "Update models"
```

### 4. Keep Models in Sync

```python
# app/models/__init__.py
from .user import User, UserCreate, UserRead, UserUpdate
from .team import Team, TeamCreate, TeamRead
from .project import Project

__all__ = [
    "User", "UserCreate", "UserRead", "UserUpdate",
    "Team", "TeamCreate", "TeamRead",
    "Project",
]
```

### 5. CI/CD Integration

```yaml
# GitHub Actions example
- name: Run migrations
  run: alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```
