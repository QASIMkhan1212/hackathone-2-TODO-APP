# FastAPI Database Patterns

## SQLAlchemy with FastAPI

### Database Setup

#### session.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### base.py (Import all models for Alembic)
```python
from app.db.session import Base
from app.models.user import User
from app.models.item import Item
# Import all models here
```

### Model Definition

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    items = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
```

### CRUD Operations

#### crud/user.py
```python
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.utils import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: dict):
    db_user = get_user(db, user_id)
    if db_user:
        for key, value in user_update.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
```

### Using CRUD in Endpoints

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.user import User, UserCreate
from app.crud import user as crud_user

router = APIRouter()

@router.post("/", response_model=User, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create_user(db=db, user=user)

@router.get("/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud_user.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
```

## Alembic Migrations

### Initial Setup

```bash
# Initialize Alembic
alembic init alembic

# Configure alembic/env.py
# Import your Base and set target_metadata
from app.db.base import Base
target_metadata = Base.metadata

# Configure database URL in alembic.ini or env.py
```

### Creating Migrations

```bash
# Auto-generate migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View current version
alembic current

# View migration history
alembic history
```

### Manual Migration Example

```python
"""Add users table

Revision ID: abc123
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

def downgrade():
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
```

## Async Database Operations

### Using databases library

```python
import databases
from app.core.config import settings

database = databases.Database(settings.DATABASE_URL)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
```

### Async CRUD

```python
from databases import Database

async def get_users(db: Database):
    query = "SELECT * FROM users"
    return await db.fetch_all(query)

async def create_user(db: Database, email: str, hashed_password: str):
    query = "INSERT INTO users(email, hashed_password) VALUES (:email, :password) RETURNING *"
    return await db.fetch_one(query, values={"email": email, "password": hashed_password})
```

## Tortoise ORM (Async Alternative)

### Setup

```python
from tortoise import Tortoise, fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    username = fields.CharField(max_length=50, unique=True)
    hashed_password = fields.CharField(max_length=128)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "users"

# Initialize in FastAPI
from tortoise.contrib.fastapi import register_tortoise

register_tortoise(
    app,
    db_url=settings.DATABASE_URL,
    modules={"models": ["app.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
```

### Tortoise CRUD

```python
# Create
user = await User.create(email="test@example.com", username="test")

# Read
user = await User.get(id=1)
users = await User.all()
user = await User.filter(email="test@example.com").first()

# Update
await User.filter(id=1).update(username="new_username")
user = await User.get(id=1)
user.username = "updated"
await user.save()

# Delete
await User.filter(id=1).delete()
user = await User.get(id=1)
await user.delete()

# Relations
user = await User.get(id=1).prefetch_related("items")
```

## Connection Pooling

### PostgreSQL with psycopg2

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set True for SQL logging
)
```

## Transaction Management

### Context Manager Approach

```python
from contextlib import contextmanager

@contextmanager
def get_db_transaction():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Usage
with get_db_transaction() as db:
    user = crud_user.create_user(db, user_data)
    item = crud_item.create_item(db, item_data, user_id=user.id)
```

### Nested Transactions

```python
from sqlalchemy.orm import Session

def complex_operation(db: Session):
    with db.begin_nested():  # Savepoint
        try:
            # Operations that might fail
            user = create_user(db, user_data)
            item = create_item(db, item_data)
        except Exception:
            # Rollback to savepoint
            raise
```

## Query Optimization

### Eager Loading

```python
from sqlalchemy.orm import joinedload, selectinload

# Joinedload (single query with JOIN)
users = db.query(User).options(joinedload(User.items)).all()

# Selectinload (separate query)
users = db.query(User).options(selectinload(User.items)).all()
```

### Pagination

```python
from fastapi import Query

@router.get("/users/", response_model=List[User])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users
```

### Filtering

```python
from typing import Optional

@router.get("/users/", response_model=List[User])
def read_users(
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if email:
        query = query.filter(User.email.contains(email))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.all()
```

## Database Testing

### Test Database Setup

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# In tests
from app.main import app
from app.db.session import get_db

app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

# Test
def test_create_user():
    response = client.post("/users/", json={"email": "test@test.com"})
    assert response.status_code == 201

# Cleanup
Base.metadata.drop_all(bind=engine)
```
