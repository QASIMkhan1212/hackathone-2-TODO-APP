---
name: fastapi
description: "Comprehensive FastAPI web framework assistant for building modern Python APIs. Use when working with FastAPI projects for: (1) Creating new FastAPI applications, (2) Generating CRUD endpoints, (3) Adding authentication (JWT, OAuth2), (4) Setting up database integration (SQLAlchemy, Tortoise ORM), (5) Creating tests, (6) Adding deployment configurations, (7) Implementing best practices, (8) Debugging FastAPI applications, or any other FastAPI-related development tasks"
---

# FastAPI Development Assistant

## Overview

FastAPI is a modern, fast (high-performance) Python web framework for building APIs. This skill provides automated scaffolding, code generation, and best practices guidance for FastAPI development.

## Quick Start

### Create New Project
```bash
python scripts/scaffold_project.py <project-name> [--db] [--auth]
```

Options:
- `--db`: Include database setup (SQLAlchemy, PostgreSQL)
- `--auth`: Include JWT authentication

Example:
```bash
python scripts/scaffold_project.py my-api --db --auth
```

### Generate CRUD Endpoints
```bash
python scripts/generate_crud.py <ModelName> [field:type field:type ...]
```

Example:
```bash
python scripts/generate_crud.py Product name:str price:float description:str? stock:int
```

Field types: `str`, `int`, `float`, `bool` (add `?` for Optional)

### Add Authentication
```bash
python scripts/add_auth.py
```

This adds JWT-based authentication with login endpoint and protected routes.

## Workflows

### 1. Starting a New FastAPI Project

**Steps:**

1. **Scaffold the project** with appropriate options:
   ```bash
   python scripts/scaffold_project.py my-api --db --auth
   ```

2. **Review the generated structure**:
   ```
   my-api/
   ├── app/
   │   ├── api/v1/
   │   │   ├── api.py
   │   │   └── endpoints/
   │   ├── core/
   │   │   └── config.py
   │   ├── models/
   │   ├── schemas/
   │   ├── crud/
   │   └── main.py
   ├── tests/
   ├── requirements.txt
   └── .env.example
   ```

3. **Set up environment**:
   ```bash
   cd my-api
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### 2. Adding New Endpoints

**For simple endpoints**, manually create them following this pattern:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_items():
    return {"message": "List of items"}

@router.post("/")
async def create_item(item: ItemCreate):
    # Create logic
    return {"message": "Item created"}
```

**For CRUD operations**, use the generator:

1. **Generate CRUD endpoints**:
   ```bash
   python scripts/generate_crud.py Product name:str price:float description:str? category:str
   ```

2. **Register the router** in `app/api/v1/api.py`:
   ```python
   from app.api.v1.endpoints import products

   api_router.include_router(products.router, prefix="/products", tags=["products"])
   ```

3. **Test the endpoints** at http://localhost:8000/docs

### 3. Database Integration

**Basic Setup:**

1. **Install dependencies**:
   ```bash
   pip install sqlalchemy alembic psycopg2-binary
   ```

2. **Configure database** in `app/core/config.py`:
   ```python
   DATABASE_URL: str = "postgresql://user:password@localhost/dbname"
   ```

3. **Create database models** in `app/models/`:
   ```python
   from sqlalchemy import Column, Integer, String
   from app.db.session import Base

   class Product(Base):
       __tablename__ = "products"

       id = Column(Integer, primary_key=True, index=True)
       name = Column(String, index=True)
       price = Column(Integer)
   ```

4. **Create CRUD operations** in `app/crud/`:
   See [database-patterns.md](references/database-patterns.md) for detailed patterns

5. **Set up Alembic migrations**:
   ```bash
   alembic init alembic
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

**For comprehensive database patterns**, see [database-patterns.md](references/database-patterns.md):
- SQLAlchemy setup and models
- Alembic migrations
- Async database operations (Tortoise ORM, databases library)
- Connection pooling
- Transaction management
- Query optimization
- Testing with databases

### 4. Authentication & Authorization

**Quick Setup:**

Run the authentication script:
```bash
python scripts/add_auth.py
```

This creates:
- JWT token generation and verification
- Login endpoint (`/api/v1/auth/login`)
- User authentication dependencies
- Password hashing utilities

**Using Authentication in Routes:**

```python
from app.auth.dependencies import get_current_active_user

@router.get("/protected")
async def protected_route(current_user = Depends(get_current_active_user)):
    return {"message": f"Hello {current_user['username']}"}
```

**Test Credentials** (default):
- Username: `testuser`
- Password: `secret`

**Login Flow:**

1. POST to `/api/v1/auth/login` with credentials
2. Receive JWT token
3. Include token in requests: `Authorization: Bearer <token>`

### 5. Testing

**Create test file** `tests/test_api.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_create_item():
    response = client.post(
        "/api/v1/items/",
        json={"name": "Test", "price": 10.99}
    )
    assert response.status_code == 201
    assert "id" in response.json()

