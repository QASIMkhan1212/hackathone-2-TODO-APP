#!/usr/bin/env python3
"""Set up pytest testing infrastructure for a Python project."""

import argparse
from pathlib import Path


def find_package_name(project_path: Path) -> str | None:
    """Find the main package name."""
    src_path = project_path / "src"
    if src_path.exists():
        for item in src_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                return item.name

    for item in project_path.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            if item.name not in ["tests", "docs", ".venv", "venv"]:
                return item.name

    return None


def setup_testing(
    project_path: Path,
    with_async: bool = False,
    with_mock: bool = True,
    coverage_threshold: int = 80,
) -> None:
    """Set up pytest testing infrastructure."""

    package_name = find_package_name(project_path)
    if not package_name:
        print("Warning: Could not detect package name, using 'src'")
        package_name = "src"

    print(f"Setting up testing for: {package_name}")
    print("=" * 50)

    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)

    # Create conftest.py
    conftest_imports = ["import pytest"]
    if with_async:
        conftest_imports.append("import asyncio")

    conftest_content = f'''{chr(10).join(conftest_imports)}
from pathlib import Path


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def sample_data() -> dict:
    """Sample test data."""
    return {{
        "id": "test-123",
        "name": "Test Item",
        "value": 42,
    }}


@pytest.fixture
def sample_list() -> list[dict]:
    """Sample list of test data."""
    return [
        {{"id": "1", "name": "Item 1"}},
        {{"id": "2", "name": "Item 2"}},
        {{"id": "3", "name": "Item 3"}},
    ]

'''

    if with_async:
        conftest_content += '''
# =============================================================================
# Async Fixtures
# =============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    """Async HTTP client fixture."""
    import httpx
    async with httpx.AsyncClient() as client:
        yield client

'''

    if with_mock:
        conftest_content += '''
# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    def _mock_env(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
    return _mock_env


@pytest.fixture
def mock_datetime(mocker):
    """Mock datetime.now()."""
    from datetime import datetime
    mock = mocker.patch("datetime.datetime")
    mock.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
    return mock

'''

    conftest_file = tests_dir / "conftest.py"
    conftest_file.write_text(conftest_content, encoding="utf-8")
    print(f"  Created: {conftest_file}")

    # Create __init__.py
    init_file = tests_dir / "__init__.py"
    init_file.write_text('"""Test suite."""\n', encoding="utf-8")
    print(f"  Created: {init_file}")

    # Create example test file
    test_example_content = f'''"""Example tests demonstrating pytest features."""

import pytest


class TestBasicAssertions:
    """Basic assertion examples."""

    def test_equality(self):
        assert 1 + 1 == 2

    def test_string_contains(self):
        assert "hello" in "hello world"

    def test_list_membership(self):
        items = [1, 2, 3]
        assert 2 in items

    def test_dict_key_exists(self):
        data = {{"key": "value"}}
        assert "key" in data


class TestFixtures:
    """Fixture usage examples."""

    def test_with_sample_data(self, sample_data):
        assert sample_data["id"] == "test-123"
        assert "name" in sample_data

    def test_with_temp_dir(self, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("hello")
        assert test_file.exists()
        assert test_file.read_text() == "hello"


class TestParameterized:
    """Parameterized test examples."""

    @pytest.mark.parametrize("input,expected", [
        ("hello", "HELLO"),
        ("world", "WORLD"),
        ("Python", "PYTHON"),
    ])
    def test_uppercase(self, input, expected):
        assert input.upper() == expected

    @pytest.mark.parametrize("a,b,expected", [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
        (100, 200, 300),
    ])
    def test_addition(self, a, b, expected):
        assert a + b == expected


class TestExceptions:
    """Exception testing examples."""

    def test_raises_value_error(self):
        with pytest.raises(ValueError):
            int("not a number")

    def test_raises_with_message(self):
        with pytest.raises(ValueError, match="invalid literal"):
            int("not a number")

    def test_raises_key_error(self):
        data = {{"a": 1}}
        with pytest.raises(KeyError):
            _ = data["b"]


class TestMarkers:
    """Test marker examples."""

    @pytest.mark.skip(reason="Demonstrating skip")
    def test_skipped(self):
        pass

    @pytest.mark.skipif(True, reason="Conditional skip")
    def test_conditional_skip(self):
        pass

    @pytest.mark.xfail(reason="Expected to fail")
    def test_expected_failure(self):
        assert False

'''

    if with_async:
        test_example_content += '''

class TestAsync:
    """Async test examples."""

    @pytest.mark.asyncio
    async def test_async_function(self):
        async def async_add(a, b):
            return a + b

        result = await async_add(1, 2)
        assert result == 3

    @pytest.mark.asyncio
    async def test_async_with_sleep(self):
        import asyncio
        await asyncio.sleep(0.01)
        assert True

'''

    test_file = tests_dir / "test_examples.py"
    test_file.write_text(test_example_content, encoding="utf-8")
    print(f"  Created: {test_file}")

    # Generate pytest configuration
    pytest_config = f'''
# Add/update in pyproject.toml:

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]
addopts = "-v --cov=src --cov-report=term-missing --cov-fail-under={coverage_threshold}"
'''

    if with_async:
        pytest_config += 'asyncio_mode = "auto"\n'

    pytest_config += f'''markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
    "unit: marks unit tests",
]

[tool.coverage.run]
source = ["src"]
branch = true
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
fail_under = {coverage_threshold}
show_missing = true
'''

    # Print dependencies
    deps = ["pytest>=7.0", "pytest-cov>=4.0"]
    if with_async:
        deps.append("pytest-asyncio>=0.23")
    if with_mock:
        deps.append("pytest-mock>=3.0")

    print("\n" + "=" * 50)
    print("Testing setup complete!")
    print(f"\nAdd to pyproject.toml [project.optional-dependencies]:")
    print("-" * 30)
    print(f"dev = [")
    for dep in deps:
        print(f'    "{dep}",')
    print("]")
    print("\n" + pytest_config)
    print("\nRun tests with:")
    print("  pytest")
    print("  pytest -v")
    print("  pytest --cov=src --cov-report=html")
    print('  pytest -m "not slow"')


def main():
    parser = argparse.ArgumentParser(
        description="Set up pytest testing infrastructure"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Project path (default: current directory)"
    )
    parser.add_argument(
        "--async",
        dest="with_async",
        action="store_true",
        help="Include async testing support"
    )
    parser.add_argument(
        "--no-mock",
        dest="with_mock",
        action="store_false",
        help="Skip mock fixtures"
    )
    parser.add_argument(
        "--coverage",
        type=int,
        default=80,
        help="Coverage threshold (default: 80)"
    )

    args = parser.parse_args()
    setup_testing(
        args.path,
        with_async=args.with_async,
        with_mock=args.with_mock,
        coverage_threshold=args.coverage,
    )


if __name__ == "__main__":
    main()
