# MCP Clients Reference

## Overview

MCP clients connect to servers and consume their tools, resources, and prompts. AI applications like Claude Desktop and ChatGPT act as MCP clients.

## Client Session

The `ClientSession` is the main interface for interacting with MCP servers:

```python
from mcp.client.session import ClientSession

async with ClientSession(read_stream, write_stream) as session:
    await session.initialize()
    # Use session...
```

## Connecting to Servers

### Stdio Connection

```python
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def connect_stdio():
    # Connect to local server via subprocess
    async with stdio_client(["python", "server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return session
```

### HTTP Connection

```python
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def connect_http():
    async with streamablehttp_client("http://localhost:8000/mcp") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return session
```

### SSE Connection

```python
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

async def connect_sse():
    async with sse_client("http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return session
```

## Session Operations

### List Tools

```python
async def list_available_tools(session: ClientSession):
    """Get all available tools from server."""
    result = await session.list_tools()

    for tool in result.tools:
        print(f"Tool: {tool.name}")
        print(f"  Description: {tool.description}")
        print(f"  Schema: {tool.inputSchema}")
```

### Call Tool

```python
async def call_tool(session: ClientSession):
    """Call a tool on the server."""
    result = await session.call_tool(
        name="add",
        arguments={"a": 5, "b": 3}
    )

    # Handle result
    for content in result.content:
        if content.type == "text":
            print(f"Result: {content.text}")
```

### List Resources

```python
async def list_available_resources(session: ClientSession):
    """Get all available resources."""
    result = await session.list_resources()

    for resource in result.resources:
        print(f"Resource: {resource.uri}")
        print(f"  Name: {resource.name}")
        print(f"  Description: {resource.description}")
        print(f"  MIME Type: {resource.mimeType}")
```

### Read Resource

```python
async def read_resource(session: ClientSession, uri: str):
    """Read a resource from the server."""
    result = await session.read_resource(uri)

    for content in result.contents:
        if content.type == "text":
            print(f"Content: {content.text}")
        elif content.type == "blob":
            print(f"Binary data: {len(content.blob)} bytes")
```

### List Prompts

```python
async def list_available_prompts(session: ClientSession):
    """Get all available prompts."""
    result = await session.list_prompts()

    for prompt in result.prompts:
        print(f"Prompt: {prompt.name}")
        print(f"  Description: {prompt.description}")
        print(f"  Arguments: {prompt.arguments}")
```

### Get Prompt

```python
async def get_prompt(session: ClientSession, name: str, args: dict):
    """Get a prompt with arguments."""
    result = await session.get_prompt(name, args)

    for message in result.messages:
        print(f"Role: {message.role}")
        print(f"Content: {message.content}")
```

## Complete Client Example

```python
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
import asyncio

async def main():
    """Complete client example."""

    # Connect to server
    async with stdio_client(["python", "server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()

            # Get server info
            print(f"Connected to: {session.server_info}")

            # List and call tools
            tools = await session.list_tools()
            print(f"\nAvailable tools: {len(tools.tools)}")

            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call a tool
            if any(t.name == "add" for t in tools.tools):
                result = await session.call_tool("add", {"a": 10, "b": 20})
                print(f"\nadd(10, 20) = {result.content[0].text}")

            # List and read resources
            resources = await session.list_resources()
            print(f"\nAvailable resources: {len(resources.resources)}")

            for resource in resources.resources:
                print(f"  - {resource.uri}")

            # Read a resource
            if resources.resources:
                uri = resources.resources[0].uri
                content = await session.read_resource(uri)
                print(f"\nResource {uri}:")
                print(content.contents[0].text[:200])

            # List and get prompts
            prompts = await session.list_prompts()
            print(f"\nAvailable prompts: {len(prompts.prompts)}")

            for prompt in prompts.prompts:
                print(f"  - {prompt.name}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Client Wrapper Class

```python
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from typing import Any
from contextlib import asynccontextmanager

class MCPClient:
    """Wrapper class for MCP client operations."""

    def __init__(self):
        self.session: ClientSession | None = None
        self._context = None

    @asynccontextmanager
    async def connect_stdio(self, command: list[str]):
        """Connect to local server via stdio."""
        async with stdio_client(command) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.session = session
                yield self
                self.session = None

    @asynccontextmanager
    async def connect_http(self, url: str):
        """Connect to remote server via HTTP."""
        async with streamablehttp_client(url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.session = session
                yield self
                self.session = None

    async def list_tools(self) -> list[dict]:
        """List available tools."""
        result = await self.session.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "schema": t.inputSchema,
            }
            for t in result.tools
        ]

    async def call_tool(self, name: str, arguments: dict) -> Any:
        """Call a tool and return result."""
        result = await self.session.call_tool(name, arguments)
        # Extract text content
        for content in result.content:
            if content.type == "text":
                return content.text
        return result

    async def list_resources(self) -> list[dict]:
        """List available resources."""
        result = await self.session.list_resources()
        return [
            {
                "uri": r.uri,
                "name": r.name,
                "description": r.description,
            }
            for r in result.resources
        ]

    async def read_resource(self, uri: str) -> str:
        """Read a resource."""
        result = await self.session.read_resource(uri)
        for content in result.contents:
            if content.type == "text":
                return content.text
        return None


# Usage
async def example():
    client = MCPClient()

    async with client.connect_stdio(["python", "server.py"]):
        tools = await client.list_tools()
        result = await client.call_tool("add", {"a": 1, "b": 2})
        print(result)
```

## TypeScript Client

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
  // Create transport
  const transport = new StdioClientTransport({
    command: "python",
    args: ["server.py"],
  });

  // Create client
  const client = new Client({
    name: "my-client",
    version: "1.0.0",
  });

  // Connect
  await client.connect(transport);

  // List tools
  const tools = await client.listTools();
  console.log("Tools:", tools);

  // Call tool
  const result = await client.callTool({
    name: "add",
    arguments: { a: 5, b: 3 },
  });
  console.log("Result:", result);

  // Disconnect
  await client.close();
}

main();
```

## Error Handling

```python
from mcp.types import McpError

async def safe_tool_call(session: ClientSession, name: str, args: dict):
    """Call tool with error handling."""
    try:
        result = await session.call_tool(name, args)
        return {"success": True, "result": result}
    except McpError as e:
        return {"success": False, "error": str(e), "code": e.code}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Best Practices

1. **Always Initialize**: Call `session.initialize()` before other operations
2. **Use Context Managers**: Ensures proper cleanup
3. **Handle Errors**: Wrap calls in try/except
4. **Check Capabilities**: List tools/resources before using them
5. **Timeout**: Set appropriate timeouts for operations
6. **Reconnection**: Implement retry logic for remote servers
