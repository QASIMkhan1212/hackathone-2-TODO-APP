# MCP Tools Reference

## Overview

Tools are functions that LLMs can call to perform actions. Unlike resources (read-only), tools can have side effects like modifying data, calling APIs, or executing commands.

## Basic Tool Definition

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ToolServer")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b
```

## Tool Decorators

### Simple Tool

```python
@mcp.tool()
def simple_tool(param: str) -> str:
    """A simple tool."""
    return f"Result: {param}"
```

### Tool with Custom Name

```python
@mcp.tool(name="custom_name")
def my_function(data: str) -> str:
    """Tool exposed as 'custom_name'."""
    return data
```

### Tool with Disabled Structured Output

```python
@mcp.tool(structured_output=False)
def raw_tool(query: str) -> str:
    """Tool returning raw text."""
    return "Raw text response"
```

## Parameter Types

### Primitive Types

```python
@mcp.tool()
def primitives(
    text: str,
    number: int,
    decimal: float,
    flag: bool,
) -> dict:
    """Tool with primitive parameters."""
    return {
        "text": text,
        "number": number,
        "decimal": decimal,
        "flag": flag,
    }
```

### Optional Parameters

```python
from typing import Optional

@mcp.tool()
def optional_params(
    required: str,
    optional: str = "default",
    maybe_none: Optional[int] = None,
) -> str:
    """Tool with optional parameters."""
    return f"{required}, {optional}, {maybe_none}"
```

### Complex Types

```python
from typing import List, Dict

@mcp.tool()
def complex_params(
    items: List[str],
    metadata: Dict[str, str],
) -> int:
    """Tool with complex parameters."""
    return len(items)
```

### Pydantic Models

```python
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=10, ge=1, le=100)
    filters: dict = Field(default_factory=dict)

@mcp.tool()
def search(params: SearchQuery) -> list[dict]:
    """Search with structured parameters."""
    return database.search(
        params.query,
        limit=params.limit,
        filters=params.filters,
    )
```

## Return Types

### Primitive Returns

```python
@mcp.tool()
def return_string(x: str) -> str:
    return f"Result: {x}"

@mcp.tool()
def return_int(x: int) -> int:
    return x * 2

@mcp.tool()
def return_bool(x: int) -> bool:
    return x > 0
```

### Structured Returns (Pydantic)

```python
from pydantic import BaseModel

class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    active: bool

@mcp.tool()
def get_user(user_id: int) -> UserProfile:
    """Get user profile - returns structured JSON."""
    return UserProfile(
        id=user_id,
        name="Alice",
        email="alice@example.com",
        active=True,
    )
```

### Dictionary Returns

```python
@mcp.tool()
def get_stats() -> dict[str, int]:
    """Returns dictionary as JSON."""
    return {
        "users": 100,
        "posts": 500,
        "comments": 2000,
    }
```

### List Returns

```python
@mcp.tool()
def list_items(category: str) -> list[dict]:
    """Returns list of items."""
    return [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"},
    ]
```

### Raw CallToolResult

```python
from mcp.types import CallToolResult, TextContent, ImageContent

@mcp.tool()
def advanced_result(query: str) -> CallToolResult:
    """Full control over response."""
    return CallToolResult(
        content=[
            TextContent(type="text", text="Analysis complete"),
            TextContent(type="text", text="Details here..."),
        ],
        isError=False,
        _meta={"processing_time": 1.5},
    )
```

### Multiple Content Types

```python
import base64
from mcp.types import CallToolResult, TextContent, ImageContent

@mcp.tool()
def generate_report(data: str) -> CallToolResult:
    """Generate report with text and chart."""
    # Generate chart image
    chart_bytes = generate_chart(data)
    chart_b64 = base64.b64encode(chart_bytes).decode()

    return CallToolResult(
        content=[
            TextContent(type="text", text="# Report\n\nAnalysis complete."),
            ImageContent(
                type="image",
                data=chart_b64,
                mimeType="image/png",
            ),
        ]
    )
