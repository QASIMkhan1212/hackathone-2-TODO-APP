"""Common MCP Tool Patterns.

Reusable tool templates for common operations.
"""

import os
from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from mcp.types import CallToolResult, TextContent, McpError, ErrorCode
from pydantic import BaseModel, Field


# =============================================================================
# Initialize Server (for standalone use)
# =============================================================================

mcp = FastMCP("ToolsExample")


# =============================================================================
# HTTP API Tools
# =============================================================================


@mcp.tool()
async def http_get(url: str, headers: dict[str, str] | None = None) -> dict:
    """
    Make an HTTP GET request.

    Args:
        url: URL to request
        headers: Optional HTTP headers

    Returns:
        Response data
    """
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers or {},
            timeout=30.0,
        )
        response.raise_for_status()

        return {
            "status": response.status_code,
            "headers": dict(response.headers),
            "data": response.json() if "application/json" in response.headers.get("content-type", "") else response.text,
        }


@mcp.tool()
async def http_post(
    url: str,
    data: dict,
    headers: dict[str, str] | None = None,
) -> dict:
    """
    Make an HTTP POST request.

    Args:
        url: URL to request
        data: JSON body data
        headers: Optional HTTP headers

    Returns:
        Response data
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

        return {
            "status": response.status_code,
            "data": response.json() if "application/json" in response.headers.get("content-type", "") else response.text,
        }


# =============================================================================
# File System Tools
# =============================================================================


ALLOWED_PATHS = [os.getcwd(), "/tmp"]  # Customize allowed paths


def validate_path(path: str) -> str:
    """Validate and resolve file path."""
    import os.path

    resolved = os.path.abspath(path)

    # Security: Check against allowed paths
    if not any(resolved.startswith(allowed) for allowed in ALLOWED_PATHS):
        raise McpError(ErrorCode.INVALID_PARAMS, f"Path not allowed: {path}")

    return resolved


@mcp.tool()
def read_file(path: str, encoding: str = "utf-8") -> str:
    """
    Read contents of a file.

    Args:
        path: File path to read
        encoding: File encoding

    Returns:
        File contents
    """
    resolved = validate_path(path)

    if not os.path.exists(resolved):
        raise McpError(ErrorCode.NOT_FOUND, f"File not found: {path}")

    with open(resolved, encoding=encoding) as f:
        return f.read()


@mcp.tool()
def write_file(path: str, content: str, encoding: str = "utf-8") -> bool:
    """
    Write content to a file.

    Args:
        path: File path to write
        content: Content to write
        encoding: File encoding

    Returns:
        True if successful
    """
    resolved = validate_path(path)

    # Create parent directories
    os.makedirs(os.path.dirname(resolved), exist_ok=True)

    with open(resolved, "w", encoding=encoding) as f:
        f.write(content)

    return True


@mcp.tool()
def list_directory(
    path: str,
    pattern: str = "*",
    recursive: bool = False,
) -> list[dict]:
    """
    List files in a directory.

    Args:
        path: Directory path
        pattern: Glob pattern to match
        recursive: Search recursively

    Returns:
        List of file information
    """
    import glob

    resolved = validate_path(path)

    if not os.path.isdir(resolved):
        raise McpError(ErrorCode.NOT_FOUND, f"Directory not found: {path}")

    glob_pattern = os.path.join(resolved, "**" if recursive else "", pattern)
    matches = glob.glob(glob_pattern, recursive=recursive)

    return [
        {
            "path": match,
            "name": os.path.basename(match),
            "type": "directory" if os.path.isdir(match) else "file",
            "size": os.path.getsize(match) if os.path.isfile(match) else None,
            "modified": datetime.fromtimestamp(os.path.getmtime(match)).isoformat(),
        }
        for match in matches
    ]


# =============================================================================
# Data Processing Tools
# =============================================================================


class DataAnalysisResult(BaseModel):
    """Result of data analysis."""
    row_count: int
    column_count: int
    columns: list[str]
    dtypes: dict[str, str]
    summary: dict[str, Any]


@mcp.tool()
def analyze_csv(path: str, delimiter: str = ",") -> DataAnalysisResult:
    """
    Analyze a CSV file.

    Args:
        path: Path to CSV file
        delimiter: Column delimiter

    Returns:
        Analysis results
    """
    import csv

    resolved = validate_path(path)

    with open(resolved, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)

    if not rows:
        return DataAnalysisResult(
            row_count=0,
            column_count=0,
            columns=[],
            dtypes={},
            summary={},
        )

    columns = list(rows[0].keys())

    # Infer types and calculate summary
    dtypes = {}
    summary = {}

    for col in columns:
        values = [r[col] for r in rows if r[col]]

        # Infer type
        if all(v.isdigit() for v in values):
            dtypes[col] = "integer"
            int_values = [int(v) for v in values]
            summary[col] = {
                "min": min(int_values),
                "max": max(int_values),
                "mean": sum(int_values) / len(int_values),
            }
        elif all(v.replace(".", "").replace("-", "").isdigit() for v in values):
            dtypes[col] = "float"
        else:
            dtypes[col] = "string"
            summary[col] = {
                "unique": len(set(values)),
                "sample": values[:3],
            }

    return DataAnalysisResult(
        row_count=len(rows),
        column_count=len(columns),
        columns=columns,
        dtypes=dtypes,
        summary=summary,
    )


@mcp.tool()
def transform_json(
    data: dict | list,
    operation: str,
    path: str | None = None,
    value: Any = None,
) -> dict | list:
    """
    Transform JSON data.

    Args:
        data: Input JSON data
        operation: Operation (get, set, delete, filter)
        path: JSON path (dot notation)
        value: Value for set operations

    Returns:
        Transformed data
    """
    import copy

    result = copy.deepcopy(data)

    if operation == "get" and path:
        keys = path.split(".")
        current = result
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                current = current[int(key)]
            else:
                return None
        return current

    elif operation == "set" and path:
        keys = path.split(".")
        current = result
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        return result

    elif operation == "delete" and path:
        keys = path.split(".")
        current = result
        for key in keys[:-1]:
            current = current[key]
        del current[keys[-1]]
        return result

    elif operation == "filter" and isinstance(result, list):
        # Simple key=value filter
        if path and value is not None:
            return [item for item in result if item.get(path) == value]

    return result


# =============================================================================
# Utility Tools
# =============================================================================


@mcp.tool()
def get_current_time(
    timezone: str = "UTC",
    format: str = "iso",
) -> str:
    """
    Get current date and time.

    Args:
        timezone: Timezone (UTC, America/New_York, etc.)
        format: Output format (iso, date, time, human)

    Returns:
        Formatted datetime
    """
    from zoneinfo import ZoneInfo

    try:
        tz = ZoneInfo(timezone)
    except Exception:
        tz = ZoneInfo("UTC")

    now = datetime.now(tz)

    formats = {
        "iso": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "human": now.strftime("%B %d, %Y at %I:%M %p %Z"),
    }

    return formats.get(format, now.isoformat())


@mcp.tool()
def calculate(expression: str) -> float:
    """
    Safely evaluate a mathematical expression.

    Args:
        expression: Math expression (e.g., "2 + 2 * 3")

    Returns:
        Calculated result
    """
    import ast
    import operator

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
            raise McpError(ErrorCode.INVALID_PARAMS, f"Unsupported: {type(node)}")

    try:
        tree = ast.parse(expression, mode="eval")
        return eval_node(tree.body)
    except Exception as e:
        raise McpError(ErrorCode.INVALID_PARAMS, f"Invalid expression: {e}")


@mcp.tool()
def generate_uuid(version: int = 4) -> str:
    """
    Generate a UUID.

    Args:
        version: UUID version (1 or 4)

    Returns:
        UUID string
    """
    import uuid

    if version == 1:
        return str(uuid.uuid1())
    else:
        return str(uuid.uuid4())


@mcp.tool()
def hash_text(text: str, algorithm: str = "sha256") -> str:
    """
    Generate hash of text.

    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha256, sha512)

    Returns:
        Hex digest
    """
    import hashlib

    algorithms = {
        "md5": hashlib.md5,
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
    }

    if algorithm not in algorithms:
        raise McpError(ErrorCode.INVALID_PARAMS, f"Unknown algorithm: {algorithm}")

    return algorithms[algorithm](text.encode()).hexdigest()


# =============================================================================
# Progress Reporting Tool
# =============================================================================


@mcp.tool()
async def batch_process(
    items: list[str],
    operation: str = "uppercase",
    ctx: Context[ServerSession, Any] = None,
) -> list[str]:
    """
    Process items in batch with progress reporting.

    Args:
        items: Items to process
        operation: Operation to perform (uppercase, lowercase, reverse)

    Returns:
        Processed items
    """
    import asyncio

    operations = {
        "uppercase": str.upper,
        "lowercase": str.lower,
        "reverse": lambda s: s[::-1],
    }

    op_func = operations.get(operation, str.upper)
    results = []
    total = len(items)

    for i, item in enumerate(items):
        if ctx:
            await ctx.report_progress(progress=i, total=total)

        # Simulate processing time
        await asyncio.sleep(0.1)
        results.append(op_func(item))

    if ctx:
        await ctx.report_progress(progress=total, total=total)

    return results


# =============================================================================
# Multi-Content Result Tool
# =============================================================================


@mcp.tool()
def generate_report(title: str, sections: list[str]) -> CallToolResult:
    """
    Generate a multi-section report.

    Args:
        title: Report title
        sections: Section names

    Returns:
        Formatted report with multiple content blocks
    """
    content = [
        TextContent(type="text", text=f"# {title}\n\n"),
        TextContent(type="text", text=f"Generated: {datetime.now().isoformat()}\n\n"),
    ]

    for i, section in enumerate(sections, 1):
        content.append(
            TextContent(type="text", text=f"## {i}. {section}\n\nContent for {section}...\n\n")
        )

    return CallToolResult(
        content=content,
        _meta={"title": title, "section_count": len(sections)},
    )


# =============================================================================
# Tool Collections
# =============================================================================

# Group tools by category for easy import
HTTP_TOOLS = [http_get, http_post]
FILE_TOOLS = [read_file, write_file, list_directory]
DATA_TOOLS = [analyze_csv, transform_json]
UTILITY_TOOLS = [get_current_time, calculate, generate_uuid, hash_text]
ADVANCED_TOOLS = [batch_process, generate_report]


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":
    mcp.run()
