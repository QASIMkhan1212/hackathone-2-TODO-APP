"""Common tool patterns for OpenAI Agents SDK.

This template provides reusable tool patterns for common operations
including HTTP APIs, databases, files, and more.
"""

from typing import Optional, Any
from pydantic import BaseModel
from agents import function_tool, ToolError


# =============================================================================
# HTTP API Tools
# =============================================================================


@function_tool
async def http_get(url: str, headers: Optional[dict] = None) -> dict:
    """Make an HTTP GET request.

    Args:
        url: The URL to request
        headers: Optional HTTP headers

    Returns:
        Response data as dict
    """
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers or {},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


@function_tool
async def http_post(
    url: str,
    data: dict,
    headers: Optional[dict] = None
) -> dict:
    """Make an HTTP POST request.

    Args:
        url: The URL to request
        data: JSON body data
        headers: Optional HTTP headers

    Returns:
        Response data as dict
    """
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json=data,
            headers=headers or {},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


# =============================================================================
# Database Tools (PostgreSQL with asyncpg)
# =============================================================================


class DatabaseConfig:
    """Database configuration singleton."""
    pool = None

    @classmethod
    async def get_pool(cls):
        if cls.pool is None:
            import asyncpg
            import os
            cls.pool = await asyncpg.create_pool(
                os.getenv("DATABASE_URL", "postgresql://localhost/mydb")
            )
        return cls.pool


@function_tool
async def db_query(
    query: str,
    params: Optional[list] = None
) -> list[dict]:
    """Execute a read-only database query.

    Args:
        query: SQL query string (SELECT only)
        params: Query parameters

    Returns:
        Query results as list of dicts
    """
    if not query.strip().upper().startswith("SELECT"):
        raise ToolError("Only SELECT queries are allowed")

    pool = await DatabaseConfig.get_pool()
    async with pool.acquire() as conn:
        results = await conn.fetch(query, *(params or []))
        return [dict(r) for r in results]


@function_tool
async def db_execute(
    query: str,
    params: Optional[list] = None
) -> str:
    """Execute a database modification query.

    Args:
        query: SQL query string (INSERT, UPDATE, DELETE)
        params: Query parameters

    Returns:
        Execution status message
    """
    pool = await DatabaseConfig.get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(query, *(params or []))
        return result


# =============================================================================
# File System Tools
# =============================================================================


@function_tool
def read_file(path: str, encoding: str = "utf-8") -> str:
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
    if not file_path.is_file():
        raise ToolError(f"Not a file: {path}")

    # Security: prevent reading sensitive files
    sensitive_patterns = [".env", "credentials", "secret", ".pem", ".key"]
    if any(p in path.lower() for p in sensitive_patterns):
        raise ToolError("Cannot read sensitive files")

    return file_path.read_text(encoding=encoding)


@function_tool
def write_file(
    path: str,
    content: str,
    encoding: str = "utf-8"
) -> bool:
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

    # Security: restrict write locations
    allowed_dirs = ["./output", "./tmp", "./data"]
    if not any(path.startswith(d) for d in allowed_dirs):
        raise ToolError(f"Can only write to: {allowed_dirs}")

    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding=encoding)
    return True


@function_tool
def list_directory(
    directory: str,
    pattern: str = "*"
) -> list[str]:
    """List files in a directory.

    Args:
        directory: Directory path
        pattern: Glob pattern to match

    Returns:
        List of file paths
    """
    from pathlib import Path

    dir_path = Path(directory)
    if not dir_path.exists():
        raise ToolError(f"Directory not found: {directory}")
    if not dir_path.is_dir():
        raise ToolError(f"Not a directory: {directory}")

    return [str(p) for p in dir_path.glob(pattern)]


# =============================================================================
# Data Processing Tools
# =============================================================================


class DataAnalysis(BaseModel):
    """Analysis result schema."""
    row_count: int
    column_count: int
    columns: list[str]
    summary: dict[str, Any]


@function_tool
def analyze_csv(path: str) -> DataAnalysis:
    """Analyze a CSV file.

    Args:
        path: Path to CSV file

    Returns:
        Analysis results
    """
    import csv
    from pathlib import Path

    file_path = Path(path)
    if not file_path.exists():
        raise ToolError(f"File not found: {path}")

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return DataAnalysis(
            row_count=0,
            column_count=0,
            columns=[],
            summary={}
        )

    columns = list(rows[0].keys())

    # Basic summary
    summary = {}
    for col in columns:
        values = [r[col] for r in rows if r[col]]
        summary[col] = {
            "non_null_count": len(values),
            "unique_count": len(set(values)),
            "sample": values[:3] if values else [],
        }

    return DataAnalysis(
        row_count=len(rows),
        column_count=len(columns),
        columns=columns,
        summary=summary,
    )


