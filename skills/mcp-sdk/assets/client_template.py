"""MCP Client Template.

A reusable client wrapper for connecting to and interacting with MCP servers.
"""

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncGenerator

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Tool, Resource, Prompt


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ToolInfo:
    """Information about an available tool."""
    name: str
    description: str
    schema: dict


@dataclass
class ResourceInfo:
    """Information about an available resource."""
    uri: str
    name: str
    description: str
    mime_type: str | None


@dataclass
class PromptInfo:
    """Information about an available prompt."""
    name: str
    description: str
    arguments: list[dict]


@dataclass
class ToolResult:
    """Result from calling a tool."""
    success: bool
    content: Any
    error: str | None = None


# =============================================================================
# MCP Client Wrapper
# =============================================================================


class MCPClient:
    """
    Wrapper class for MCP client operations.

    Usage:
        # Stdio connection
        async with MCPClient.connect_stdio(["python", "server.py"]) as client:
            tools = await client.list_tools()
            result = await client.call_tool("hello", {"name": "World"})

        # HTTP connection
        async with MCPClient.connect_http("http://localhost:8000/mcp") as client:
            resources = await client.list_resources()
            content = await client.read_resource("config://server")
    """

    def __init__(self, session: ClientSession):
        self.session = session
        self._tools_cache: list[ToolInfo] | None = None
        self._resources_cache: list[ResourceInfo] | None = None

    @classmethod
    @asynccontextmanager
    async def connect_stdio(
        cls,
        command: list[str],
        env: dict[str, str] | None = None,
    ) -> AsyncGenerator["MCPClient", None]:
        """
        Connect to a local MCP server via stdio.

        Args:
            command: Command to start server (e.g., ["python", "server.py"])
            env: Environment variables for the subprocess

        Yields:
            Connected MCPClient instance
        """
        async with stdio_client(command, env=env) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield cls(session)

    @classmethod
    @asynccontextmanager
    async def connect_http(
        cls,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> AsyncGenerator["MCPClient", None]:
        """
        Connect to a remote MCP server via HTTP.

        Args:
            url: Server URL (e.g., "http://localhost:8000/mcp")
            headers: Optional HTTP headers (for authentication)

        Yields:
            Connected MCPClient instance
        """
        async with streamablehttp_client(url, headers=headers) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield cls(session)

    # =========================================================================
    # Tool Operations
    # =========================================================================

    async def list_tools(self, refresh: bool = False) -> list[ToolInfo]:
        """
        List available tools from the server.

        Args:
            refresh: Force refresh of cached tools

        Returns:
            List of available tools
        """
        if self._tools_cache is None or refresh:
            result = await self.session.list_tools()
            self._tools_cache = [
                ToolInfo(
                    name=t.name,
                    description=t.description or "",
                    schema=t.inputSchema or {},
                )
                for t in result.tools
            ]
        return self._tools_cache

    async def has_tool(self, name: str) -> bool:
        """Check if a tool is available."""
        tools = await self.list_tools()
        return any(t.name == name for t in tools)

    async def call_tool(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> ToolResult:
        """
        Call a tool on the server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        try:
            result = await self.session.call_tool(name, arguments or {})

            # Extract content
            content = []
            for item in result.content:
                if item.type == "text":
                    content.append(item.text)
                elif item.type == "image":
                    content.append({"type": "image", "data": item.data})
                else:
                    content.append(item)

            # Return single item if only one
            if len(content) == 1:
                content = content[0]

            return ToolResult(success=True, content=content)

        except Exception as e:
            return ToolResult(success=False, content=None, error=str(e))

    async def call_tool_safe(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        default: Any = None,
    ) -> Any:
        """
        Call a tool and return content or default on error.

        Args:
            name: Tool name
            arguments: Tool arguments
            default: Default value on error

        Returns:
            Tool content or default
        """
        result = await self.call_tool(name, arguments)
        return result.content if result.success else default

    # =========================================================================
    # Resource Operations
    # =========================================================================

    async def list_resources(self, refresh: bool = False) -> list[ResourceInfo]:
        """
        List available resources from the server.

        Args:
            refresh: Force refresh of cached resources

        Returns:
            List of available resources
        """
        if self._resources_cache is None or refresh:
            result = await self.session.list_resources()
            self._resources_cache = [
                ResourceInfo(
                    uri=r.uri,
                    name=r.name or "",
                    description=r.description or "",
                    mime_type=r.mimeType,
                )
                for r in result.resources
            ]
        return self._resources_cache

    async def read_resource(self, uri: str) -> Any:
        """
        Read a resource from the server.

        Args:
            uri: Resource URI

        Returns:
            Resource content
        """
        result = await self.session.read_resource(uri)

        # Extract content
        for item in result.contents:
            if item.type == "text":
                return item.text
            elif item.type == "blob":
                return item.blob

        return None

    async def read_resource_safe(self, uri: str, default: Any = None) -> Any:
        """
        Read a resource, returning default on error.

        Args:
            uri: Resource URI
            default: Default value on error

        Returns:
            Resource content or default
        """
        try:
            return await self.read_resource(uri)
        except Exception:
            return default

    # =========================================================================
    # Prompt Operations
    # =========================================================================

    async def list_prompts(self) -> list[PromptInfo]:
        """
        List available prompts from the server.

        Returns:
            List of available prompts
        """
        result = await self.session.list_prompts()
        return [
            PromptInfo(
                name=p.name,
                description=p.description or "",
                arguments=[
                    {"name": a.name, "description": a.description, "required": a.required}
                    for a in (p.arguments or [])
                ],
            )
            for p in result.prompts
        ]

    async def get_prompt(
        self,
        name: str,
        arguments: dict[str, str] | None = None,
    ) -> list[dict]:
        """
        Get a prompt with arguments.

        Args:
            name: Prompt name
            arguments: Prompt arguments

        Returns:
            List of prompt messages
        """
        result = await self.session.get_prompt(name, arguments or {})
        return [
            {
                "role": m.role,
                "content": m.content.text if hasattr(m.content, "text") else str(m.content),
            }
            for m in result.messages
        ]

    # =========================================================================
    # Utility Methods
    # =========================================================================

    async def get_server_info(self) -> dict:
        """Get server information."""
        return {
            "name": self.session.server_info.name if self.session.server_info else None,
            "version": self.session.server_info.version if self.session.server_info else None,
        }

    async def ping(self) -> bool:
        """Check if server is responsive."""
        try:
            await self.list_tools()
            return True
        except Exception:
            return False


# =============================================================================
# Multi-Server Client
# =============================================================================


class MCPMultiClient:
    """
    Client for managing multiple MCP server connections.

    Usage:
        multi = MCPMultiClient()
        await multi.add_stdio("local", ["python", "server.py"])
        await multi.add_http("remote", "http://localhost:8000/mcp")

        # Use specific server
        result = await multi.call_tool("local", "hello", {"name": "World"})

        # Find tool across all servers
        result = await multi.call_tool_any("hello", {"name": "World"})
    """

    def __init__(self):
        self.clients: dict[str, MCPClient] = {}
        self._contexts: list = []

    async def add_stdio(
        self,
        name: str,
        command: list[str],
        env: dict[str, str] | None = None,
    ) -> None:
        """Add a stdio server connection."""
        ctx = stdio_client(command, env=env)
        read, write = await ctx.__aenter__()
        self._contexts.append(ctx)

        session = ClientSession(read, write)
        await session.__aenter__()
        await session.initialize()

        self.clients[name] = MCPClient(session)

    async def add_http(
        self,
        name: str,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Add an HTTP server connection."""
        ctx = streamablehttp_client(url, headers=headers)
        read, write = await ctx.__aenter__()
        self._contexts.append(ctx)

        session = ClientSession(read, write)
        await session.__aenter__()
        await session.initialize()

        self.clients[name] = MCPClient(session)

    def get(self, name: str) -> MCPClient | None:
        """Get a specific client by name."""
        return self.clients.get(name)

    async def call_tool(
        self,
        server: str,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> ToolResult:
        """Call a tool on a specific server."""
        client = self.clients.get(server)
        if not client:
            return ToolResult(success=False, content=None, error=f"Server not found: {server}")
        return await client.call_tool(name, arguments)

    async def call_tool_any(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> ToolResult:
        """Call a tool on any server that has it."""
        for client in self.clients.values():
            if await client.has_tool(name):
                return await client.call_tool(name, arguments)
        return ToolResult(success=False, content=None, error=f"Tool not found: {name}")

    async def list_all_tools(self) -> dict[str, list[ToolInfo]]:
        """List tools from all servers."""
        result = {}
        for name, client in self.clients.items():
            result[name] = await client.list_tools()
        return result

    async def close(self) -> None:
        """Close all connections."""
        for ctx in self._contexts:
            await ctx.__aexit__(None, None, None)
        self.clients.clear()
        self._contexts.clear()


# =============================================================================
# Example Usage
# =============================================================================


async def example_single_client():
    """Example using single client."""
    async with MCPClient.connect_stdio(["python", "server.py"]) as client:
        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Call a tool
        result = await client.call_tool("hello", {"name": "World"})
        if result.success:
            print(f"Result: {result.content}")
        else:
            print(f"Error: {result.error}")

        # Read a resource
        config = await client.read_resource("config://server")
        print(f"Config: {config}")


async def example_multi_client():
    """Example using multi-client."""
    multi = MCPMultiClient()

    try:
        await multi.add_stdio("local", ["python", "server.py"])
        # await multi.add_http("remote", "http://localhost:8000/mcp")

        # List all tools
        all_tools = await multi.list_all_tools()
        for server, tools in all_tools.items():
            print(f"{server}: {[t.name for t in tools]}")

        # Call tool on any server
        result = await multi.call_tool_any("hello", {"name": "World"})
        print(f"Result: {result.content}")

    finally:
        await multi.close()


if __name__ == "__main__":
    asyncio.run(example_single_client())
