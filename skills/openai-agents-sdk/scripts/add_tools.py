#!/usr/bin/env python3
"""Generate tool definitions for OpenAI Agents SDK."""

import argparse


def generate_function_tool(
    name: str,
    description: str,
    params: list[tuple[str, str, str]],
    return_type: str = "str",
    is_async: bool = False,
) -> str:
    """Generate a function tool definition."""
    async_prefix = "async " if is_async else ""
    await_prefix = "await " if is_async else ""

    # Build parameters
    param_lines = []
    docstring_params = []
    for param_name, param_type, param_desc in params:
        param_lines.append(f"{param_name}: {param_type}")
        docstring_params.append(f"        {param_name}: {param_desc}")

    params_str = ", ".join(param_lines)
    docstring_params_str = "\n".join(docstring_params)

    return f'''@function_tool
{async_prefix}def {name}({params_str}) -> {return_type}:
    """{description}

    Args:
{docstring_params_str}

    Returns:
        {return_type}: Description of return value
    """
    # TODO: Implement {name}
    {await_prefix}pass
'''


def generate_http_tool(name: str, endpoint: str, method: str = "GET") -> str:
    """Generate an HTTP API tool."""
    return f'''@function_tool
async def {name}(params: dict) -> dict:
    """Call the {endpoint} API endpoint.

    Args:
        params: Request parameters

    Returns:
        API response data
    """
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.{method.lower()}(
            "{endpoint}",
            {"json" if method in ["POST", "PUT", "PATCH"] else "params"}=params,
        )
        response.raise_for_status()
        return response.json()
'''


def generate_database_tool(name: str, operation: str) -> str:
    """Generate a database operation tool."""
    operations = {
        "query": '''@function_tool
async def {name}(query: str, params: list | None = None) -> list[dict]:
    """Execute a database query.

    Args:
        query: SQL query string
        params: Query parameters for safe interpolation

    Returns:
        Query results as list of dicts
    """
    async with db_pool.acquire() as conn:
        results = await conn.fetch(query, *(params or []))
        return [dict(r) for r in results]
''',
        "insert": '''@function_tool
async def {name}(table: str, data: dict) -> int:
    """Insert a record into the database.

    Args:
        table: Table name
        data: Record data as dict

    Returns:
        ID of inserted record
    """
    columns = ", ".join(data.keys())
    placeholders = ", ".join(f"${i+1}" for i in range(len(data)))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"

    async with db_pool.acquire() as conn:
        result = await conn.fetchval(query, *data.values())
        return result
''',
        "update": '''@function_tool
async def {name}(table: str, id: int, data: dict) -> bool:
    """Update a record in the database.

    Args:
        table: Table name
        id: Record ID
        data: Fields to update

    Returns:
        True if record was updated
    """
    sets = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(data.keys()))
    query = f"UPDATE {table} SET {sets} WHERE id = $1"

    async with db_pool.acquire() as conn:
        result = await conn.execute(query, id, *data.values())
        return result == "UPDATE 1"
''',
    }

    template = operations.get(operation, operations["query"])
    return template.format(name=name)


def generate_file_tool(name: str, operation: str) -> str:
    """Generate a file operation tool."""
    operations = {
        "read": '''@function_tool
def {name}(path: str, encoding: str = "utf-8") -> str:
    """Read contents of a file.

    Args:
        path: File path to read
        encoding: File encoding

    Returns:
        File contents as string
    """
    from pathlib import Path

    file_path = Path(path)
    if not file_path.exists():
        raise ToolError(f"File not found: {path}")

    return file_path.read_text(encoding=encoding)
''',
        "write": '''@function_tool
def {name}(path: str, content: str, encoding: str = "utf-8") -> bool:
    """Write content to a file.

    Args:
        path: File path to write
        content: Content to write
        encoding: File encoding

    Returns:
        True if successful
    """
    from pathlib import Path

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding=encoding)
    return True
''',
        "list": '''@function_tool
def {name}(directory: str, pattern: str = "*") -> list[str]:
    """List files in a directory.

    Args:
        directory: Directory path
        pattern: Glob pattern to match

    Returns:
        List of file paths
    """
    from pathlib import Path

    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise ToolError(f"Not a directory: {directory}")

    return [str(p) for p in dir_path.glob(pattern)]
''',
    }

    template = operations.get(operation, operations["read"])
    return template.format(name=name)


def main():
    parser = argparse.ArgumentParser(
        description="Generate tool definitions for OpenAI Agents SDK"
    )
    parser.add_argument("name", help="Tool function name")
    parser.add_argument(
        "--type", "-t",
        choices=["function", "http", "database", "file"],
        default="function",
        help="Tool type"
    )
    parser.add_argument(
        "--description", "-d",
        default="Tool description",
        help="Tool description (for function type)"
    )
    parser.add_argument(
        "--params",
        nargs="*",
        default=[],
        help="Parameters as 'name:type:description' (for function type)"
    )
    parser.add_argument(
        "--async",
        dest="is_async",
        action="store_true",
        help="Generate async function"
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
        help="Operation type (for database/file type)"
    )

    args = parser.parse_args()

    if args.type == "function":
        params = []
        for p in args.params:
            parts = p.split(":")
            if len(parts) >= 3:
                params.append((parts[0], parts[1], ":".join(parts[2:])))
            elif len(parts) == 2:
                params.append((parts[0], parts[1], f"The {parts[0]} parameter"))
            else:
                params.append((parts[0], "str", f"The {parts[0]} parameter"))

        code = generate_function_tool(
            args.name,
            args.description,
            params,
            is_async=args.is_async
        )
    elif args.type == "http":
        endpoint = args.endpoint or "https://api.example.com/endpoint"
        code = generate_http_tool(args.name, endpoint, args.method)
    elif args.type == "database":
        code = generate_database_tool(args.name, args.operation)
    elif args.type == "file":
        code = generate_file_tool(args.name, args.operation)

    print("# Add to your agent file:\n")
    print("from agents import function_tool, ToolError\n")
    print(code)


if __name__ == "__main__":
    main()