@function_tool
def transform_json(
    data: dict,
    jq_expression: str
) -> Any:
    """Transform JSON data using a jq-like expression.

    Args:
        data: Input JSON data
        jq_expression: Transformation expression (simplified jq syntax)

    Returns:
        Transformed data
    """
    # Simplified jq-like transformations
    # In production, consider using pyjq or jmespath

    if jq_expression == ".":
        return data

    if jq_expression.startswith("."):
        keys = jq_expression[1:].split(".")
        result = data
        for key in keys:
            if isinstance(result, dict) and key in result:
                result = result[key]
            elif isinstance(result, list) and key.isdigit():
                result = result[int(key)]
            else:
                raise ToolError(f"Key not found: {key}")
        return result

    raise ToolError(f"Unsupported expression: {jq_expression}")


# =============================================================================
# Utility Tools
# =============================================================================


@function_tool
def get_current_datetime(
    timezone: str = "UTC",
    format: str = "iso"
) -> str:
    """Get current date and time.

    Args:
        timezone: Timezone name (e.g., 'UTC', 'America/New_York')
        format: Output format ('iso', 'date', 'time', 'human')

    Returns:
        Formatted datetime string
    """
    from datetime import datetime
    import zoneinfo

    try:
        tz = zoneinfo.ZoneInfo(timezone)
    except Exception:
        tz = zoneinfo.ZoneInfo("UTC")

    now = datetime.now(tz)

    formats = {
        "iso": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "human": now.strftime("%B %d, %Y at %I:%M %p"),
    }

    return formats.get(format, now.isoformat())


@function_tool
def calculate(expression: str) -> float:
    """Safely evaluate a mathematical expression.

    Args:
        expression: Math expression (e.g., "2 + 2 * 3")

    Returns:
        Calculated result
    """
    import ast
    import operator

    # Safe operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def eval_node(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            return operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            return operators[type(node.op)](operand)
        else:
            raise ToolError(f"Unsupported operation: {type(node)}")

    try:
        tree = ast.parse(expression, mode='eval')
        return eval_node(tree.body)
    except Exception as e:
        raise ToolError(f"Invalid expression: {e}")


@function_tool
def generate_uuid() -> str:
    """Generate a unique identifier.

    Returns:
        UUID string
    """
    import uuid
    return str(uuid.uuid4())


@function_tool
def hash_text(text: str, algorithm: str = "sha256") -> str:
    """Generate a hash of text.

    Args:
        text: Text to hash
        algorithm: Hash algorithm ('md5', 'sha256', 'sha512')

    Returns:
        Hex digest of hash
    """
    import hashlib

    algorithms = {
        "md5": hashlib.md5,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
    }

    if algorithm not in algorithms:
        raise ToolError(f"Unsupported algorithm: {algorithm}")

    return algorithms[algorithm](text.encode()).hexdigest()


# =============================================================================
# Tool Collections
# =============================================================================


# HTTP tools for web interactions
HTTP_TOOLS = [http_get, http_post]

# Database tools for data persistence
DATABASE_TOOLS = [db_query, db_execute]

# File tools for file system operations
FILE_TOOLS = [read_file, write_file, list_directory]

# Data tools for analysis and transformation
DATA_TOOLS = [analyze_csv, transform_json]

# Utility tools for common operations
UTILITY_TOOLS = [get_current_datetime, calculate, generate_uuid, hash_text]

# All tools combined
ALL_TOOLS = HTTP_TOOLS + FILE_TOOLS + DATA_TOOLS + UTILITY_TOOLS


# =============================================================================
# Usage Example
# =============================================================================


if __name__ == "__main__":
    from agents import Agent, Runner

    # Create agent with utility tools
    agent = Agent(
        name="UtilityAgent",
        instructions="You are a helpful assistant with access to various utility tools.",
        tools=UTILITY_TOOLS,
    )

    async def main():
        result = await Runner.run(agent, "What time is it in New York?")
        print(result.final_output)

    import asyncio
    asyncio.run(main())
