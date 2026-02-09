#!/usr/bin/env python3
"""Generate MCP tool boilerplate code."""

import argparse
from typing import List, Tuple


def parse_parameters(params: List[str]) -> List[Tuple[str, str, str, str]]:
    """Parse parameter specifications.

    Format: name:type:description[:default]
    """
    parsed = []
    for param in params:
        parts = param.split(":")
        if len(parts) < 3:
            raise ValueError(f"Invalid parameter format: {param}")

        name = parts[0]
        ptype = parts[1]
        description = parts[2]
        default = parts[3] if len(parts) > 3 else None

        parsed.append((name, ptype, description, default))

    return parsed


def generate_sync_tool(
    name: str,
    description: str,
    params: List[Tuple[str, str, str, str]],
    return_type: str,
) -> str:
    """Generate synchronous tool code."""
    # Build parameter string
    param_strs = []
    for pname, ptype, pdesc, pdefault in params:
        if pdefault:
            param_strs.append(f"{pname}: {ptype} = {pdefault}")
        else:
            param_strs.append(f"{pname}: {ptype}")

    params_str = ", ".join(param_strs)

    # Build docstring
    doc_params = "\n".join(
        f"        {pname}: {pdesc}"
        for pname, _, pdesc, _ in params
    )

    return f'''@mcp.tool()
def {name}({params_str}) -> {return_type}:
    """{description}

    Args:
{doc_params}

    Returns:
        {return_type}: Description of return value
    """
    # TODO: Implement {name}
    pass
'''


def generate_async_tool(
    name: str,
    description: str,
    params: List[Tuple[str, str, str, str]],
    return_type: str,
) -> str:
    """Generate asynchronous tool code."""
    param_strs = []
    for pname, ptype, pdesc, pdefault in params:
        if pdefault:
            param_strs.append(f"{pname}: {ptype} = {pdefault}")
        else:
            param_strs.append(f"{pname}: {ptype}")

    params_str = ", ".join(param_strs)

    doc_params = "\n".join(
        f"        {pname}: {pdesc}"
        for pname, _, pdesc, _ in params
    )

    return f'''@mcp.tool()
async def {name}({params_str}) -> {return_type}:
    """{description}

    Args:
{doc_params}

    Returns:
        {return_type}: Description of return value
    """
    # TODO: Implement {name}
    pass
'''


def generate_context_tool(
    name: str,
    description: str,
    params: List[Tuple[str, str, str, str]],
    return_type: str,
) -> str:
    """Generate tool with context access."""
    param_strs = []
    for pname, ptype, pdesc, pdefault in params:
        if pdefault:
            param_strs.append(f"{pname}: {ptype} = {pdefault}")
        else:
            param_strs.append(f"{pname}: {ptype}")

    # Add context parameter
    param_strs.append("ctx: Context[ServerSession, AppContext]")
    params_str = ", ".join(param_strs)

    doc_params = "\n".join(
        f"        {pname}: {pdesc}"
        for pname, _, pdesc, _ in params
    )

    return f'''from mcp.server.fastmcp import Context
from mcp.server.session import ServerSession

@mcp.tool()
async def {name}({params_str}) -> {return_type}:
    """{description}

    Args:
{doc_params}

    Returns:
        {return_type}: Description of return value
    """
    # Access lifespan context
    app = ctx.request_context.lifespan_context

    # Report progress (optional)
    await ctx.report_progress(progress=0, total=100)

    # Log (optional)
    ctx.info(f"Processing {name}...")

    # TODO: Implement {name}
    pass
'''


def generate_http_tool(name: str, endpoint: str, method: str) -> str:
    """Generate HTTP API tool."""
    return f'''@mcp.tool()
async def {name}(params: dict) -> dict:
    """Call {endpoint} API endpoint.

    Args:
        params: Request parameters

    Returns:
        API response data
    """
    import httpx

    url = f"{{API_BASE_URL}}{endpoint}"
    headers = {{"Authorization": f"Bearer {{API_KEY}}"}}

    async with httpx.AsyncClient() as client:
        response = await client.{method.lower()}(
            url,
            {"json=params" if method in ["POST", "PUT", "PATCH"] else "params=params"},
            headers=headers,
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
'''


