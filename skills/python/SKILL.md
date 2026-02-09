---
name: python
description: Python development assistant for building modern applications. Use when users want to (1) create new Python projects with proper structure, (2) implement classes, functions, and modules, (3) set up virtual environments and dependency management, (4) write tests with pytest, (5) configure linting and formatting (ruff, black, mypy), (6) create CLI applications with click/typer, (7) package and distribute Python libraries, (8) implement async/await patterns. Triggers on mentions of "python", "pip", "poetry", "pytest", "pydantic", or Python package development.
---

# Python

Modern Python development with best practices for 3.10+.

## Project Setup

### Create New Project

```bash
# Using uv (recommended - fast)
uv init my-project
cd my-project
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Using poetry
poetry new my-project
cd my-project
poetry install

# Traditional
mkdir my-project && cd my-project
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Project Structure

```
my-project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── main.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── pyproject.toml
├── README.md
└── .gitignore
```

## pyproject.toml (Modern Standard)

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "Project description"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1",
    "mypy>=1.0",
]

[project.scripts]
my-cli = "my_project.main:cli"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.10"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=src"
```

## Type Hints (Required for Modern Python)

```python
from typing import Optional, List, Dict, Any, Callable
from collections.abc import Sequence, Mapping, Iterator

# Basic types
def greet(name: str) -> str:
    return f"Hello, {name}"

# Optional and Union
def process(value: str | None = None) -> str:
    return value or "default"

# Collections
def get_items() -> list[dict[str, Any]]:
    return [{"id": 1}]

# Callable
def apply(func: Callable[[int], int], value: int) -> int:
    return func(value)

# Generics
from typing import TypeVar, Generic

T = TypeVar("T")

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
```

## Pydantic Models

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    created_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = []

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("Invalid email")
        return v.lower()

# Usage
user = User(id=1, name="John", email="john@example.com")
user_dict = user.model_dump()
user_json = user.model_dump_json()
```

## Async/Await Patterns

```python
import asyncio
from typing import Any

async def fetch_data(url: str) -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def process_items(items: list[str]) -> list[str]:
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks)

# Running async code
async def main() -> None:
    result = await fetch_data("https://api.example.com")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling

```python
from typing import Never

class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, code: str = "UNKNOWN") -> None:
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str) -> None:
        super().__init__(f"{resource} {id} not found", "NOT_FOUND")

# Usage with context
def get_user(user_id: str) -> User:
    user = db.get(user_id)
    if not user:
        raise NotFoundError("User", user_id)
    return user

# Result pattern (alternative)
from dataclasses import dataclass

@dataclass
class Result[T]:
    value: T | None = None
    error: str | None = None

    @property
    def is_ok(self) -> bool:
        return self.error is None
```

## Testing with Pytest

```python
# tests/conftest.py
import pytest
from my_project.database import Database

@pytest.fixture
def db() -> Database:
    """Provide test database."""
    return Database(":memory:")

@pytest.fixture
def sample_user() -> dict:
    return {"id": 1, "name": "Test User"}

# tests/test_main.py
import pytest
from my_project.main import create_user, get_user

def test_create_user(db, sample_user):
    user = create_user(db, sample_user)
    assert user.id == 1
    assert user.name == "Test User"

def test_get_user_not_found(db):
    with pytest.raises(NotFoundError):
        get_user(db, "nonexistent")

@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected

@pytest.mark.asyncio
async def test_async_function():
    result = await fetch_data("https://api.example.com")
    assert "data" in result
```

**Detailed testing patterns**: See [references/testing.md](references/testing.md)

## CLI Applications

```python
# Using Typer (recommended)
import typer
from typing import Annotated

app = typer.Typer(help="My CLI application")

@app.command()
def greet(
    name: Annotated[str, typer.Argument(help="Name to greet")],
    formal: Annotated[bool, typer.Option("--formal", "-f")] = False,
) -> None:
    """Greet someone."""
    if formal:
        print(f"Good day, {name}.")
    else:
        print(f"Hello, {name}!")

@app.command()
def version() -> None:
    """Show version."""
    print("1.0.0")

if __name__ == "__main__":
    app()
```

## Common Patterns

- **Design patterns**: See [references/patterns.md](references/patterns.md)
- **Packaging & distribution**: See [references/packaging.md](references/packaging.md)
- **Testing strategies**: See [references/testing.md](references/testing.md)

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/scaffold_project.py` | Generate new Python project |
| `scripts/add_cli.py` | Add CLI scaffolding with Typer |
| `scripts/setup_testing.py` | Configure pytest with coverage |

## Commands Reference

```bash
# Virtual environment
python -m venv .venv
source .venv/bin/activate

# Dependencies
pip install -e ".[dev]"
uv pip install -e ".[dev]"

# Testing
pytest
pytest --cov=src --cov-report=html
pytest -k "test_specific"

# Linting & Formatting
ruff check .
ruff format .
mypy src/

# Build & Publish
python -m build
twine upload dist/*
```
