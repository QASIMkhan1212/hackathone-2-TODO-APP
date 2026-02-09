"""Complete MCP Server Template.

A production-ready MCP server with tools, resources, prompts,
and lifecycle management.
"""

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel, Field


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class ServerConfig:
    """Server configuration."""
    name: str = "MyMCPServer"
    version: str = "1.0.0"
    debug: bool = False


@dataclass
class AppContext:
    """Application context available to all handlers."""
    config: ServerConfig
    start_time: datetime
    # Add your resources here:
    # db: Database
    # cache: Cache
    # api_client: APIClient


# =============================================================================
# Lifecycle Management
# =============================================================================


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """
    Manage application lifecycle.

    Initialize resources on startup, clean up on shutdown.
    """
    print("Starting MCP server...")

    # Initialize configuration
    config = ServerConfig(
        name=os.getenv("SERVER_NAME", "MyMCPServer"),
        version=os.getenv("SERVER_VERSION", "1.0.0"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
    )

    # Initialize resources
    # db = await Database.connect(os.getenv("DATABASE_URL"))
    # cache = await Cache.connect(os.getenv("REDIS_URL"))

    context = AppContext(
        config=config,
        start_time=datetime.now(),
        # db=db,
        # cache=cache,
    )

    print(f"Server {config.name} v{config.version} ready")

    yield context

    # Cleanup
    # await db.disconnect()
    # await cache.disconnect()
    print("Server stopped")


# =============================================================================
# Server Definition
# =============================================================================


mcp = FastMCP(
    name="MyMCPServer",
    version="1.0.0",
    lifespan=app_lifespan,
    instructions="""
    This MCP server provides various tools and resources.

    Available capabilities:
    - Tools for data processing and API calls
    - Resources for configuration and status
    - Prompts for common tasks

    Usage guidelines:
    - Use appropriate tools for each task
    - Check resources for current state
    - Handle errors gracefully
    """
)


# =============================================================================
# Pydantic Models
# =============================================================================


class SearchParams(BaseModel):
    """Search parameters."""
    query: str = Field(description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Max results")
    filters: dict[str, Any] = Field(default_factory=dict, description="Filters")


class SearchResult(BaseModel):
    """Search result."""
    id: str
    title: str
    score: float
    metadata: dict[str, Any] = {}


class ProcessingResult(BaseModel):
    """Processing result."""
    success: bool
    message: str
    data: dict[str, Any] | None = None
    errors: list[str] = []


# =============================================================================
# Tools
# =============================================================================


@mcp.tool()
def hello(name: str) -> str:
    """
    Say hello to someone.

    Args:
        name: Name of the person to greet

    Returns:
        Greeting message
    """
    return f"Hello, {name}! Welcome to MyMCPServer."


@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b
    """
    return a + b


@mcp.tool()
async def search(params: SearchParams) -> list[SearchResult]:
    """
    Search for items.

    Args:
        params: Search parameters

    Returns:
        List of search results
    """
    # TODO: Implement actual search logic
    return [
        SearchResult(
            id="1",
            title=f"Result for: {params.query}",
            score=0.95,
            metadata={"source": "example"},
        )
    ]


@mcp.tool()
async def process_data(
    data: str,
    ctx: Context[ServerSession, AppContext]
) -> ProcessingResult:
    """
    Process data with progress reporting.

    Args:
        data: Data to process

    Returns:
        Processing result
    """
    # Report progress
    await ctx.report_progress(progress=0, total=100)
    ctx.info(f"Processing data: {data[:50]}...")

    try:
        # Simulate processing
        await ctx.report_progress(progress=50, total=100)

        # Access lifespan context
        app = ctx.request_context.lifespan_context
        ctx.debug(f"Server uptime: {datetime.now() - app.start_time}")

        await ctx.report_progress(progress=100, total=100)

        return ProcessingResult(
            success=True,
            message="Data processed successfully",
            data={"length": len(data)},
        )
    except Exception as e:
        ctx.error(f"Processing failed: {e}")
        return ProcessingResult(
            success=False,
            message="Processing failed",
            errors=[str(e)],
        )


@mcp.tool()
def advanced_output(query: str) -> CallToolResult:
    """
    Tool with advanced output control.

    Args:
        query: Query to process

    Returns:
        Multi-content result
    """
    return CallToolResult(
        content=[
            TextContent(type="text", text=f"# Results for: {query}\n"),
            TextContent(type="text", text="## Summary\nProcessing complete."),
        ],
        _meta={"query": query, "timestamp": datetime.now().isoformat()},
    )


# =============================================================================
# Resources
# =============================================================================


@mcp.resource("config://server")
async def server_config(ctx: Context[ServerSession, AppContext]) -> dict:
    """Get server configuration."""
    app = ctx.request_context.lifespan_context
    return {
        "name": app.config.name,
        "version": app.config.version,
        "debug": app.config.debug,
    }


@mcp.resource("status://health")
async def health_status(ctx: Context[ServerSession, AppContext]) -> dict:
    """Get server health status."""
    app = ctx.request_context.lifespan_context
    uptime = datetime.now() - app.start_time

    return {
        "status": "healthy",
        "uptime_seconds": uptime.total_seconds(),
        "timestamp": datetime.now().isoformat(),
    }


@mcp.resource("data://items")
def list_items() -> list[dict]:
    """List available items."""
    return [
        {"id": "1", "name": "Item 1", "status": "active"},
        {"id": "2", "name": "Item 2", "status": "active"},
    ]


@mcp.resource("data://items/{item_id}")
def get_item(item_id: str) -> dict | None:
    """Get item by ID."""
    items = {
        "1": {"id": "1", "name": "Item 1", "description": "First item"},
        "2": {"id": "2", "name": "Item 2", "description": "Second item"},
    }
    return items.get(item_id)


# =============================================================================
# Prompts
# =============================================================================


@mcp.prompt()
def analyze(topic: str, depth: str = "moderate") -> str:
    """
    Generate an analysis prompt.

    Args:
        topic: Topic to analyze
        depth: Analysis depth (brief, moderate, detailed)

    Returns:
        Analysis prompt
    """
    depth_instructions = {
        "brief": "Provide a brief 2-3 sentence overview.",
        "moderate": "Provide a balanced analysis with key points.",
        "detailed": "Provide comprehensive analysis with examples.",
    }

    return f"""Please analyze the following topic: {topic}

{depth_instructions.get(depth, depth_instructions["moderate"])}

Include:
1. Main concepts
2. Key considerations
3. Recommendations
"""


@mcp.prompt()
def code_review(code: str, language: str = "python") -> str:
    """
    Generate a code review prompt.

    Args:
        code: Code to review
        language: Programming language

    Returns:
        Code review prompt
    """
    return f"""Review the following {language} code:

```{language}
{code}
```

Please evaluate:
1. Correctness - Does it work as intended?
2. Performance - Are there efficiency issues?
3. Security - Are there vulnerabilities?
4. Style - Does it follow best practices?
5. Maintainability - Is it easy to understand and modify?

Provide specific suggestions for improvement.
"""


@mcp.prompt()
def summarize(text: str, format: str = "bullets") -> str:
    """
    Generate a summarization prompt.

    Args:
        text: Text to summarize
        format: Output format (bullets, paragraph, outline)

    Returns:
        Summarization prompt
    """
    format_instructions = {
        "bullets": "Use bullet points for key takeaways.",
        "paragraph": "Write a concise paragraph summary.",
        "outline": "Create a structured outline with headers.",
    }

    return f"""Summarize the following text:

{text}

{format_instructions.get(format, format_instructions["bullets"])}

Focus on the most important information and main conclusions.
"""


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MCP server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http", "sse"],
        default="stdio",
        help="Transport type",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transports",
    )

    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run(transport=args.transport, port=args.port)
