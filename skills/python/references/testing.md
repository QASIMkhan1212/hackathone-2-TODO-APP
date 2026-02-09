# Python Testing with Pytest

## Setup

### Installation

```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock
```

### Configuration (pyproject.toml)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=term-missing --cov-report=html"
asyncio_mode = "auto"
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
]
```

---

## Basic Tests

### Simple Assertions

```python
# tests/test_basic.py

def test_addition():
    assert 1 + 1 == 2

def test_string_operations():
    name = "Python"
    assert name.lower() == "python"
    assert name.startswith("Py")
    assert len(name) == 6

def test_list_operations():
    items = [1, 2, 3]
    assert 2 in items
    assert len(items) == 3
    assert items[0] == 1

def test_dict_operations():
    data = {"name": "John", "age": 30}
    assert data["name"] == "John"
    assert "age" in data
    assert data.get("missing") is None
```

### Testing Exceptions

```python
import pytest
from my_project.errors import ValidationError, NotFoundError

def test_raises_validation_error():
    with pytest.raises(ValidationError):
        validate_email("invalid-email")

def test_raises_with_message():
    with pytest.raises(ValidationError, match="Invalid email format"):
        validate_email("invalid")

def test_raises_not_found():
    with pytest.raises(NotFoundError) as exc_info:
        get_user("nonexistent")

    assert exc_info.value.resource == "User"
    assert "nonexistent" in str(exc_info.value)
```

---

## Fixtures

### Basic Fixtures

```python
# tests/conftest.py
import pytest
from my_project.database import Database
from my_project.models import User

@pytest.fixture
def db():
    """Create test database."""
    database = Database(":memory:")
    database.create_tables()
    yield database
    database.close()

@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        "id": "user-123",
        "name": "Test User",
        "email": "test@example.com",
    }

@pytest.fixture
def created_user(db, sample_user):
    """Create and return a user in the database."""
    user = User(**sample_user)
    db.save(user)
    return user
```

### Fixture Scopes

```python
@pytest.fixture(scope="session")
def expensive_resource():
    """Created once per test session."""
    resource = create_expensive_resource()
    yield resource
    resource.cleanup()

@pytest.fixture(scope="module")
def module_db():
    """Created once per test module."""
    return Database()

@pytest.fixture(scope="function")  # Default
def fresh_db():
    """Created for each test function."""
    return Database()
```

### Parameterized Fixtures

```python
@pytest.fixture(params=["sqlite", "postgres", "mysql"])
def database(request):
    """Test with multiple database backends."""
    db_type = request.param
    db = create_database(db_type)
    yield db
    db.close()

def test_insert(database):
    # This test runs 3 times, once for each db type
    database.insert({"id": 1, "name": "test"})
    assert database.count() == 1
```

---

## Parameterized Tests

### Basic Parameterization

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("Python", "PYTHON"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_addition(a, b, expected):
    assert a + b == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", [10, 20])
def test_multiply(x, y):
    # Runs 6 times: (1,10), (1,20), (2,10), (2,20), (3,10), (3,20)
    assert x * y == x * y
```

### IDs for Clarity

```python
@pytest.mark.parametrize(
    "email,valid",
    [
        ("user@example.com", True),
        ("invalid", False),
        ("", False),
        ("user@domain", False),
    ],
    ids=["valid_email", "no_at", "empty", "no_tld"],
)
def test_email_validation(email, valid):
    assert is_valid_email(email) == valid
```

---

## Mocking

### Using pytest-mock

```python
def test_with_mock(mocker):
    # Mock a function
    mock_fetch = mocker.patch("my_project.api.fetch_data")
    mock_fetch.return_value = {"data": "mocked"}

    result = process_data()

    mock_fetch.assert_called_once()
    assert result["data"] == "mocked"

def test_mock_method(mocker):
    # Mock a method
    mock_send = mocker.patch.object(EmailService, "send")
    mock_send.return_value = True

    service = EmailService()
    result = service.send("test@example.com", "Hello")

    mock_send.assert_called_with("test@example.com", "Hello")
    assert result is True
```

### Mock Side Effects

```python
def test_mock_side_effect(mocker):
    # Raise exception
    mock_api = mocker.patch("my_project.api.call")
    mock_api.side_effect = ConnectionError("Network error")

    with pytest.raises(ConnectionError):
        make_api_call()

def test_mock_multiple_returns(mocker):
    # Return different values on each call
    mock_read = mocker.patch("my_project.file.read")
    mock_read.side_effect = ["first", "second", "third"]

    assert read_file() == "first"
    assert read_file() == "second"
    assert read_file() == "third"
```

### Spy (Track Calls Without Replacing)

```python
def test_spy(mocker):
    spy = mocker.spy(UserService, "create")

    service = UserService()
    service.create({"name": "John"})

    spy.assert_called_once()
    # Original method still executed
```

---

## Async Tests

### Testing Async Functions

```python
import pytest

@pytest.mark.asyncio
async def test_async_fetch():
    result = await fetch_data("https://api.example.com")
    assert "data" in result

@pytest.mark.asyncio
async def test_async_with_mock(mocker):
    mock_fetch = mocker.patch("my_project.api.async_fetch")
    mock_fetch.return_value = {"status": "ok"}

    result = await process_async()
    assert result["status"] == "ok"
```

### Async Fixtures

```python
@pytest.fixture
async def async_db():
    db = await Database.connect("test://")
    yield db
    await db.close()

@pytest.mark.asyncio
async def test_with_async_fixture(async_db):
    await async_db.insert({"id": 1})
    result = await async_db.get(1)
    assert result["id"] == 1
```

---

## Test Organization

### Markers

```python
# Mark slow tests
@pytest.mark.slow
def test_large_dataset():
    # Long running test
    pass

# Mark integration tests
@pytest.mark.integration
def test_database_integration():
    pass

# Skip tests
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_feature():
    pass

# Expected failures
@pytest.mark.xfail(reason="Known bug #123")
def test_known_issue():
    pass
```

### Running Specific Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_user.py

# Run specific test
pytest tests/test_user.py::test_create_user

# Run by marker
pytest -m "not slow"
pytest -m integration

# Run by keyword
pytest -k "user and not delete"

# Stop on first failure
pytest -x

# Run last failed
pytest --lf
```

---

## Coverage

### Configuration

```toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
fail_under = 80
```

### Commands

```bash
# Run with coverage
pytest --cov=src

# Generate HTML report
pytest --cov=src --cov-report=html

# Show missing lines
pytest --cov=src --cov-report=term-missing
```

---

## Best Practices

### Test Structure (AAA Pattern)

```python
def test_user_creation():
    # Arrange
    user_data = {"name": "John", "email": "john@example.com"}
    service = UserService()

    # Act
    user = service.create(user_data)

    # Assert
    assert user.id is not None
    assert user.name == "John"
    assert user.email == "john@example.com"
```

### Test Naming

```python
# Good: Descriptive names
def test_create_user_with_valid_data_returns_user():
    pass

def test_create_user_with_invalid_email_raises_validation_error():
    pass

def test_get_user_by_id_when_not_found_raises_not_found_error():
    pass

# Avoid: Generic names
def test_user():  # Bad
    pass
```
