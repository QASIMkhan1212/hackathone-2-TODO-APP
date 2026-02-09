---
name: mcp-sdk
description: Official Model Context Protocol (MCP) SDK for building AI agent integrations. Use when users want to (1) create MCP servers exposing tools/resources, (2) build MCP clients connecting to servers, (3) integrate external APIs with AI agents, (4) add custom tools to Claude/ChatGPT, (5) implement resources and prompts, (6) configure transports (stdio, HTTP, SSE). Triggers on mentions of "mcp", "model context protocol", "mcp server", "mcp client", "agent tools", or building integrations for AI assistants.
---

# MCP SDK (Model Context Protocol)

The official SDK for building MCP servers and clients that connect AI agents to external tools, data, and systems.

## When to Use This Skill

- Creating MCP servers to expose tools to AI agents
- Building MCP clients to connect to existing servers
- Integrating external APIs (databases, services, files) with Claude/ChatGPT
- Adding custom tools and resources to AI assistants
- Implementing prompts for guided AI interactions
- Configuring different transport protocols

## What is MCP?

MCP (Model Context Protocol) is an open standard for connecting AI applications to external systems. Think of it as **"USB-C for AI"** - a universal connector enabling any AI to use any tool.

```
┌─────────────────────────────────────────────────────────┐
│                    AI Application                        │
│            (Claude, ChatGPT, Custom Agent)              │
└─────────────────────────┬───────────────────────────────┘
                          │ MCP Protocol
                          ▼
┌─────────────────────────────────────────────────────────┐
│                     MCP Server                           │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐           │
│  │   Tools   │  │ Resources │  │  Prompts  │           │
│  │ (actions) │  │  (data)   │  │(templates)│           │
│  └───────────┘  └───────────┘  └───────────┘           │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              External Systems                            │
│    Databases │ APIs │ Files │ Services │ Hardware      │
└─────────────────────────────────────────────────────────┘
```

## Core Concepts

### 1. MCP Servers

Servers expose capabilities to AI agents:

| Capability | Description | Example |
|------------|-------------|---------|
| **Tools** | Functions AI can call | `send_email()`, `query_database()` |
| **Resources** | Read-only data | Files, database records, API responses |
| **Prompts** | Reusable templates | "Summarize this document", "Write SQL for..." |

### 2. MCP Clients

Clients connect to servers and consume their capabilities. AI applications like Claude Desktop act as MCP clients.

### 3. Transports

Communication protocols between clients and servers:

| Transport | Use Case |
|-----------|----------|
| **stdio** | Local subprocess communication |
| **Streamable HTTP** | Remote server connections |
| **SSE** | Server-sent events streaming |

## Installation

```bash
# Python SDK
pip install "mcp[cli]"
# or with uv
uv add "mcp[cli]"

# TypeScript SDK
npm install @modelcontextprotocol/sdk
```

## Quick Start: Python Server

### Basic Server with Tools

```python
from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP("MyToolServer")

# Define a tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

# Run server
if __name__ == "__main__":
    mcp.run()
```

### Server with Resources

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DataServer")

# Static resource
@mcp.resource("config://app/settings")
def get_settings() -> dict:
    """Get application settings."""
    return {
        "version": "1.0.0",
        "environment": "production",
    }

# Parameterized resource
@mcp.resource("file://documents/{name}")
def read_document(name: str) -> str:
    """Read a document by name."""
    with open(f"documents/{name}") as f:
        return f.read()

# List resource
@mcp.resource("db://users")
def list_users() -> list[dict]:
    """List all users."""
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
```

### Server with Prompts

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("PromptServer")

@mcp.prompt()
def summarize(text: str, style: str = "concise") -> str:
    """Generate a summarization prompt."""
    return f"""Please summarize the following text in a {style} manner:

{text}

Provide key points and main takeaways."""

@mcp.prompt()
def code_review(code: str, language: str = "python") -> str:
    """Generate a code review prompt."""
    return f"""Review the following {language} code for:
- Bugs and errors
- Performance issues
- Best practices
- Security concerns

```{language}
{code}
```

Provide specific suggestions for improvement."""
```

## Tools Deep Dive

### Basic Tool

```python
@mcp.tool()
def search_database(query: str, limit: int = 10) -> list[dict]:
    """
    Search the database for matching records.

    Args:
        query: Search query string
        limit: Maximum results to return
    """
    # Implementation
    return database.search(query, limit=limit)
```

### Async Tool

```python
@mcp.tool()
async def fetch_url(url: str) -> str:
    """Fetch content from a URL."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text
```

### Tool with Context (Progress Reporting)

```python
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

mcp = FastMCP("ProgressServer")

@mcp.tool()
async def long_running_task(
    items: list[str],
    ctx: Context[ServerSession, None]
) -> str:
    """Process items with progress reporting."""
    total = len(items)
    results = []

    for i, item in enumerate(items):
        # Report progress
        await ctx.report_progress(progress=i, total=total)

        # Process item
        result = await process_item(item)
        results.append(result)

    return f"Processed {total} items"
```

### Tool with Structured Output

