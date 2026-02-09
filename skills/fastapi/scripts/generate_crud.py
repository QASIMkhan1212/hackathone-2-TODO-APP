#!/usr/bin/env python3
"""
FastAPI CRUD Generator
Generates complete CRUD operations for a model
"""

import sys
from pathlib import Path


def to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case"""
    import re
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def generate_crud(model_name: str, fields: list, output_dir: str = "app"):
    """Generate CRUD operations for a model"""

    base_path = Path(output_dir)
    model_snake = to_snake_case(model_name)

    # Generate schema
    schema_content = f'''from pydantic import BaseModel
from typing import Optional

class {model_name}Base(BaseModel):
'''

    for field_name, field_type in fields:
        nullable = "Optional[" if field_type.endswith("?") else ""
        clean_type = field_type.rstrip("?")
        schema_content += f'    {field_name}: {nullable}{clean_type}{"]" if nullable else ""}\n'

    schema_content += f'''

class {model_name}Create({model_name}Base):
    pass

class {model_name}Update({model_name}Base):
    pass

class {model_name}({model_name}Base):
    id: int

    class Config:
        from_attributes = True
'''

    schema_file = base_path / "schemas" / f"{model_snake}.py"
    schema_file.parent.mkdir(parents=True, exist_ok=True)
    schema_file.write_text(schema_content, encoding='utf-8')
    print(f"[OK] Created schema: {schema_file}")

    # Generate endpoint
    endpoint_content = f'''from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.{model_snake} import {model_name}, {model_name}Create, {model_name}Update

router = APIRouter()

# In-memory storage (replace with database in production)
{model_snake}_db = []

@router.get("/", response_model=List[{model_name}])
async def read_{model_snake}s(skip: int = 0, limit: int = 100):
    """Get all {model_snake}s"""
    return {model_snake}_db[skip : skip + limit]

@router.post("/", response_model={model_name}, status_code=201)
async def create_{model_snake}({model_snake}: {model_name}Create):
    """Create a new {model_snake}"""
    new_{model_snake} = {model_name}(id=len({model_snake}_db) + 1, **{model_snake}.dict())
    {model_snake}_db.append(new_{model_snake})
    return new_{model_snake}

@router.get("/{{item_id}}", response_model={model_name})
async def read_{model_snake}(item_id: int):
    """Get a specific {model_snake} by ID"""
    for item in {model_snake}_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="{model_name} not found")

@router.put("/{{item_id}}", response_model={model_name})
async def update_{model_snake}(item_id: int, {model_snake}_update: {model_name}Update):
    """Update a {model_snake}"""
    for idx, item in enumerate({model_snake}_db):
        if item.id == item_id:
            updated_item = {model_name}(id=item_id, **{model_snake}_update.dict())
            {model_snake}_db[idx] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="{model_name} not found")

@router.delete("/{{item_id}}")
async def delete_{model_snake}(item_id: int):
    """Delete a {model_snake}"""
    for idx, item in enumerate({model_snake}_db):
        if item.id == item_id:
            {model_snake}_db.pop(idx)
            return {{"message": "{model_name} deleted successfully"}}
    raise HTTPException(status_code=404, detail="{model_name} not found")
'''

    endpoint_file = base_path / "api" / "v1" / "endpoints" / f"{model_snake}.py"
    endpoint_file.parent.mkdir(parents=True, exist_ok=True)
    endpoint_file.write_text(endpoint_content, encoding='utf-8')
    print(f"[OK] Created endpoint: {endpoint_file}")

    # Instructions for adding to api.py
    print(f"\n[NOTE] Add to app/api/v1/api.py:")
    print(f"from app.api.v1.endpoints import {model_snake}")
    print(f'api_router.include_router({model_snake}.router, prefix="/{model_snake}s", tags=["{model_snake}s"])')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_crud.py <ModelName> [field:type field:type ...]")
        print("Example: python generate_crud.py User name:str email:str age:int is_active:bool")
        print("         python generate_crud.py Product name:str price:float description:str?")
        print("\nTypes: str, int, float, bool (add ? for Optional)")
        sys.exit(1)

    model_name = sys.argv[1]
    fields = []

    for arg in sys.argv[2:]:
        if ":" in arg:
            field_name, field_type = arg.split(":", 1)
            fields.append((field_name, field_type))

    if not fields:
        print("[WARNING] No fields provided. Using default fields: name:str, description:str?")
        fields = [("name", "str"), ("description", "str?")]

    generate_crud(model_name, fields)
    print(f"\n[SUCCESS] CRUD operations for '{model_name}' generated successfully!")
