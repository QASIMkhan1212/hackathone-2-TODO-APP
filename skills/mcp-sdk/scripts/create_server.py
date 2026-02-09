#!/usr/bin/env python3
"""Create a new MCP server with boilerplate code."""

import argparse
from pathlib import Path


def generate_basic_server(name: str, description: str) -> str:
    """Generate a basic MCP server."""
    return f'''"""MCP Server: {name}

{description}
"""

from mcp.server.fastmcp import FastMCP

# Create server
mcp = FastMCP(
    name="{name}",
    instructions="""{description}

Available tools and their purposes will be listed here.
"""
)


# =============================================================================
# Tools
# =============================================================================


@mcp.tool()
def hello(name: str) -> str:
    """Say hello to someone.

    Args:
        name: Name of the person to greet

    Returns:
        Greeting message
    """
    return f"Hello, {{name}}!"


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


# =============================================================================
# Resources
# =============================================================================


@mcp.resource("config://server")
def get_server_config() -> dict:
    """Get server configuration."""
    return {{
        "name": "{name}",
        "version": "1.0.0",
        "status": "running",
    }}


# =============================================================================
# Prompts
# =============================================================================


@mcp.prompt()
def analyze(topic: str) -> str:
    """Generate an analysis prompt.

    Args:
        topic: Topic to analyze

    Returns:
        Analysis prompt
    """
    return f"""Please analyze the following topic: {{topic}}

Provide:
1. Key points
2. Pros and cons
3. Recommendations
"""


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":
    mcp.run()
'''


def generate_api_server(name: str, base_url: str) -> str:
    """Generate an API integration server."""
    return f'''"""MCP Server: {name} API Integration

Provides tools to interact with {name} API.
"""

import os
import httpx
from mcp.server.fastmcp import FastMCP

# Configuration
API_BASE_URL = os.getenv("{name.upper()}_API_URL", "{base_url}")
API_KEY = os.getenv("{name.upper()}_API_KEY", "")

# Create server
mcp = FastMCP(
    name="{name}API",
    instructions="""This server provides integration with the {name} API.

Make sure to set the following environment variables:
- {name.upper()}_API_URL: API base URL
- {name.upper()}_API_KEY: API authentication key
"""
)


# =============================================================================
# HTTP Client Helper
# =============================================================================


async def api_request(
    method: str,
    endpoint: str,
    data: dict | None = None,
) -> dict:
    """Make API request."""
    headers = {{
        "Authorization": f"Bearer {{API_KEY}}",
        "Content-Type": "application/json",
    }}

    url = f"{{API_BASE_URL}}{{endpoint}}"

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = await client.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {{method}}")

        response.raise_for_status()
        return response.json()


# =============================================================================
# Tools
# =============================================================================


@mcp.tool()
async def list_items(limit: int = 10, offset: int = 0) -> list[dict]:
    """List items from the API.

    Args:
        limit: Maximum items to return
        offset: Number of items to skip

    Returns:
        List of items
    """
    return await api_request("GET", f"/items?limit={{limit}}&offset={{offset}}")


@mcp.tool()
async def get_item(item_id: str) -> dict:
    """Get a specific item by ID.

    Args:
        item_id: The item ID

    Returns:
        Item details
    """
    return await api_request("GET", f"/items/{{item_id}}")


@mcp.tool()
async def create_item(name: str, data: dict) -> dict:
    """Create a new item.

    Args:
        name: Item name
        data: Item data

    Returns:
        Created item
    """
    return await api_request("POST", "/items", {{"name": name, **data}})


@mcp.tool()
async def update_item(item_id: str, data: dict) -> dict:
    """Update an existing item.

    Args:
        item_id: The item ID
        data: Updated data

    Returns:
        Updated item
    """
    return await api_request("PUT", f"/items/{{item_id}}", data)


@mcp.tool()
async def delete_item(item_id: str) -> bool:
    """Delete an item.

    Args:
        item_id: The item ID

    Returns:
        True if deleted
    """
    await api_request("DELETE", f"/items/{{item_id}}")
    return True


# =============================================================================
# Resources
# =============================================================================


@mcp.resource("api://status")
async def api_status() -> dict:
    """Get API status."""
    try:
        return await api_request("GET", "/status")
    except Exception as e:
        return {{"status": "error", "message": str(e)}}


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":
    mcp.run()
'''


