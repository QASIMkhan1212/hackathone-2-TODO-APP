# MCP Transports Reference

## Overview

Transports define how MCP clients and servers communicate. The protocol supports multiple transport mechanisms for different deployment scenarios.

## Transport Types

| Transport | Use Case | Connection |
|-----------|----------|------------|
| **stdio** | Local subprocess | stdin/stdout |
| **Streamable HTTP** | Remote servers | HTTP + streaming |
| **SSE** | Legacy HTTP | Server-sent events |

## Stdio Transport

Standard input/output communication for local servers.

### Server (Python)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LocalServer")

@mcp.tool()
def hello(name: str) -> str:
    return f"Hello, {name}!"

# Run with stdio (default)
if __name__ == "__main__":
    mcp.run()  # or mcp.run(transport="stdio")
```

### Client (Python)

```python
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def main():
    # Start server as subprocess
    async with stdio_client(["python", "server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Use the session
            tools = await session.list_tools()
            result = await session.call_tool("hello", {"name": "World"})
            print(result)
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "my-local-server": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "API_KEY": "your-key"
      }
    }
  }
}
```

### With UV/Virtual Environment

```json
{
  "mcpServers": {
    "my-server": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/project", "server.py"]
    }
  }
}
```

## Streamable HTTP Transport

HTTP-based transport with streaming support for remote servers.

### Server (Python)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("RemoteServer")

@mcp.tool()
def process(data: str) -> str:
    return f"Processed: {data}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000)
```

### Server Options

```python
mcp.run(
    transport="streamable-http",
    host="0.0.0.0",      # Listen on all interfaces
    port=8000,            # Port number
)
```

### Client (Python)

```python
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    url = "http://localhost:8000/mcp"

    async with streamablehttp_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool("process", {"data": "test"})
            print(result)
```

### Claude Desktop Configuration (HTTP)

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
# Add remote HTTP server
claude mcp add --transport http my-server http://localhost:8000/mcp

# List configured servers
claude mcp list
```

## SSE Transport (Legacy)

Server-Sent Events transport for older HTTP streaming.

### Server

```python
mcp = FastMCP("SSEServer")
mcp.run(transport="sse", port=8000)
```

### Client

```python
from mcp.client.sse import sse_client

async with sse_client("http://localhost:8000/sse") as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # Use session...
```

## TypeScript Transports

### Stdio Server

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({
  name: "TypeScriptServer",
  version: "1.0.0",
});

// Add capabilities...

const transport = new StdioServerTransport();
await server.connect(transport);
```

### HTTP Server

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";

const server = new McpServer({
  name: "HTTPServer",
  version: "1.0.0",
});

const transport = new StreamableHTTPServerTransport({
  port: 8000,
});

await server.connect(transport);
```

### Stdio Client

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const transport = new StdioClientTransport({
  command: "python",
  args: ["server.py"],
});

const client = new Client({
  name: "my-client",
  version: "1.0.0",
});

await client.connect(transport);

// Use client
const tools = await client.listTools();
```

## Authentication

### HTTP with Authentication

```python
from mcp.server.fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

# Custom auth backend
class APIKeyAuth:
    async def authenticate(self, request):
        api_key = request.headers.get("X-API-Key")
        if api_key != os.getenv("API_KEY"):
            raise AuthenticationError("Invalid API key")
        return AuthCredentials(["authenticated"]), SimpleUser("api")

mcp = FastMCP("AuthServer")

# Add authentication middleware
# (Implementation depends on HTTP framework used)
```

### OAuth (Remote MCP)

Neon and other remote MCP servers support OAuth:

```json
{
  "mcpServers": {
    "neon": {
      "url": "https://mcp.neon.tech/mcp",
      "oauth": {
        "client_id": "your-client-id",
        "scopes": ["read", "write"]
      }
    }
  }
}
```

## Connection Management

### Reconnection Logic

```python
import asyncio
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def connect_with_retry(url: str, max_retries: int = 3):
    """Connect with automatic retry."""
    for attempt in range(max_retries):
        try:
            async with streamablehttp_client(url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    return session
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Health Checks

```python
async def check_server_health(url: str) -> bool:
    """Check if MCP server is responsive."""
    try:
        async with streamablehttp_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return True
    except Exception:
        return False
```

## Deployment Patterns

### Docker Compose (HTTP)

```yaml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
    command: python server.py
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mcp-server
  template:
    spec:
      containers:
        - name: mcp-server
          image: my-mcp-server:latest
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
```

### Serverless (AWS Lambda)

```python
# Using Mangum for AWS Lambda
from mangum import Mangum
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LambdaServer")

# ... define tools/resources ...

# Create ASGI handler for Lambda
handler = Mangum(mcp.app)
```

## Best Practices

1. **Use stdio for local**: Simplest setup for local development
2. **Use HTTP for remote**: Enables network access and scaling
3. **Secure HTTP servers**: Always use authentication in production
4. **Health checks**: Implement health endpoints for monitoring
5. **Timeouts**: Set appropriate connection and read timeouts
6. **Retry logic**: Implement exponential backoff for reconnection
7. **TLS/HTTPS**: Use HTTPS for production remote servers