def test_protected_endpoint():
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "secret"}
    )
    token = login_response.json()["access_token"]

    # Access protected route
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

**Run tests**:
```bash
pytest tests/
```

### 6. Deployment

**Docker Configuration:**

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db/dbname
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Deploy:**
```bash
docker-compose up -d
```

## Common Patterns

### Request Validation

```python
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    age: int

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

    @validator('age')
    def age_valid(cls, v):
        if v < 18:
            raise ValueError('Must be 18 or older')
        return v
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Email sending logic
    pass

@router.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Notification will be sent"}
```

### File Upload

```python
from fastapi import File, UploadFile

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Process file
    return {"filename": file.filename, "size": len(contents)}
```

### Query Parameters

```python
from typing import Optional
from fastapi import Query

@router.get("/items/")
async def read_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=3)
):
    # Query logic
    return {"skip": skip, "limit": limit, "search": search}
```

### Error Handling

```python
from fastapi import HTTPException

@router.get("/items/{item_id}")
async def get_item(item_id: int):
    item = database.get(item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "Item-Not-Found"}
        )
    return item
```

### Response Models

```python
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: int
    email: str
    # password field excluded

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    user = get_user_from_db(user_id)  # Has password field
    return user  # Password automatically excluded
```

## Best Practices Reference

For comprehensive best practices including:
- Project structure conventions
- Configuration management
- Schema design patterns
- Dependency injection
- Error handling strategies
- Response model patterns
- Database session management
- Async operations
- Testing strategies
- CORS configuration
- Background tasks
- Logging
- Security patterns
- Performance optimization
- Documentation customization

See [best-practices.md](references/best-practices.md)

## Troubleshooting

### Common Issues

**1. Import errors after adding new endpoints:**
- Ensure `__init__.py` exists in all directories
- Check import paths match directory structure
- Restart uvicorn with `--reload`

**2. Database connection errors:**
- Verify DATABASE_URL in .env
- Check database is running
- Ensure database driver is installed (`psycopg2-binary` for PostgreSQL)

**3. Authentication not working:**
- Check SECRET_KEY is set in .env
- Verify token is included in headers: `Authorization: Bearer <token>`
- Ensure dependencies are installed: `python-jose`, `passlib`

**4. CORS errors:**
- Add allowed origins to `BACKEND_CORS_ORIGINS` in config
- Check CORSMiddleware is configured in main.py

**5. Validation errors:**
- Check Pydantic schema matches request data
- Use response.json() to see detailed error messages
- Verify field types (int vs str, required vs optional)

## Development Tips

1. **Use automatic API documentation** - FastAPI generates interactive docs at `/docs`
2. **Leverage type hints** - They enable automatic validation and documentation
3. **Separate concerns** - Keep models, schemas, and CRUD operations separate
4. **Use dependency injection** - Makes testing and code reuse easier
5. **Implement proper error handling** - Return meaningful HTTP status codes
6. **Use response models** - Automatically exclude sensitive data
7. **Test your endpoints** - Use TestClient for automated testing
8. **Follow RESTful conventions** - Use appropriate HTTP methods and status codes
9. **Version your API** - Use `/api/v1` prefix for future compatibility
10. **Document your endpoints** - Add docstrings and OpenAPI metadata

## Resources

### Generated Scripts
- `scripts/scaffold_project.py` - Project scaffolding
- `scripts/generate_crud.py` - CRUD endpoint generator
- `scripts/add_auth.py` - Authentication setup

### Reference Documentation
- `references/best-practices.md` - Comprehensive best practices
- `references/database-patterns.md` - Database integration patterns

### Official Documentation
- FastAPI Docs: https://fastapi.tiangolo.com
- Pydantic Docs: https://docs.pydantic.dev
- SQLAlchemy Docs: https://docs.sqlalchemy.org
- Uvicorn Docs: https://www.uvicorn.org

## Examples

### Complete CRUD with Database

```python
# models/item.py
from sqlalchemy import Column, Integer, String, Float
from app.db.session import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)

# schemas/item.py
from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    price: float

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    class Config:
        from_attributes = True

# crud/item.py
from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()

def create_item(db: Session, item: ItemCreate):
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# api/v1/endpoints/items.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.item import Item, ItemCreate
from app.crud import item as crud_item

router = APIRouter()

@router.get("/", response_model=list[Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_item.get_items(db, skip=skip, limit=limit)

@router.post("/", response_model=Item, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return crud_item.create_item(db, item)
```

This skill provides everything needed to build production-ready FastAPI applications efficiently.