```python
from pydantic import BaseModel

class WeatherResult(BaseModel):
    city: str
    temperature: float
    conditions: str
    humidity: int

@mcp.tool()
def get_weather(city: str) -> WeatherResult:
    """Get weather for a city."""
    # Returns structured JSON automatically
    return WeatherResult(
        city=city,
        temperature=72.5,
        conditions="Sunny",
        humidity=45,
    )
```

### Tool Returning Raw CallToolResult

```python
from mcp.types import CallToolResult, TextContent, ImageContent

@mcp.tool()
def advanced_tool(query: str) -> CallToolResult:
    """Tool with full control over response."""
    return CallToolResult(
        content=[
            TextContent(type="text", text="Analysis complete"),
            ImageContent(type="image", data=base64_image, mimeType="image/png"),
        ],
        _meta={"processing_time": 1.5}
    )
```

## Resources Deep Dive

### Static Resource

```python
@mcp.resource("config://settings")
def get_config() -> dict:
    """Application configuration."""
    return {"debug": False, "version": "2.0"}
```

### Dynamic Resource with Parameters

```python
@mcp.resource("api://users/{user_id}/profile")
async def get_user_profile(user_id: str) -> dict:
    """Get user profile by ID."""
    user = await database.get_user(user_id)
    return user.to_dict()
```

### Binary Resource

```python
@mcp.resource("file://images/{name}")
def get_image(name: str) -> bytes:
    """Get image file."""
    with open(f"images/{name}", "rb") as f:
        return f.read()
```

## Transports

### Stdio (Default - Local)

```python
# Server
mcp = FastMCP("LocalServer")
mcp.run()  # Uses stdio by default

# Or explicitly
mcp.run(transport="stdio")
```

### Streamable HTTP (Remote)

```python
# Server
mcp = FastMCP("RemoteServer")
mcp.run(transport="streamable-http", port=8000)

# Client connects to http://localhost:8000/mcp
```

### SSE (Server-Sent Events)

```python
mcp = FastMCP("SSEServer")
mcp.run(transport="sse", port=8000)
```

## Client Usage

### Basic Client

```python
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def main():
    # Connect via stdio
    async with stdio_client(["python", "server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

            # Call a tool
            result = await session.call_tool("add", {"a": 5, "b": 3})
            print(f"Result: {result}")

            # List resources
            resources = await session.list_resources()

            # Read a resource
            content = await session.read_resource("config://settings")
```

### HTTP Client

```python
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Use session...
```

## Lifespan Management

```python
from contextlib import asynccontextmanager
from dataclasses import dataclass

@dataclass
class AppContext:
    db: Database
    cache: Cache

@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """Manage application resources."""
    # Startup
    db = await Database.connect()
    cache = await Cache.connect()

    yield AppContext(db=db, cache=cache)

    # Shutdown
    await db.disconnect()
    await cache.disconnect()

mcp = FastMCP("AppServer", lifespan=app_lifespan)

@mcp.tool()
async def query_data(
    sql: str,
    ctx: Context[ServerSession, AppContext]
) -> list[dict]:
    """Query database using lifespan context."""
    return await ctx.request_context.lifespan_context.db.query(sql)
```

## Configuration for AI Clients

### Claude Desktop

```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

### Claude Desktop (HTTP)

```json
{
  "mcpServers": {
    "remote-server": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Claude CLI

```bash
# Add local server
claude mcp add my-server python /path/to/server.py

# Add remote server
claude mcp add --transport http my-server http://localhost:8000/mcp

# List servers
claude mcp list

# Remove server
claude mcp remove my-server
```

## Testing with MCP Inspector

```bash
# Install and run inspector
npx -y @modelcontextprotocol/inspector

# Connect to your server at http://localhost:5173
# Test tools, resources, and prompts interactively
```

## Best Practices

1. **Clear Tool Descriptions**: LLMs use docstrings to understand tools
2. **Type Annotations**: Enable automatic schema generation
3. **Error Handling**: Return meaningful errors for LLM understanding
4. **Idempotent Tools**: Design tools that can be safely retried
5. **Security**: Validate inputs, limit permissions, use authentication
6. **Logging**: Use context logging for debugging

```python
@mcp.tool()
async def safe_tool(
    user_input: str,
    ctx: Context[ServerSession, None]
) -> str:
    """Tool with best practices."""
    # Validate input
    if not user_input or len(user_input) > 10000:
        raise ValueError("Invalid input")

    # Log for debugging
    ctx.info(f"Processing: {user_input[:50]}...")

    try:
        result = await process(user_input)
        return result
    except Exception as e:
        ctx.error(f"Processing failed: {e}")
        raise
```

## References

- See `references/servers.md` for server patterns
- See `references/clients.md` for client usage
- See `references/tools.md` for tool development
- See `references/resources.md` for resource patterns
- See `references/transports.md` for transport configuration

## Scripts

- `scripts/create_server.py` - Scaffold new MCP server
- `scripts/create_tool.py` - Generate tool boilerplate
- `scripts/setup_mcp.py` - Set up MCP development environment

## Assets

- `assets/server_template.py` - Complete server template
- `assets/client_template.py` - Client implementation template
- `assets/tools_template.py` - Common tool patterns
