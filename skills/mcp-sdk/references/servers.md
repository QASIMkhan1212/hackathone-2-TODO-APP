# MCP Servers Reference

## Overview

MCP servers expose tools, resources, and prompts to AI applications. They handle protocol compliance, connection management, and message routing.

## FastMCP Server

FastMCP is the high-level API for building MCP servers in Python:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ServerName")
```

### Configuration Options

```python
mcp = FastMCP(
    name="MyServer",                    # Server name
    version="1.0.0",                    # Server version
    instructions="Server description",   # Instructions for LLMs
    lifespan=app_lifespan,              # Lifecycle manager
)
```

## Server Patterns

### Basic Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("BasicServer")

@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

### Server with Multiple Capabilities

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FullServer")

# Tools
@mcp.tool()
def calculate(expression: str) -> float:
    """Evaluate a math expression."""
    return eval(expression)

# Resources
@mcp.resource("config://app")
def get_config() -> dict:
    """Get application config."""
    return {"version": "1.0", "env": "prod"}

# Prompts
@mcp.prompt()
def analyze(topic: str) -> str:
    """Generate analysis prompt."""
    return f"Analyze {topic} in detail."

if __name__ == "__main__":
    mcp.run()
```

### Server with Lifespan

```python
from contextlib import asynccontextmanager
from dataclasses import dataclass
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

@dataclass
class AppContext:
    db: Database
    api_client: APIClient

@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """Manage server lifecycle."""
    print("Starting server...")

    # Initialize resources
    db = await Database.connect(os.getenv("DATABASE_URL"))
    api_client = APIClient(os.getenv("API_KEY"))

    yield AppContext(db=db, api_client=api_client)

    # Cleanup
    await db.disconnect()
    await api_client.close()
    print("Server stopped.")

mcp = FastMCP("LifespanServer", lifespan=app_lifespan)

@mcp.tool()
async def query(
    sql: str,
    ctx: Context[ServerSession, AppContext]
) -> list[dict]:
    """Execute database query."""
    app = ctx.request_context.lifespan_context
    return await app.db.query(sql)
```

### Server with Dependencies

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DependencyServer")

# Shared state
class SharedState:
    def __init__(self):
        self.counter = 0
        self.cache = {}

state = SharedState()

@mcp.tool()
def increment() -> int:
    """Increment counter."""
    state.counter += 1
    return state.counter

@mcp.tool()
def get_cached(key: str) -> str | None:
    """Get cached value."""
    return state.cache.get(key)

@mcp.tool()
def set_cached(key: str, value: str) -> bool:
    """Set cached value."""
    state.cache[key] = value
    return True
```

## Running Servers

### Stdio (Development)

```python
# Default - stdin/stdout communication
mcp.run()
# or
mcp.run(transport="stdio")
```

### Streamable HTTP

```python
# HTTP server on port 8000
mcp.run(transport="streamable-http", port=8000)

# Custom host and port
mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)
```

### SSE (Server-Sent Events)

```python
mcp.run(transport="sse", port=8000)
```

## Server Instructions

Provide guidance to LLMs about how to use your server:

```python
mcp = FastMCP(
    name="DatabaseServer",
    instructions="""
    This server provides database access tools.

    Available operations:
    - query: Execute SELECT queries
    - insert: Add new records
    - update: Modify existing records

    Guidelines:
    - Always use parameterized queries
    - Limit results to 100 rows by default
    - Handle errors gracefully
    """
)
```

## Error Handling

```python
from mcp.server.fastmcp import FastMCP
from mcp.types import McpError, ErrorCode

mcp = FastMCP("ErrorServer")

@mcp.tool()
def risky_operation(value: int) -> str:
    """Operation that might fail."""
    if value < 0:
        raise McpError(
            ErrorCode.INVALID_PARAMS,
            "Value must be non-negative"
        )

    if value > 1000:
        raise ValueError("Value too large")  # Converted to MCP error

    return f"Processed: {value}"
```

## Logging

```python
from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("LoggingServer")

@mcp.tool()
async def logged_operation(
    data: str,
    ctx: Context
) -> str:
    """Operation with logging."""
    ctx.debug(f"Starting operation with: {data}")
    ctx.info("Processing...")

    try:
        result = process(data)
        ctx.info(f"Success: {result}")
        return result
    except Exception as e:
        ctx.error(f"Failed: {e}")
        raise
```

## Server Metadata

```python
mcp = FastMCP(
    name="MetadataServer",
    version="2.0.0",
    instructions="A server with full metadata.",
)

# Access server info
print(f"Name: {mcp.name}")
print(f"Version: {mcp.version}")
```

## TypeScript Server

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({
  name: "TypeScriptServer",
  version: "1.0.0",
});

// Add tool
server.tool(
  "greet",
  { name: { type: "string", description: "Name to greet" } },
  async ({ name }) => ({
    content: [{ type: "text", text: `Hello, ${name}!` }],
  })
);

// Run server
const transport = new StdioServerTransport();
await server.connect(transport);
```

## Best Practices

1. **Clear Names**: Use descriptive server and tool names
2. **Documentation**: Provide instructions and docstrings
3. **Error Messages**: Return helpful error messages
4. **Idempotency**: Design tools to be safely retried
5. **Validation**: Validate all inputs
6. **Logging**: Log important operations
7. **Cleanup**: Use lifespan for resource management
8. **Security**: Limit permissions and validate requests
