#!/usr/bin/env python3
"""Set up MCP development environment."""

import argparse
from pathlib import Path


def generate_pyproject_toml(name: str) -> str:
    """Generate pyproject.toml for MCP server."""
    return f'''[project]
name = "{name}"
version = "0.1.0"
description = "MCP server for {name}"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.0.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.10"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
'''


def generate_requirements_txt() -> str:
    """Generate requirements.txt."""
    return '''# MCP SDK
mcp[cli]>=1.0.0

# HTTP client
httpx>=0.27.0

# Data validation
pydantic>=2.0.0

# Development
pytest>=8.0.0
pytest-asyncio>=0.23.0
ruff>=0.1.0
mypy>=1.8.0
'''


def generate_gitignore() -> str:
    """Generate .gitignore."""
    return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Type checking
.mypy_cache/

# MCP
.mcp/
'''


def generate_env_example() -> str:
    """Generate .env.example."""
    return '''# MCP Server Configuration
MCP_SERVER_NAME=my-server
MCP_SERVER_PORT=8000

# API Keys (if needed)
API_KEY=your-api-key-here

# Database (if needed)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# External APIs (if needed)
EXTERNAL_API_URL=https://api.example.com
EXTERNAL_API_KEY=your-external-key
'''


def generate_claude_config(name: str, server_path: str) -> str:
    """Generate Claude Desktop configuration."""
    return f'''{{
  "mcpServers": {{
    "{name}": {{
      "command": "python",
      "args": ["{server_path}"],
      "env": {{}}
    }}
  }}
}}
'''


def generate_readme(name: str) -> str:
    """Generate README.md."""
    return f'''# {name} MCP Server

An MCP server providing tools and resources for {name}.

## Installation

```bash
# Install dependencies
pip install -e .

# Or with uv
uv pip install -e .
```

## Running the Server

### Development (stdio)

```bash
python src/server.py
```

### HTTP Server

```bash
python src/server.py --transport http --port 8000
```

## Configuration

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{{
  "mcpServers": {{
    "{name}": {{
      "command": "python",
      "args": ["/path/to/src/server.py"]
    }}
  }}
}}
```

### Claude CLI

```bash
claude mcp add {name} python /path/to/src/server.py
```

## Testing

```bash
# Run tests
pytest

# Test with MCP Inspector
npx -y @modelcontextprotocol/inspector
```

## Tools

| Tool | Description |
|------|-------------|
| `hello` | Say hello to someone |
| `add` | Add two numbers |

## Resources

| Resource | Description |
|----------|-------------|
| `config://server` | Server configuration |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Format code
ruff format .

# Lint
ruff check .

# Type check
mypy src/
```
'''


def generate_test_file(name: str) -> str:
    """Generate test file."""
    return f'''"""Tests for {name} MCP server."""

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client


@pytest.fixture
async def client():
    """Create MCP client connected to server."""
    async with stdio_client(["python", "src/server.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


@pytest.mark.asyncio
async def test_list_tools(client):
    """Test listing available tools."""
    result = await client.list_tools()
    tool_names = [t.name for t in result.tools]

    assert "hello" in tool_names
    assert "add" in tool_names


@pytest.mark.asyncio
async def test_hello_tool(client):
    """Test hello tool."""
    result = await client.call_tool("hello", {{"name": "World"}})
    assert result.content[0].text == "Hello, World!"


@pytest.mark.asyncio
async def test_add_tool(client):
    """Test add tool."""
    result = await client.call_tool("add", {{"a": 5, "b": 3}})
    assert "8" in result.content[0].text


@pytest.mark.asyncio
async def test_list_resources(client):
    """Test listing resources."""
    result = await client.list_resources()
    uris = [r.uri for r in result.resources]

    assert "config://server" in uris


@pytest.mark.asyncio
async def test_read_resource(client):
    """Test reading a resource."""
    result = await client.read_resource("config://server")
    content = result.contents[0].text

    assert "{name}" in content
'''


def setup_mcp_project(
    output_path: Path,
    name: str,
) -> None:
    """Set up MCP project structure."""
    print(f"Setting up MCP project: {name}")
    print("=" * 50)

    # Create directories
    src_path = output_path / "src"
    tests_path = output_path / "tests"
    src_path.mkdir(parents=True, exist_ok=True)
    tests_path.mkdir(exist_ok=True)

    # Generate files
    files = [
        (output_path / "pyproject.toml", generate_pyproject_toml(name)),
        (output_path / "requirements.txt", generate_requirements_txt()),
        (output_path / ".gitignore", generate_gitignore()),
        (output_path / ".env.example", generate_env_example()),
        (output_path / "README.md", generate_readme(name)),
        (output_path / "claude_config.json", generate_claude_config(name, "src/server.py")),
        (tests_path / f"test_{name}.py", generate_test_file(name)),
        (tests_path / "__init__.py", ""),
        (src_path / "__init__.py", ""),
    ]

    # Generate server file
    from create_server import generate_basic_server
    files.append((
        src_path / "server.py",
        generate_basic_server(name, f"MCP server for {name}")
    ))

    for file_path, content in files:
        file_path.write_text(content, encoding="utf-8")
        print(f"  Created: {file_path}")

    print("\n" + "=" * 50)
    print("MCP project setup complete!")
    print("\nNext steps:")
    print(f"  1. cd {output_path}")
    print("  2. pip install -e '.[dev]'")
    print("  3. python src/server.py")
    print("\nTo add to Claude Desktop:")
    print(f"  Copy claude_config.json contents to your Claude config")
    print("\nTo test:")
    print("  pytest")
    print("  npx -y @modelcontextprotocol/inspector")


def main():
    parser = argparse.ArgumentParser(
        description="Set up MCP development environment"
    )
    parser.add_argument("name", help="Project name")
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output directory (default: ./<name>)"
    )

    args = parser.parse_args()
    output_path = args.output or Path(args.name.lower().replace(" ", "-"))

    setup_mcp_project(output_path, args.name)


if __name__ == "__main__":
    main()
