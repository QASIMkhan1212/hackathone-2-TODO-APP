# Tools Reference

## Function Tools

The simplest way to add tools to agents:

```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city.

    Args:
        city: The city name to get weather for

    Returns:
        Weather description string
    """
    # Implementation
    return f"Sunny, 72°F in {city}"

@function_tool
def calculate(expression: str) -> float:
    """Safely evaluate a mathematical expression.

    Args:
        expression: Math expression like "2 + 2 * 3"

    Returns:
        The calculated result
    """
    # Safe evaluation
    return eval(expression, {"__builtins__": {}}, {})
```

## Tool with Complex Types

```python
from agents import function_tool
from pydantic import BaseModel
from typing import Optional

class SearchFilters(BaseModel):
    category: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: bool = True

class SearchResult(BaseModel):
    id: str
    name: str
    price: float
    category: str

@function_tool
def search_products(
    query: str,
    filters: SearchFilters,
    limit: int = 10
) -> list[SearchResult]:
    """Search products with filters.

    Args:
        query: Search query string
        filters: Search filters to apply
        limit: Maximum results to return

    Returns:
        List of matching products
    """
    # Implementation
    results = database.search(query, filters, limit)
    return [SearchResult(**r) for r in results]
```

## Async Tools

```python
from agents import function_tool
import httpx

@function_tool
async def fetch_url(url: str) -> str:
    """Fetch content from a URL.

    Args:
        url: The URL to fetch

    Returns:
        The page content as text
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

@function_tool
async def query_database(sql: str) -> list[dict]:
    """Execute a read-only SQL query.

    Args:
        sql: The SQL query to execute

    Returns:
        Query results as list of dicts
    """
    async with db_pool.acquire() as conn:
        results = await conn.fetch(sql)
        return [dict(r) for r in results]
```

## Tool with Context Access

```python
from agents import function_tool, RunContext

@function_tool
def get_user_data(field: str, context: RunContext) -> str:
    """Get data about the current user.

    Args:
        field: The field to retrieve (name, email, etc.)

    Returns:
        The requested user data
    """
    user_id = context.context.get("user_id")
    user = database.get_user(user_id)
    return getattr(user, field, "Unknown")

# Usage with context
result = await Runner.run(
    agent,
    "What's my email?",
    context={"user_id": "user_123"}
)
```

## Custom Tool Class

For more control, create a custom tool class:

```python
from agents import Tool, ToolResult
from pydantic import BaseModel

class FileReadToolInput(BaseModel):
    path: str
    encoding: str = "utf-8"

class FileReadTool(Tool):
    name = "read_file"
    description = "Read contents of a file"
    input_schema = FileReadToolInput

    async def run(self, input: FileReadToolInput) -> ToolResult:
        try:
            with open(input.path, encoding=input.encoding) as f:
                content = f.read()
            return ToolResult(output=content)
        except Exception as e:
            return ToolResult(error=str(e))

# Add to agent
agent = Agent(
    name="FileAgent",
    tools=[FileReadTool()],
)
```

## Tool Error Handling

```python
from agents import function_tool, ToolError

@function_tool
def divide(a: float, b: float) -> float:
    """Divide two numbers.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        Result of division
    """
    if b == 0:
        raise ToolError("Cannot divide by zero")
    return a / b

@function_tool
def fetch_data(id: str) -> dict:
    """Fetch data by ID.

    Args:
        id: The record ID

    Returns:
        The record data
    """
    data = database.get(id)
    if data is None:
        raise ToolError(f"Record {id} not found")
    return data
```

## Built-in Tools

OpenAI provides some built-in tools:

```python
from agents import Agent
from agents.tools import WebSearchTool, CodeInterpreterTool

agent = Agent(
    name="ResearchAgent",
    instructions="Research topics using web search.",
    tools=[
        WebSearchTool(),        # Web search capability
        CodeInterpreterTool(),  # Code execution
    ],
)
```

## Tool Best Practices

1. **Clear Docstrings**: LLM uses docstrings to understand tool usage
2. **Type Hints**: Always include type hints for parameters
3. **Focused Purpose**: One tool = one clear action
4. **Error Messages**: Return helpful error messages
5. **Async When Needed**: Use async for I/O operations
6. **Validation**: Validate inputs before processing

```python
@function_tool
def good_tool(
    required_param: str,
    optional_param: int = 10,
    flag: bool = False
) -> dict:
    """Clear description of what this tool does.

    Use this tool when you need to accomplish X.
    The tool will return Y based on the inputs.

    Args:
        required_param: What this parameter is for
        optional_param: Description with default behavior
        flag: When to set this to True

    Returns:
        Dictionary containing the results with keys:
        - result: The main output
        - metadata: Additional information
    """
    # Validate
    if not required_param:
        raise ToolError("required_param cannot be empty")

    # Process
    result = process(required_param, optional_param, flag)

    return {"result": result, "metadata": {...}}
```