def generate_database_server(name: str, db_type: str) -> str:
    """Generate a database integration server."""
    return f'''"""MCP Server: {name} Database

Provides tools to interact with the database.
"""

import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "{db_type}://localhost/{name.lower()}")


# =============================================================================
# Database Connection
# =============================================================================


@dataclass
class AppContext:
    db: "Database"


class Database:
    """Simple database wrapper."""

    def __init__(self, url: str):
        self.url = url
        self.pool = None

    async def connect(self):
        # Implement connection logic based on db_type
        import asyncpg
        self.pool = await asyncpg.create_pool(self.url)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def query(self, sql: str, *args) -> list[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *args)
            return [dict(row) for row in rows]

    async def execute(self, sql: str, *args) -> str:
        async with self.pool.acquire() as conn:
            return await conn.execute(sql, *args)


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """Manage database lifecycle."""
    db = Database(DATABASE_URL)
    await db.connect()
    print(f"Connected to database: {{DATABASE_URL}}")

    yield AppContext(db=db)

    await db.disconnect()
    print("Disconnected from database")


# Create server with lifespan
mcp = FastMCP(
    name="{name}Database",
    lifespan=app_lifespan,
    instructions="""Database server for {name}.

Provides SQL query and data manipulation tools.
Always use parameterized queries for safety.
"""
)


# =============================================================================
# Tools
# =============================================================================


@mcp.tool()
async def query(
    sql: str,
    ctx: Context[ServerSession, AppContext]
) -> list[dict]:
    """Execute a SELECT query.

    Args:
        sql: SQL SELECT query

    Returns:
        Query results
    """
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries allowed")

    db = ctx.request_context.lifespan_context.db
    return await db.query(sql)


@mcp.tool()
async def get_tables(
    ctx: Context[ServerSession, AppContext]
) -> list[str]:
    """List all tables in the database.

    Returns:
        List of table names
    """
    db = ctx.request_context.lifespan_context.db
    rows = await db.query("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)
    return [row["table_name"] for row in rows]


@mcp.tool()
async def describe_table(
    table_name: str,
    ctx: Context[ServerSession, AppContext]
) -> list[dict]:
    """Get table schema.

    Args:
        table_name: Name of the table

    Returns:
        Column definitions
    """
    db = ctx.request_context.lifespan_context.db
    return await db.query("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = $1
        ORDER BY ordinal_position
    """, table_name)


@mcp.tool()
async def count_rows(
    table_name: str,
    ctx: Context[ServerSession, AppContext]
) -> int:
    """Count rows in a table.

    Args:
        table_name: Name of the table

    Returns:
        Row count
    """
    # Sanitize table name
    if not table_name.replace("_", "").isalnum():
        raise ValueError("Invalid table name")

    db = ctx.request_context.lifespan_context.db
    rows = await db.query(f"SELECT COUNT(*) as count FROM {{table_name}}")
    return rows[0]["count"]


# =============================================================================
# Resources
# =============================================================================


@mcp.resource("db://schema")
async def database_schema(ctx: Context[ServerSession, AppContext]) -> dict:
    """Get database schema overview."""
    db = ctx.request_context.lifespan_context.db
    tables = await db.query("""
        SELECT
            t.table_name,
            array_agg(c.column_name || ' ' || c.data_type) as columns
        FROM information_schema.tables t
        JOIN information_schema.columns c ON t.table_name = c.table_name
        WHERE t.table_schema = 'public'
        GROUP BY t.table_name
    """)
    return {{"tables": tables}}


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":
    mcp.run()
'''


def main():
    parser = argparse.ArgumentParser(
        description="Create a new MCP server"
    )
    parser.add_argument("name", help="Server name")
    parser.add_argument(
        "--type", "-t",
        choices=["basic", "api", "database"],
        default="basic",
        help="Server type"
    )
    parser.add_argument(
        "--description", "-d",
        default="A custom MCP server",
        help="Server description"
    )
    parser.add_argument(
        "--api-url",
        default="https://api.example.com/v1",
        help="API base URL (for api type)"
    )
    parser.add_argument(
        "--db-type",
        default="postgresql",
        help="Database type (for database type)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file path"
    )

    args = parser.parse_args()

    if args.type == "basic":
        code = generate_basic_server(args.name, args.description)
    elif args.type == "api":
        code = generate_api_server(args.name, args.api_url)
    elif args.type == "database":
        code = generate_database_server(args.name, args.db_type)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(code, encoding="utf-8")
        print(f"Created: {args.output}")
    else:
        print(code)


if __name__ == "__main__":
    main()
