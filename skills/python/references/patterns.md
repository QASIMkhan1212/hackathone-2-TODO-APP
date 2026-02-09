# Python Design Patterns

## Creational Patterns

### Factory Pattern

```python
from abc import ABC, abstractmethod
from typing import Type

class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass

class EmailNotification(Notification):
    def send(self, message: str) -> None:
        print(f"Email: {message}")

class SMSNotification(Notification):
    def send(self, message: str) -> None:
        print(f"SMS: {message}")

class NotificationFactory:
    _notifications: dict[str, Type[Notification]] = {
        "email": EmailNotification,
        "sms": SMSNotification,
    }

    @classmethod
    def create(cls, notification_type: str) -> Notification:
        if notification_type not in cls._notifications:
            raise ValueError(f"Unknown type: {notification_type}")
        return cls._notifications[notification_type]()

# Usage
notification = NotificationFactory.create("email")
notification.send("Hello!")
```

### Singleton Pattern

```python
from typing import Self

class Database:
    _instance: Self | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        self.connection = "Connected"

# Better: Module-level singleton
# database.py
_db: Database | None = None

def get_database() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
```

### Builder Pattern

```python
from dataclasses import dataclass, field
from typing import Self

@dataclass
class Query:
    table: str = ""
    columns: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    limit: int | None = None

class QueryBuilder:
    def __init__(self) -> None:
        self._query = Query()

    def select(self, *columns: str) -> Self:
        self._query.columns = list(columns)
        return self

    def from_table(self, table: str) -> Self:
        self._query.table = table
        return self

    def where(self, condition: str) -> Self:
        self._query.conditions.append(condition)
        return self

    def limit(self, n: int) -> Self:
        self._query.limit = n
        return self

    def build(self) -> str:
        cols = ", ".join(self._query.columns) or "*"
        sql = f"SELECT {cols} FROM {self._query.table}"
        if self._query.conditions:
            sql += " WHERE " + " AND ".join(self._query.conditions)
        if self._query.limit:
            sql += f" LIMIT {self._query.limit}"
        return sql

# Usage
query = (
    QueryBuilder()
    .select("id", "name")
    .from_table("users")
    .where("active = true")
    .limit(10)
    .build()
)
```

---

## Structural Patterns

### Repository Pattern

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from dataclasses import dataclass

T = TypeVar("T")

@dataclass
class User:
    id: str
    name: str
    email: str

class Repository(ABC, Generic[T]):
    @abstractmethod
    def get(self, id: str) -> T | None:
        pass

    @abstractmethod
    def get_all(self) -> list[T]:
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        pass

class UserRepository(Repository[User]):
    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def get(self, id: str) -> User | None:
        return self._users.get(id)

    def get_all(self) -> list[User]:
        return list(self._users.values())

    def create(self, entity: User) -> User:
        self._users[entity.id] = entity
        return entity

    def update(self, entity: User) -> User:
        self._users[entity.id] = entity
        return entity

    def delete(self, id: str) -> bool:
        if id in self._users:
            del self._users[id]
            return True
        return False
```

### Dependency Injection

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

# Using Protocol for duck typing
class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> bool:
        ...

class SMTPEmailSender:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def send(self, to: str, subject: str, body: str) -> bool:
        print(f"Sending to {to}: {subject}")
        return True

class MockEmailSender:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []

    def send(self, to: str, subject: str, body: str) -> bool:
        self.sent.append((to, subject, body))
        return True

@dataclass
class UserService:
    email_sender: EmailSender

    def welcome_user(self, email: str, name: str) -> bool:
        return self.email_sender.send(
            to=email,
            subject="Welcome!",
            body=f"Hello {name}, welcome to our service!",
        )

# Production
service = UserService(email_sender=SMTPEmailSender("smtp.example.com", 587))

# Testing
mock_sender = MockEmailSender()
test_service = UserService(email_sender=mock_sender)
```

### Decorator Pattern

