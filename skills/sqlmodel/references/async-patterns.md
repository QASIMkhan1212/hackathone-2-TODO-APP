# SQLModel Async Patterns

## Async Setup

### Database Configuration

```python
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# SQLite (use aiosqlite)
DATABASE_URL = "sqlite+aiosqlite:///./database.db"

# PostgreSQL (use asyncpg)
# DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"

# MySQL (use aiomysql)
# DATABASE_URL = "mysql+aiomysql://user:password@localhost:3306/dbname"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Log SQL queries
    future=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
```

### Database Initialization

```python
async def create_db_and_tables():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def drop_db_and_tables():
    """Drop all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
```

### Session Dependency

```python
from typing import AsyncGenerator

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for async session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
```

---

## Async CRUD Operations

### Create

```python
from sqlmodel import SQLModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)

async def create_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# Bulk create
async def create_users(session: AsyncSession, users: list[User]) -> list[User]:
    session.add_all(users)
    await session.commit()
    for user in users:
        await session.refresh(user)
    return users
```

### Read

```python
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_user(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)

async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    result = await session.exec(statement)
    return result.first()

async def get_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[User]:
    statement = select(User).offset(skip).limit(limit)
    result = await session.exec(statement)
    return result.all()

async def count_users(session: AsyncSession) -> int:
    from sqlmodel import func
    statement = select(func.count(User.id))
    result = await session.exec(statement)
    return result.one()
```

### Update

```python
async def update_user(
    session: AsyncSession,
    user_id: int,
    user_data: dict,
) -> User | None:
    user = await session.get(User, user_id)
    if not user:
        return None

    for key, value in user_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# Bulk update
async def deactivate_users(
    session: AsyncSession,
    user_ids: list[int],
) -> int:
    from sqlalchemy import update
    statement = (
        update(User)
        .where(User.id.in_(user_ids))
        .values(is_active=False)
    )
    result = await session.exec(statement)
    await session.commit()
    return result.rowcount
```

### Delete

```python
async def delete_user(session: AsyncSession, user_id: int) -> bool:
    user = await session.get(User, user_id)
    if not user:
        return False

    await session.delete(user)
    await session.commit()
    return True

# Bulk delete
async def delete_inactive_users(session: AsyncSession) -> int:
    from sqlalchemy import delete
    statement = delete(User).where(User.is_active == False)
    result = await session.exec(statement)
    await session.commit()
    return result.rowcount
```

---

## Async Relationships

### Eager Loading with Async

```python
from sqlalchemy.orm import selectinload
from sqlmodel import select

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    members: list["User"] = Relationship(back_populates="team")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="members")

async def get_team_with_members(
    session: AsyncSession,
    team_id: int,
) -> Team | None:
    statement = (
        select(Team)
        .where(Team.id == team_id)
        .options(selectinload(Team.members))
    )
    result = await session.exec(statement)
    return result.first()

async def get_user_with_team(
    session: AsyncSession,
    user_id: int,
) -> User | None:
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.team))
    )
    result = await session.exec(statement)
    return result.first()
```

---

## FastAPI Async Integration

### Complete Example

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager

# Models
class UserBase(SQLModel):
    name: str
    email: str

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_active: bool = Field(default=True)

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    is_active: bool

class UserUpdate(SQLModel):
    name: str | None = None
    email: str | None = None
    is_active: bool | None = None

# App with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# Endpoints
@app.post("/users/", response_model=UserRead)
async def create_user_endpoint(
    user: UserCreate,
    session: AsyncSession = Depends(get_session),
):
    # Check existing
    existing = await get_user_by_email(session, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User.model_validate(user)
    return await create_user(session, db_user)

@app.get("/users/{user_id}", response_model=UserRead)
async def read_user_endpoint(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    user = await get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=list[UserRead])
async def read_users_endpoint(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    return await get_users(session, skip=skip, limit=limit)

@app.patch("/users/{user_id}", response_model=UserRead)
async def update_user_endpoint(
    user_id: int,
    user: UserUpdate,
    session: AsyncSession = Depends(get_session),
):
    db_user = await update_user(
        session,
        user_id,
        user.model_dump(exclude_unset=True),
    )
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.delete("/users/{user_id}")
async def delete_user_endpoint(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    if not await delete_user(session, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}
```

---

## Transactions

### Manual Transaction Control

```python
async def transfer_funds(
    session: AsyncSession,
    from_id: int,
    to_id: int,
    amount: float,
):
    async with session.begin():
        from_account = await session.get(Account, from_id)
        to_account = await session.get(Account, to_id)

        if not from_account or not to_account:
            raise ValueError("Account not found")

        if from_account.balance < amount:
            raise ValueError("Insufficient funds")

        from_account.balance -= amount
        to_account.balance += amount

        session.add(from_account)
        session.add(to_account)
        # Commit happens automatically at end of context
```

### Nested Transactions (Savepoints)

```python
async def complex_operation(session: AsyncSession):
    async with session.begin():
        # Main transaction
        user = User(name="Test", email="test@example.com")
        session.add(user)

        try:
            async with session.begin_nested():
                # Savepoint
                profile = Profile(user_id=user.id, bio="Test")
                session.add(profile)
                # If this fails, only profile is rolled back
        except Exception:
            pass  # Continue with main transaction

        # Main transaction continues
        await session.commit()
```

---

## Connection Pooling

### PostgreSQL Configuration

```python
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/db",
    pool_size=20,           # Number of connections to keep open
    max_overflow=10,        # Extra connections when pool is exhausted
    pool_timeout=30,        # Seconds to wait for connection
    pool_recycle=1800,      # Recycle connections after N seconds
    pool_pre_ping=True,     # Test connections before using
)
```

---

## Testing Async Code

```python
import pytest
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest.fixture
async def async_session():
    """Fixture for async test session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session

    await engine.dispose()

@pytest.mark.asyncio
async def test_create_user(async_session: AsyncSession):
    user = User(name="Test", email="test@example.com")
    result = await create_user(async_session, user)

    assert result.id is not None
    assert result.name == "Test"

@pytest.mark.asyncio
async def test_get_user(async_session: AsyncSession):
    # Create
    user = User(name="Test", email="test@example.com")
    created = await create_user(async_session, user)

    # Get
    fetched = await get_user(async_session, created.id)
    assert fetched is not None
    assert fetched.email == "test@example.com"
```
