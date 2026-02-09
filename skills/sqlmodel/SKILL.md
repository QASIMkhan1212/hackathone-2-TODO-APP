---
name: sqlmodel
description: SQLModel ORM for Python combining SQLAlchemy and Pydantic. Use when users want to (1) define database models with validation, (2) create unified schemas for FastAPI, (3) implement CRUD operations, (4) set up relationships between models, (5) use async database operations, (6) integrate with FastAPI endpoints, (7) handle migrations with Alembic. Triggers on mentions of "sqlmodel", "SQLModel", database models with Pydantic, or FastAPI database integration.
---

# SQLModel

Modern Python ORM combining SQLAlchemy power with Pydantic validation.

## Installation

```bash
pip install sqlmodel
# For async support
pip install sqlmodel aiosqlite  # SQLite
pip install sqlmodel asyncpg    # PostgreSQL
```

## Basic Model Definition

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=100, index=True)
    email: str = Field(unique=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Field Options

| Option | Description |
|--------|-------------|
| `primary_key=True` | Mark as primary key |
| `default=value` | Default value |
| `default_factory=func` | Default factory function |
| `nullable=True` | Allow NULL values |
| `unique=True` | Unique constraint |
| `index=True` | Create index |
| `foreign_key="table.column"` | Foreign key reference |
| `min_length`, `max_length` | String length validation |
| `ge`, `le`, `gt`, `lt` | Numeric validation |

## Database Setup

### Sync Engine

```python
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///database.db"
# DATABASE_URL = "postgresql://user:pass@localhost/dbname"

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

### Async Engine

```python
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///database.db"
# DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/dbname"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async with async_session() as session:
        yield session
```

## CRUD Operations

### Create

```python
from sqlmodel import Session

def create_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# Usage
user = User(name="John", email="john@example.com")
created = create_user(session, user)
```

### Read

```python
from sqlmodel import Session, select

def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)

def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def get_users(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> list[User]:
    statement = select(User)
    if active_only:
        statement = statement.where(User.is_active == True)
    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()
```

### Update

```python
def update_user(
    session: Session,
    user_id: int,
    user_data: dict,
) -> User | None:
    user = session.get(User, user_id)
    if not user:
        return None
    for key, value in user_data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
```

### Delete

```python
def delete_user(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True
```

## Schema Separation (API vs DB)

```python
from sqlmodel import SQLModel, Field

# Base model (shared fields)
class UserBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    email: str

# Database model
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)

# API models
class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    is_active: bool

class UserUpdate(SQLModel):
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None
```

## FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/users/", response_model=UserRead)
def create_user_endpoint(
    user: UserCreate,
    session: Session = Depends(get_session),
):
    # Check existing
    existing = get_user_by_email(session, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    return create_user(session, db_user)

@app.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=list[UserRead])
def read_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    return get_users(session, skip=skip, limit=limit)

@app.patch("/users/{user_id}", response_model=UserRead)
def update_user_endpoint(
    user_id: int,
    user: UserUpdate,
    session: Session = Depends(get_session),
):
    db_user = update_user(session, user_id, user.model_dump(exclude_unset=True))
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}")
def delete_user_endpoint(user_id: int, session: Session = Depends(get_session)):
    if not delete_user(session, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}
```

## Queries

### Filtering

```python
from sqlmodel import select, or_, and_

# Basic filter
statement = select(User).where(User.is_active == True)

# Multiple conditions
statement = select(User).where(
    User.is_active == True,
    User.name.contains("john"),
)

# OR conditions
statement = select(User).where(
    or_(User.name == "John", User.name == "Jane")
)

# AND with OR
statement = select(User).where(
    and_(
        User.is_active == True,
        or_(User.role == "admin", User.role == "moderator"),
    )
)
```

### Ordering & Pagination

```python
from sqlmodel import select, col

# Order by
statement = select(User).order_by(User.created_at.desc())
statement = select(User).order_by(col(User.name).asc())

# Pagination
statement = select(User).offset(10).limit(20)
```

### Aggregations

```python
from sqlmodel import select, func

# Count
statement = select(func.count(User.id))
count = session.exec(statement).one()

# Count with filter
statement = select(func.count(User.id)).where(User.is_active == True)
```

## Common Patterns

- **Relationships**: See [references/relationships.md](references/relationships.md)
- **Async Operations**: See [references/async-patterns.md](references/async-patterns.md)
- **Migrations**: See [references/migrations.md](references/migrations.md)

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/generate_model.py` | Generate SQLModel from table spec |
| `scripts/generate_crud.py` | Generate CRUD operations for model |
| `scripts/setup_database.py` | Initialize database configuration |
