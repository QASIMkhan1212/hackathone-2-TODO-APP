#!/usr/bin/env python3
"""Scaffold a new Python project with modern best practices."""

import argparse
from pathlib import Path
from datetime import datetime


def create_directory(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    print(f"  Created: {path}")


def write_file(path: Path, content: str) -> None:
    """Write content to file."""
    path.write_text(content, encoding="utf-8")
    print(f"  Created: {path}")


def scaffold_project(
    name: str,
    base_path: Path,
    author: str = "Your Name",
    email: str = "you@example.com",
    with_cli: bool = False,
) -> None:
    """Create a new Python project structure."""

    # Convert name to package name (lowercase, underscores)
    package_name = name.lower().replace("-", "_")
    project_path = base_path / name

    if project_path.exists():
        print(f"Error: Directory '{project_path}' already exists.")
        return

    print(f"\nScaffolding Python project: {name}")
    print("=" * 50)

    # Create directory structure
    directories = [
        f"src/{package_name}",
        "tests",
    ]

    for dir_name in directories:
        create_directory(project_path / dir_name)

    # Create pyproject.toml
    cli_script = ""
    cli_dep = ""
    if with_cli:
        cli_script = f'''
[project.scripts]
{name} = "{package_name}.cli:app"
'''
        cli_dep = '    "typer>=0.9",\n'

    pyproject_content = f'''[project]
name = "{name}"
version = "0.1.0"
description = "A Python project"
readme = "README.md"
license = {{text = "MIT"}}
requires-python = ">=3.10"
authors = [
    {{name = "{author}", email = "{email}"}},
]
dependencies = [
    "pydantic>=2.0",
{cli_dep}]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.1",
    "mypy>=1.0",
    "pre-commit>=3.0",
]
{cli_script}
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/{package_name}"]

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4"]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-v --cov=src --cov-report=term-missing"
'''
    write_file(project_path / "pyproject.toml", pyproject_content)

    # Create __init__.py
    init_content = f'''"""{name} - A Python project."""

__version__ = "0.1.0"
'''
    write_file(project_path / f"src/{package_name}/__init__.py", init_content)

    # Create main module
    main_content = '''"""Main module."""

from pydantic import BaseModel


class Config(BaseModel):
    """Application configuration."""

    debug: bool = False
    name: str = "app"


def main() -> None:
    """Main entry point."""
    config = Config()
    print(f"Running {config.name}")


if __name__ == "__main__":
    main()
'''
    write_file(project_path / f"src/{package_name}/main.py", main_content)

    # Create CLI if requested
    if with_cli:
        cli_content = f'''"""CLI interface for {name}."""

import typer
from typing import Annotated

from . import __version__

app = typer.Typer(
    name="{name}",
    help="{name} CLI application",
    add_completion=False,
)


@app.command()
def run(
    name: Annotated[str, typer.Argument(help="Name to greet")] = "World",
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose output")] = False,
) -> None:
    """Run the main command."""
    if verbose:
        typer.echo(f"Running in verbose mode")
    typer.echo(f"Hello, {{name}}!")


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo(f"{name} v{{__version__}}")


if __name__ == "__main__":
    app()
'''
        write_file(project_path / f"src/{package_name}/cli.py", cli_content)

    # Create tests
    write_file(project_path / "tests/__init__.py", "")

    conftest_content = '''"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_data() -> dict:
    """Sample test data."""
    return {"key": "value"}
'''
    write_file(project_path / "tests/conftest.py", conftest_content)

    test_content = f'''"""Tests for {package_name}."""

from {package_name}.main import Config, main


def test_config_defaults():
    """Test Config default values."""
    config = Config()
    assert config.debug is False
    assert config.name == "app"


def test_config_custom():
    """Test Config with custom values."""
    config = Config(debug=True, name="custom")
    assert config.debug is True
    assert config.name == "custom"


def test_main(capsys):
    """Test main function output."""
    main()
    captured = capsys.readouterr()
    assert "Running" in captured.out
'''
    write_file(project_path / "tests/test_main.py", test_content)

    # Create README.md
    readme_content = f'''# {name}

A Python project.

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

```python
from {package_name} import main
main()
```
'''
    if with_cli:
        readme_content += f'''
### CLI

```bash
{name} run --help
{name} version
```
'''

    readme_content += '''
## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
ruff format .

# Type checking
mypy src/
```

## License

MIT
'''
    write_file(project_path / "README.md", readme_content)

    # Create .gitignore
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
.Python
*.so

# Virtual environments
.venv/
venv/
ENV/

# Distribution
dist/
build/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.local
'''
    write_file(project_path / ".gitignore", gitignore_content)

    # Create py.typed marker
    write_file(project_path / f"src/{package_name}/py.typed", "")

    print("\n" + "=" * 50)
    print(f"Project '{name}' created successfully!")
    print(f"\nNext steps:")
    print(f"  cd {name}")
    print(f"  python -m venv .venv")
    print(f"  source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows")
    print(f'  pip install -e ".[dev]"')
    print(f"  pytest")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new Python project"
    )
    parser.add_argument("name", help="Project name")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Base path for project (default: current directory)"
    )
    parser.add_argument(
        "--author",
        default="Your Name",
        help="Author name"
    )
    parser.add_argument(
        "--email",
        default="you@example.com",
        help="Author email"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Include CLI scaffolding with Typer"
    )

    args = parser.parse_args()
    scaffold_project(
        args.name,
        args.path,
        author=args.author,
        email=args.email,
        with_cli=args.cli,
    )


if __name__ == "__main__":
    main()
