#!/usr/bin/env python3
"""Add CLI scaffolding to an existing Python project."""

import argparse
from pathlib import Path


def find_package_dir(project_path: Path) -> Path | None:
    """Find the main package directory."""
    src_path = project_path / "src"
    if src_path.exists():
        for item in src_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                return item

    # Check flat layout
    for item in project_path.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            if item.name not in ["tests", "docs", ".venv", "venv"]:
                return item

    return None


def add_cli(project_path: Path, framework: str = "typer") -> None:
    """Add CLI scaffolding to existing project."""

    package_dir = find_package_dir(project_path)
    if not package_dir:
        print("Error: Could not find package directory")
        return

    package_name = package_dir.name
    print(f"Adding CLI to package: {package_name}")
    print("=" * 50)

    if framework == "typer":
        cli_content = f'''"""CLI interface for {package_name}."""

import typer
from typing import Annotated

app = typer.Typer(
    name="{package_name}",
    help="{package_name} command-line interface",
    add_completion=False,
)


@app.command()
def hello(
    name: Annotated[str, typer.Argument(help="Name to greet")] = "World",
    count: Annotated[int, typer.Option("--count", "-c", help="Number of greetings")] = 1,
    formal: Annotated[bool, typer.Option("--formal", "-f", help="Use formal greeting")] = False,
) -> None:
    """Say hello to NAME."""
    greeting = "Good day" if formal else "Hello"
    for _ in range(count):
        typer.echo(f"{{greeting}}, {{name}}!")


@app.command()
def goodbye(
    name: Annotated[str, typer.Argument(help="Name to bid farewell")],
) -> None:
    """Say goodbye to NAME."""
    typer.echo(f"Goodbye, {{name}}!")


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__
    typer.echo(f"{package_name} v{{__version__}}")


# Group example
config_app = typer.Typer(help="Configuration commands")
app.add_typer(config_app, name="config")


@config_app.command("show")
def config_show() -> None:
    """Show current configuration."""
    typer.echo("Configuration:")
    typer.echo("  debug: false")
    typer.echo("  log_level: INFO")


@config_app.command("set")
def config_set(
    key: Annotated[str, typer.Argument(help="Configuration key")],
    value: Annotated[str, typer.Argument(help="Configuration value")],
) -> None:
    """Set a configuration value."""
    typer.echo(f"Setting {{key}} = {{value}}")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
'''
    else:  # click
        cli_content = f'''"""CLI interface for {package_name}."""

import click


@click.group()
@click.version_option()
def cli() -> None:
    """{package_name} command-line interface."""
    pass


@cli.command()
@click.argument("name", default="World")
@click.option("--count", "-c", default=1, help="Number of greetings")
@click.option("--formal", "-f", is_flag=True, help="Use formal greeting")
def hello(name: str, count: int, formal: bool) -> None:
    """Say hello to NAME."""
    greeting = "Good day" if formal else "Hello"
    for _ in range(count):
        click.echo(f"{{greeting}}, {{name}}!")


@cli.command()
@click.argument("name")
def goodbye(name: str) -> None:
    """Say goodbye to NAME."""
    click.echo(f"Goodbye, {{name}}!")


@cli.group()
def config() -> None:
    """Configuration commands."""
    pass


@config.command("show")
def config_show() -> None:
    """Show current configuration."""
    click.echo("Configuration:")
    click.echo("  debug: false")
    click.echo("  log_level: INFO")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str) -> None:
    """Set a configuration value."""
    click.echo(f"Setting {{key}} = {{value}}")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
'''

    cli_file = package_dir / "cli.py"
    cli_file.write_text(cli_content, encoding="utf-8")
    print(f"  Created: {cli_file}")

    # Create test file
    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)

    if framework == "typer":
        test_content = f'''"""Tests for CLI."""

from typer.testing import CliRunner
from {package_name}.cli import app

runner = CliRunner()


def test_hello():
    """Test hello command."""
    result = runner.invoke(app, ["hello", "Test"])
    assert result.exit_code == 0
    assert "Hello, Test!" in result.output


def test_hello_formal():
    """Test hello command with formal flag."""
    result = runner.invoke(app, ["hello", "Test", "--formal"])
    assert result.exit_code == 0
    assert "Good day, Test!" in result.output


def test_hello_count():
    """Test hello command with count."""
    result = runner.invoke(app, ["hello", "Test", "--count", "3"])
    assert result.exit_code == 0
    assert result.output.count("Hello, Test!") == 3


def test_goodbye():
    """Test goodbye command."""
    result = runner.invoke(app, ["goodbye", "Test"])
    assert result.exit_code == 0
    assert "Goodbye, Test!" in result.output


def test_version():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0


def test_config_show():
    """Test config show command."""
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "Configuration:" in result.output
'''
    else:
        test_content = f'''"""Tests for CLI."""

from click.testing import CliRunner
from {package_name}.cli import cli

runner = CliRunner()


def test_hello():
    """Test hello command."""
    result = runner.invoke(cli, ["hello", "Test"])
    assert result.exit_code == 0
    assert "Hello, Test!" in result.output


def test_hello_formal():
    """Test hello command with formal flag."""
    result = runner.invoke(cli, ["hello", "Test", "--formal"])
    assert result.exit_code == 0
    assert "Good day, Test!" in result.output


def test_goodbye():
    """Test goodbye command."""
    result = runner.invoke(cli, ["goodbye", "Test"])
    assert result.exit_code == 0
    assert "Goodbye, Test!" in result.output
'''

    test_file = tests_dir / "test_cli.py"
    test_file.write_text(test_content, encoding="utf-8")
    print(f"  Created: {test_file}")

    print("\n" + "=" * 50)
    print("CLI scaffolding added!")
    print("\nAdd to pyproject.toml:")
    print("-" * 30)

    if framework == "typer":
        print(f'''
# In [project.scripts]
{package_name} = "{package_name}.cli:app"

# In dependencies
"typer>=0.9",
''')
    else:
        print(f'''
# In [project.scripts]
{package_name} = "{package_name}.cli:cli"

# In dependencies
"click>=8.0",
''')

    print("\nTest with:")
    print(f"  pip install -e .")
    print(f"  {package_name} --help")


def main():
    parser = argparse.ArgumentParser(
        description="Add CLI scaffolding to Python project"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Project path (default: current directory)"
    )
    parser.add_argument(
        "--framework",
        choices=["typer", "click"],
        default="typer",
        help="CLI framework (default: typer)"
    )

    args = parser.parse_args()
    add_cli(args.path, args.framework)


if __name__ == "__main__":
    main()