```

## Async Tools

```python
@mcp.tool()
async def fetch_data(url: str) -> dict:
    """Async tool for HTTP requests."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

@mcp.tool()
async def process_batch(items: list[str]) -> list[str]:
    """Process items concurrently."""
    import asyncio
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks)
```

## Context Access

### Progress Reporting

```python
from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

@mcp.tool()
async def long_task(
    items: list[str],
    ctx: Context[ServerSession, None]
) -> str:
    """Task with progress reporting."""
    total = len(items)

    for i, item in enumerate(items):
        await ctx.report_progress(progress=i, total=total)
        await process(item)

    await ctx.report_progress(progress=total, total=total)
    return f"Processed {total} items"
```

### Logging

```python
@mcp.tool()
async def logged_tool(
    data: str,
    ctx: Context[ServerSession, None]
) -> str:
    """Tool with logging."""
    ctx.debug(f"Input: {data}")
    ctx.info("Processing started")

    try:
        result = await process(data)
        ctx.info(f"Success: {result}")
        return result
    except Exception as e:
        ctx.error(f"Failed: {e}")
        raise
```

### Lifespan Context Access

```python
from dataclasses import dataclass

@dataclass
class AppContext:
    db: Database

@mcp.tool()
async def db_query(
    sql: str,
    ctx: Context[ServerSession, AppContext]
) -> list[dict]:
    """Access lifespan resources."""
    app = ctx.request_context.lifespan_context
    return await app.db.query(sql)
```

## Error Handling

### Standard Exceptions

```python
@mcp.tool()
def validate_input(value: int) -> str:
    """Tool with validation."""
    if value < 0:
        raise ValueError("Value must be non-negative")
    if value > 1000:
        raise ValueError("Value must be <= 1000")
    return f"Valid: {value}"
```

### MCP Errors

```python
from mcp.types import McpError, ErrorCode

@mcp.tool()
def mcp_errors(action: str) -> str:
    """Tool with MCP-specific errors."""
    if action == "invalid":
        raise McpError(
            ErrorCode.INVALID_PARAMS,
            "Invalid action specified"
        )
    if action == "forbidden":
        raise McpError(
            ErrorCode.FORBIDDEN,
            "Action not permitted"
        )
    return f"Executed: {action}"
```

## Tool Patterns

### CRUD Operations

```python
@mcp.tool()
def create_record(data: dict) -> dict:
    """Create a new record."""
    record = database.insert(data)
    return {"id": record.id, "created": True}

@mcp.tool()
def read_record(id: int) -> dict | None:
    """Read a record by ID."""
    return database.get(id)

@mcp.tool()
def update_record(id: int, data: dict) -> bool:
    """Update an existing record."""
    return database.update(id, data)

@mcp.tool()
def delete_record(id: int) -> bool:
    """Delete a record."""
    return database.delete(id)
```

### Search/Filter

```python
@mcp.tool()
def search(
    query: str,
    filters: dict = {},
    sort_by: str = "relevance",
    limit: int = 10,
    offset: int = 0,
) -> dict:
    """Search with filtering and pagination."""
    results = database.search(
        query,
        filters=filters,
        sort=sort_by,
        limit=limit,
        offset=offset,
    )
    return {
        "results": results,
        "total": database.count(query, filters),
        "limit": limit,
        "offset": offset,
    }
```

### API Integration

```python
@mcp.tool()
async def call_external_api(
    endpoint: str,
    method: str = "GET",
    data: dict | None = None,
) -> dict:
    """Call external API."""
    import httpx

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(endpoint)
        elif method == "POST":
            response = await client.post(endpoint, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return {
            "status": response.status_code,
            "data": response.json(),
        }
```

## Best Practices

1. **Descriptive Docstrings**: LLMs use docstrings to understand tool purpose
2. **Type Hints**: Enable automatic schema generation
3. **Validation**: Validate inputs before processing
4. **Error Messages**: Provide clear, actionable error messages
5. **Idempotency**: Design tools that can be safely called multiple times
6. **Timeouts**: Set appropriate timeouts for external calls
7. **Rate Limiting**: Consider rate limiting for expensive operations
8. **Logging**: Log important operations for debugging
