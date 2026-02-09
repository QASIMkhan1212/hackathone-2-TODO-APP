#!/usr/bin/env python3
"""
FastAPI Project Scaffolder
Creates a new FastAPI project with best practices structure
"""

import sys
from pathlib import Path


def create_project_structure(project_name: str, include_db: bool = False, include_auth: bool = False):
    """Create a well-structured FastAPI project"""

    base_path = Path(project_name)

    # Create directory structure
    directories = [
        base_path,
        base_path / "app",
        base_path / "app" / "api",
        base_path / "app" / "api" / "v1",
        base_path / "app" / "api" / "v1" / "endpoints",
        base_path / "app" / "core",
        base_path / "app" / "models",
        base_path / "app" / "schemas",
        base_path / "app" / "crud",
        base_path / "app" / "db",
        base_path / "tests",
    ]

    if include_auth:
        directories.append(base_path / "app" / "auth")

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "__init__.py").touch()

    # Create main.py
    main_content = '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}
'''

    (base_path / "app" / "main.py").write_text(main_content, encoding='utf-8')

    # Create config.py
    config_content = '''from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Project"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()
'''

    (base_path / "app" / "core" / "config.py").write_text(config_content, encoding='utf-8')

    # Create API router
    api_router_content = '''from fastapi import APIRouter
from app.api.v1.endpoints import items

api_router = APIRouter()
api_router.include_router(items.router, prefix="/items", tags=["items"])
'''

    (base_path / "app" / "api" / "v1" / "api.py").write_text(api_router_content, encoding='utf-8')

    # Create example endpoint
    endpoint_content = '''from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.item import Item, ItemCreate

router = APIRouter()

# In-memory storage for demo
items_db = []

@router.get("/", response_model=List[Item])
async def read_items():
    return items_db

@router.post("/", response_model=Item, status_code=201)
async def create_item(item: ItemCreate):
    new_item = Item(id=len(items_db) + 1, **item.dict())
    items_db.append(new_item)
    return new_item

@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/{item_id}")
async def delete_item(item_id: int):
    for idx, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(idx)
            return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")
'''

    (base_path / "app" / "api" / "v1" / "endpoints" / "items.py").write_text(endpoint_content, encoding='utf-8')

    # Create schemas
    schema_content = '''from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
'''

    (base_path / "app" / "schemas" / "item.py").write_text(schema_content, encoding='utf-8')

    # Create requirements.txt
    requirements = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
    ]

    if include_db:
        requirements.extend([
            "sqlalchemy>=2.0.0",
            "alembic>=1.13.0",
            "psycopg2-binary>=2.9.0",  # PostgreSQL
        ])

    if include_auth:
        requirements.extend([
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "python-multipart>=0.0.6",
        ])

    (base_path / "requirements.txt").write_text("\n".join(requirements), encoding='utf-8')

    # Create .env.example
    env_content = '''PROJECT_NAME="FastAPI Project"
API_V1_STR="/api/v1"
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
'''

    if include_db:
        env_content += '''
DATABASE_URL="postgresql://user:password@localhost/dbname"
'''

    if include_auth:
        env_content += '''
SECRET_KEY="your-secret-key-here-change-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
'''

    (base_path / ".env.example").write_text(env_content, encoding='utf-8')

    # Create README.md
    readme_content = f'''# {project_name}

FastAPI project with best practices structure

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy .env.example to .env and update values:
```bash
cp .env.example .env
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

4. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
{project_name}/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   ├── core/
│   │   └── config.py
│   ├── models/
│   ├── schemas/
│   ├── crud/
│   └── main.py
└── tests/
```
'''

    (base_path / "README.md").write_text(readme_content, encoding='utf-8')

    print(f"[SUCCESS] FastAPI project '{project_name}' created successfully!")
    print(f"\nNext steps:")
    print(f"1. cd {project_name}")
    print(f"2. pip install -r requirements.txt")
    print(f"3. cp .env.example .env")
    print(f"4. uvicorn app.main:app --reload")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scaffold_project.py <project_name> [--db] [--auth]")
        sys.exit(1)

    project_name = sys.argv[1]
    include_db = "--db" in sys.argv
    include_auth = "--auth" in sys.argv

    create_project_structure(project_name, include_db, include_auth)
