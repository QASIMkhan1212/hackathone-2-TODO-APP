# FastAPI Best Practices

## Project Structure

### Recommended Layout
```
project/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py          # Router aggregation
│   │       └── endpoints/      # Individual route files
│   ├── core/
│   │   ├── config.py          # Settings & configuration
│   │   └── security.py        # Security utilities
│   ├── models/                # Database models
│   ├── schemas/               # Pydantic schemas
│   ├── crud/                  # Database operations
│   ├── db/
│   │   ├── base.py           # Base model imports
│   │   └── session.py        # Database session
│   └── main.py               # FastAPI app instance
├── tests/
├── alembic/                   # Database migrations
├── .env
└── requirements.txt
```

## Configuration Management

### Use Pydantic Settings
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    SECRET_KEY: str
    BACKEND_CORS_ORIGINS: List[str] = []

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## Schema Design

### Separate Schemas for Different Operations
```python
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None

class UserInDB(UserBase):
    id: int
    hashed_password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True
```

## Dependency Injection

### Common Dependencies
```python
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    # Decode token and get user
    pass

# Use in routes
@router.get("/users/me")
async def read_user_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

## Error Handling

### Custom Exception Handlers
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class CustomException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=400,
        content={"message": exc.message, "name": exc.name}
    )
```

### HTTPException with Details
```python
raise HTTPException(
    status_code=404,
    detail="User not found",
    headers={"X-Error": "Custom header"}
)
```

## Response Models

### Use response_model for Validation
```python
@router.post("/users/", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    # Password won't be in response due to response_model
    return created_user
```

### Multiple Response Types
```python
from typing import Union

@router.get("/items/{item_id}", response_model=Union[Item, ErrorResponse])
async def get_item(item_id: int):
    pass
```

## Database Sessions

### Proper Session Management
```python
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage
@router.get("/users/")
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

## Async Operations

### When to Use Async
- Use `async def` for I/O-bound operations (database, external APIs)
- Use regular `def` for CPU-bound operations
- Don't mix async and sync database libraries

```python
# Good - Async with async database
@router.get("/users/")
async def get_users():
    users = await database.fetch_all(query)
    return users

# Good - Sync with sync database
@router.get("/users/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
```

## Testing

### Test Structure
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "secret"}
    )
    assert response.status_code == 201
    assert "id" in response.json()
```

### Testing with Authentication
```python
def test_protected_route():
    # Get token
    login_response = client.post(
        "/auth/login",
        data={"username": "test", "password": "secret"}
    )
    token = login_response.json()["access_token"]

    # Use token
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

## CORS Configuration

### Production-Ready CORS
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
```

## Background Tasks

### Using Background Tasks
```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Send email logic
    pass

@router.post("/send-notification/")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, "Welcome!")
    return {"message": "Email will be sent"}
```

## Logging

### Structured Logging
```python
import logging
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@router.post("/items/")
async def create_item(item: ItemCreate):
    logger.info(f"Creating item: {item.name}")
    # Create item
    logger.info(f"Item created with ID: {new_item.id}")
    return new_item
```

## Security

### Password Hashing
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### JWT Token Generation
```python
from datetime import datetime, timedelta
from jose import jwt

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

## Performance

### Query Optimization
```python
# Bad - N+1 queries
users = db.query(User).all()
for user in users:
    posts = user.posts  # Triggers additional query

# Good - Eager loading
from sqlalchemy.orm import joinedload
users = db.query(User).options(joinedload(User.posts)).all()
```

### Caching
```python
from functools import lru_cache

@lru_cache()
def get_settings():
    return Settings()

# Use in dependency
def get_db(settings: Settings = Depends(get_settings)):
    pass
```

## Documentation

### Custom OpenAPI Documentation
```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="Comprehensive API documentation",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "users",
            "description": "User management operations"
        },
        {
            "name": "items",
            "description": "Item operations"
        }
    ]
)
```

### Route Documentation
```python
@router.post(
    "/users/",
    response_model=User,
    status_code=201,
    summary="Create a new user",
    description="Create a new user with email and password",
    response_description="The created user"
)
async def create_user(user: UserCreate):
    """
    Create a user with all the information:

    - **email**: valid email address
    - **password**: strong password (min 8 characters)
    - **username**: unique username
    """
    return created_user
```