```python
from functools import wraps
from typing import Callable, TypeVar, ParamSpec
import time

P = ParamSpec("P")
R = TypeVar("R")

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay * (2 ** attempt))
            raise last_exception  # type: ignore
        return wrapper
    return decorator

def cache(func: Callable[P, R]) -> Callable[P, R]:
    """Simple cache decorator."""
    _cache: dict[tuple, R] = {}

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        key = (args, tuple(sorted(kwargs.items())))
        if key not in _cache:
            _cache[key] = func(*args, **kwargs)
        return _cache[key]
    return wrapper

# Usage
@retry(max_attempts=3, delay=0.5)
@cache
def fetch_data(url: str) -> dict:
    # Expensive operation
    return {"data": "value"}
```

---

## Behavioral Patterns

### Strategy Pattern

```python
from abc import ABC, abstractmethod
from typing import Protocol

class PaymentStrategy(Protocol):
    def pay(self, amount: float) -> bool:
        ...

class CreditCardPayment:
    def __init__(self, card_number: str) -> None:
        self.card_number = card_number

    def pay(self, amount: float) -> bool:
        print(f"Paid ${amount} with card {self.card_number[-4:]}")
        return True

class PayPalPayment:
    def __init__(self, email: str) -> None:
        self.email = email

    def pay(self, amount: float) -> bool:
        print(f"Paid ${amount} via PayPal ({self.email})")
        return True

class ShoppingCart:
    def __init__(self) -> None:
        self.items: list[tuple[str, float]] = []

    def add(self, item: str, price: float) -> None:
        self.items.append((item, price))

    def checkout(self, payment: PaymentStrategy) -> bool:
        total = sum(price for _, price in self.items)
        return payment.pay(total)

# Usage
cart = ShoppingCart()
cart.add("Book", 29.99)
cart.checkout(CreditCardPayment("4111111111111111"))
cart.checkout(PayPalPayment("user@example.com"))
```

### Observer Pattern

```python
from abc import ABC, abstractmethod
from typing import Callable
from dataclasses import dataclass, field

@dataclass
class Event:
    name: str
    data: dict

class EventEmitter:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[[Event], None]]] = {}

    def on(self, event_name: str, callback: Callable[[Event], None]) -> None:
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    def off(self, event_name: str, callback: Callable[[Event], None]) -> None:
        if event_name in self._listeners:
            self._listeners[event_name].remove(callback)

    def emit(self, event: Event) -> None:
        for callback in self._listeners.get(event.name, []):
            callback(event)

# Usage
emitter = EventEmitter()

def on_user_created(event: Event) -> None:
    print(f"User created: {event.data['name']}")

emitter.on("user_created", on_user_created)
emitter.emit(Event("user_created", {"name": "John"}))
```

### Context Manager Pattern

```python
from contextlib import contextmanager
from typing import Generator
import time

class DatabaseConnection:
    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string
        self.connected = False

    def __enter__(self) -> "DatabaseConnection":
        self.connected = True
        print("Connected to database")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.connected = False
        print("Disconnected from database")
        return False  # Don't suppress exceptions

    def query(self, sql: str) -> list:
        if not self.connected:
            raise RuntimeError("Not connected")
        return []

# Using contextmanager decorator
@contextmanager
def timer(name: str) -> Generator[None, None, None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{name}: {elapsed:.4f}s")

# Usage
with DatabaseConnection("postgresql://localhost/db") as db:
    results = db.query("SELECT * FROM users")

with timer("data processing"):
    # Do work
    time.sleep(0.1)
```

---

## Async Patterns

### Async Context Manager

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiohttp

@asynccontextmanager
async def http_client() -> AsyncGenerator[aiohttp.ClientSession, None]:
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()

async def fetch_all(urls: list[str]) -> list[dict]:
    async with http_client() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]
```

### Async Iterator

```python
from typing import AsyncIterator

class AsyncPaginator:
    def __init__(self, url: str, page_size: int = 10) -> None:
        self.url = url
        self.page_size = page_size
        self.page = 0

    def __aiter__(self) -> AsyncIterator[list[dict]]:
        return self

    async def __anext__(self) -> list[dict]:
        data = await self._fetch_page(self.page)
        if not data:
            raise StopAsyncIteration
        self.page += 1
        return data

    async def _fetch_page(self, page: int) -> list[dict]:
        # Fetch implementation
        return []

# Usage
async def process_all():
    async for page in AsyncPaginator("https://api.example.com/items"):
        for item in page:
            print(item)
```
