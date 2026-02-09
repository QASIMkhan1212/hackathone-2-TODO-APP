# MCP Resources Reference

## Overview

Resources expose read-only data to AI applications, similar to GET endpoints in REST APIs. They provide structured access to files, database records, API responses, and other data sources.

## Basic Resource Definition

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ResourceServer")

@mcp.resource("config://settings")
def get_settings() -> dict:
    """Get application settings."""
    return {
        "version": "1.0.0",
        "environment": "production",
    }
```

## Resource URI Patterns

### Static URI

```python
@mcp.resource("config://app/settings")
def app_settings() -> dict:
    """Fixed URI resource."""
    return {"key": "value"}
```

### Parameterized URI

```python
@mcp.resource("file://documents/{filename}")
def read_document(filename: str) -> str:
    """URI with parameter."""
    with open(f"documents/{filename}") as f:
        return f.read()

@mcp.resource("api://users/{user_id}/profile")
def user_profile(user_id: str) -> dict:
    """Multiple path segments with parameter."""
    return database.get_user(user_id)
```

### Multiple Parameters

```python
@mcp.resource("db://{database}/{table}/{id}")
def get_record(database: str, table: str, id: str) -> dict:
    """Resource with multiple parameters."""
    return db_client.get(database, table, id)
```

## URI Schemes

Common URI scheme patterns:

| Scheme | Use Case | Example |
|--------|----------|---------|
| `file://` | Local files | `file://docs/{name}` |
| `config://` | Configuration | `config://app/settings` |
| `db://` | Database records | `db://users/{id}` |
| `api://` | API responses | `api://weather/{city}` |
| `cache://` | Cached data | `cache://session/{key}` |
| `custom://` | Custom data | `custom://anything` |

## Return Types

### String Content

```python
@mcp.resource("file://readme")
def get_readme() -> str:
    """Return plain text."""
    return "# README\n\nWelcome to the project."
```

### Dictionary/JSON

```python
@mcp.resource("api://status")
def get_status() -> dict:
    """Return JSON-serializable dict."""
    return {
        "status": "healthy",
        "uptime": 3600,
        "version": "2.0.0",
    }
```

### List

```python
@mcp.resource("db://users")
def list_users() -> list[dict]:
    """Return list of items."""
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
```

### Pydantic Models

```python
from pydantic import BaseModel

class ServerInfo(BaseModel):
    name: str
    version: str
    capabilities: list[str]

@mcp.resource("config://server")
def server_info() -> ServerInfo:
    """Return Pydantic model as JSON."""
    return ServerInfo(
        name="MyServer",
        version="1.0.0",
        capabilities=["tools", "resources"],
    )
```

### Binary Data

```python
@mcp.resource("file://images/{name}")
def get_image(name: str) -> bytes:
    """Return binary content."""
    with open(f"images/{name}", "rb") as f:
        return f.read()
```

## Async Resources

```python
@mcp.resource("api://weather/{city}")
async def get_weather(city: str) -> dict:
    """Async resource fetching external data."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/{city}"
        )
        return response.json()
```

## Resource with Context

```python
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

@mcp.resource("db://records/{id}")
async def get_record(
    id: str,
    ctx: Context[ServerSession, AppContext]
) -> dict:
    """Resource with lifespan context access."""
    app = ctx.request_context.lifespan_context
    return await app.db.get_record(id)
```

## Resource Templates

Resources can define templates for dynamic discovery:

```python
from mcp.types import ResourceTemplate

@mcp.resource("db://tables/{table}/rows/{id}")
def get_row(table: str, id: str) -> dict:
    """Row from any table."""
    return database.query(f"SELECT * FROM {table} WHERE id = %s", [id])

# The template is automatically exposed:
# URI Template: db://tables/{table}/rows/{id}
# Parameters: table (string), id (string)
```

## Resource Patterns

### Configuration Resource

```python
import os
import json

@mcp.resource("config://environment")
def environment_config() -> dict:
    """Expose environment configuration."""
    return {
        "env": os.getenv("ENV", "development"),
        "debug": os.getenv("DEBUG", "false") == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }

@mcp.resource("config://features")
def feature_flags() -> dict:
    """Expose feature flags."""
    with open("features.json") as f:
        return json.load(f)
```

### File System Resources

```python
import os
from pathlib import Path

@mcp.resource("file://list/{directory}")
def list_directory(directory: str) -> list[dict]:
    """List files in a directory."""
    path = Path(directory)
    if not path.is_dir():
        return []

    return [
        {
            "name": f.name,
            "type": "directory" if f.is_dir() else "file",
            "size": f.stat().st_size if f.is_file() else None,
        }
        for f in path.iterdir()
    ]

@mcp.resource("file://content/{path:path}")
def read_file(path: str) -> str:
    """Read file content."""
    with open(path) as f:
        return f.read()
```

### Database Resources

```python
@mcp.resource("db://schema")
async def database_schema() -> dict:
    """Get database schema."""
    tables = await db.fetch_all("""
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
    """)
    return {"tables": tables}

@mcp.resource("db://tables/{table}")
async def table_data(table: str) -> list[dict]:
    """Get all rows from a table."""
    # Sanitize table name
    if not table.isalnum():
        raise ValueError("Invalid table name")
    return await db.fetch_all(f"SELECT * FROM {table} LIMIT 100")
```

### API Aggregation

```python
@mcp.resource("api://dashboard")
async def dashboard_data() -> dict:
    """Aggregate data from multiple sources."""
    import asyncio

    users, orders, revenue = await asyncio.gather(
        get_user_count(),
        get_order_count(),
        get_total_revenue(),
    )

    return {
        "users": users,
        "orders": orders,
        "revenue": revenue,
        "timestamp": datetime.now().isoformat(),
    }
```

### Cached Resources

```python
import time

_cache = {}
CACHE_TTL = 300  # 5 minutes

@mcp.resource("api://expensive/{key}")
async def cached_resource(key: str) -> dict:
    """Resource with caching."""
    now = time.time()

    if key in _cache:
        data, timestamp = _cache[key]
        if now - timestamp < CACHE_TTL:
            return data

    # Fetch fresh data
    data = await fetch_expensive_data(key)
    _cache[key] = (data, now)

    return data
```

## Error Handling

```python
from mcp.types import McpError, ErrorCode

@mcp.resource("file://secure/{path}")
def secure_file(path: str) -> str:
    """Resource with error handling."""
    # Validate path
    if ".." in path:
        raise McpError(
            ErrorCode.INVALID_PARAMS,
            "Path traversal not allowed"
        )

    full_path = f"/secure/{path}"

    if not os.path.exists(full_path):
        raise McpError(
            ErrorCode.NOT_FOUND,
            f"File not found: {path}"
        )

    with open(full_path) as f:
        return f.read()
```

## Best Practices

1. **URI Design**: Use clear, hierarchical URI schemes
2. **Read-Only**: Resources should not modify state
3. **Idempotent**: Same URI always returns consistent data
4. **Caching**: Cache expensive resources when appropriate
5. **Validation**: Validate parameters before processing
6. **Error Messages**: Return helpful error information
7. **Documentation**: Use docstrings to describe resource content
8. **Security**: Validate paths and prevent unauthorized access