def generate_database_tool(name: str, operation: str) -> str:
    """Generate database operation tool."""
    templates = {
        "query": '''@mcp.tool()
async def {name}(
    sql: str,
    ctx: Context[ServerSession, AppContext]
) -> list[dict]:
    """Execute a database query.

    Args:
        sql: SQL query (SELECT only)

    Returns:
        Query results
    """
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries allowed")

    db = ctx.request_context.lifespan_context.db
    return await db.query(sql)
''',
        "insert": '''@mcp.tool()
async def {name}(
    table: str,
    data: dict,
    ctx: Context[ServerSession, AppContext]
) -> dict:
    """Insert a record into the database.

    Args:
        table: Table name
        data: Record data

    Returns:
        Inserted record with ID
    """
    db = ctx.request_context.lifespan_context.db

    columns = ", ".join(data.keys())
    placeholders = ", ".join(f"${i+1}" for i in range(len(data)))
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING *"

    result = await db.query(sql, *data.values())
    return result[0] if result else None
''',
        "update": '''@mcp.tool()
async def {name}(
    table: str,
    id: int,
    data: dict,
    ctx: Context[ServerSession, AppContext]
) -> dict | None:
    """Update a record in the database.

    Args:
        table: Table name
        id: Record ID
        data: Fields to update

    Returns:
        Updated record or None
    """
    db = ctx.request_context.lifespan_context.db

    sets = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(data.keys()))
    sql = f"UPDATE {table} SET {sets} WHERE id = $1 RETURNING *"

    result = await db.query(sql, id, *data.values())
    return result[0] if result else None
''',
        "delete": '''@mcp.tool()
async def {name}(
    table: str,
    id: int,
    ctx: Context[ServerSession, AppContext]
) -> bool:
    """Delete a record from the database.

    Args:
        table: Table name
        id: Record ID

    Returns:
        True if deleted
    """
    db = ctx.request_context.lifespan_context.db
    result = await db.execute(f"DELETE FROM {table} WHERE id = $1", id)
    return result == "DELETE 1"
''',
    }

    template = templates.get(operation, templates["query"])
    return template.format(name=name)


def generate_pydantic_tool(
    name: str,
    description: str,
    input_fields: List[Tuple[str, str, str]],
    output_fields: List[Tuple[str, str, str]],
) -> str:
    """Generate tool with Pydantic models."""
    input_name = f"{name.title().replace('_', '')}Input"
    output_name = f"{name.title().replace('_', '')}Output"

    input_fields_str = "\n    ".join(
        f'{fname}: {ftype} = Field(description="{fdesc}")'
        for fname, ftype, fdesc in input_fields
    )

    output_fields_str = "\n    ".join(
        f'{fname}: {ftype} = Field(description="{fdesc}")'
        for fname, ftype, fdesc in output_fields
    )

    return f'''from pydantic import BaseModel, Field

class {input_name}(BaseModel):
    """Input schema for {name}."""
    {input_fields_str}


class {output_name}(BaseModel):
    """Output schema for {name}."""
    {output_fields_str}


@mcp.tool()
def {name}(params: {input_name}) -> {output_name}:
    """{description}

    Args:
        params: Input parameters

    Returns:
        Structured output
    """
    # TODO: Implement {name}
    return {output_name}(
        {", ".join(f"{fname}=..." for fname, _, _ in output_fields)}
    )
'''


def main():
    parser = argparse.ArgumentParser(
        description="Generate MCP tool boilerplate"
    )
    parser.add_argument("name", help="Tool name")
    parser.add_argument(
        "--type", "-t",
        choices=["sync", "async", "context", "http", "database", "pydantic"],
        default="async",
        help="Tool type"
    )
    parser.add_argument(
        "--description", "-d",
        default="Tool description",
        help="Tool description"
    )
    parser.add_argument(
        "--params", "-p",
        nargs="*",
        default=[],
        help="Parameters as name:type:description[:default]"
    )
    parser.add_argument(
        "--return-type", "-r",
        default="str",
        help="Return type"
    )
    parser.add_argument(
        "--endpoint",
        help="API endpoint (for http type)"
    )
    parser.add_argument(
        "--method",
        default="GET",
        help="HTTP method (for http type)"
    )
    parser.add_argument(
        "--operation",
        default="query",
        choices=["query", "insert", "update", "delete"],
        help="Database operation (for database type)"
    )

    args = parser.parse_args()

    if args.type == "sync":
        params = parse_parameters(args.params)
        code = generate_sync_tool(args.name, args.description, params, args.return_type)
    elif args.type == "async":
        params = parse_parameters(args.params)
        code = generate_async_tool(args.name, args.description, params, args.return_type)
    elif args.type == "context":
        params = parse_parameters(args.params)
        code = generate_context_tool(args.name, args.description, params, args.return_type)
    elif args.type == "http":
        endpoint = args.endpoint or f"/api/{args.name}"
        code = generate_http_tool(args.name, endpoint, args.method)
    elif args.type == "database":
        code = generate_database_tool(args.name, args.operation)
    elif args.type == "pydantic":
        # Parse input/output from params
        input_fields = [("query", "str", "Search query")]
        output_fields = [("result", "str", "Result")]
        code = generate_pydantic_tool(args.name, args.description, input_fields, output_fields)

    print(code)


if __name__ == "__main__":
    main()
