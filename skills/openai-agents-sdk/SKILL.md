---
name: openai-agents-sdk
description: OpenAI Agents SDK for building multi-agent AI workflows. Use when users want to (1) create AI agents with tools and instructions, (2) build multi-agent systems with handoffs, (3) implement guardrails for safety, (4) add conversation memory/sessions, (5) trace and debug agent workflows, (6) orchestrate complex agentic pipelines. Triggers on mentions of "openai agents", "agents sdk", "multi-agent", "agent handoffs", "agentic workflows", or building AI agent systems.
---

# OpenAI Agents SDK

A lightweight, Python-first framework for building production-ready multi-agent AI workflows.

## When to Use This Skill

- Building AI agents with custom tools and instructions
- Creating multi-agent systems with intelligent handoffs
- Implementing conversation memory across agent runs
- Adding guardrails for input/output validation
- Tracing and debugging agent execution flows
- Orchestrating complex agentic pipelines

## Core Concepts

### 1. Agents

LLMs configured with instructions, tools, guardrails, and handoffs:

```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant specialized in coding.",
    model="gpt-4o",
    tools=[my_tool],
)
```

### 2. Tools

Function tools integrate external functionality:

```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city} is sunny, 72°F"

@function_tool
def search_database(query: str, limit: int = 10) -> list[dict]:
    """Search the database for matching records."""
    # Implementation here
    return results

agent = Agent(
    name="WeatherBot",
    instructions="Help users with weather queries.",
    tools=[get_weather, search_database],
)
```

### 3. Running Agents

```python
from agents import Agent, Runner

# Synchronous execution
result = Runner.run_sync(agent, "What's the weather in Tokyo?")
print(result.final_output)

# Asynchronous execution
result = await Runner.run(agent, "What's the weather in Tokyo?")
print(result.final_output)

# With streaming
async for event in Runner.run_streamed(agent, "Tell me about Python"):
    if event.type == "raw_response_event":
        print(event.data, end="", flush=True)
```

### 4. Handoffs (Multi-Agent)

Transfer control between specialized agents:

```python
from agents import Agent

# Specialist agents
sales_agent = Agent(
    name="SalesAgent",
    instructions="Handle sales inquiries and product questions.",
    tools=[get_products, create_quote],
)

support_agent = Agent(
    name="SupportAgent",
    instructions="Handle technical support and troubleshooting.",
    tools=[search_docs, create_ticket],
)

# Router agent with handoffs
router = Agent(
    name="Router",
    instructions="""Route customers to the appropriate agent:
    - Sales questions -> SalesAgent
    - Technical issues -> SupportAgent""",
    handoffs=[sales_agent, support_agent],
)

# Router automatically delegates
result = await Runner.run(router, "I need help with a bug")
```

### 5. Sessions (Memory)

Persist conversation history across runs:

```python
from agents import Agent, Runner, SQLiteSession

# Create session for persistent memory
session = SQLiteSession("user_123")

# First interaction
result = await Runner.run(
    agent,
    "My name is Alice and I work at Acme Corp",
    session=session
)

# Later interaction - agent remembers context
result = await Runner.run(
    agent,
    "What company do I work at?",  # Agent recalls "Acme Corp"
    session=session
)
```

**Session Backends:**
- `SQLiteSession` - Local file storage
- `RedisSession` - Distributed storage (requires `pip install openai-agents[redis]`)
- Custom implementations via `SessionBackend` base class

### 6. Guardrails

Input/output validation and safety:

```python
from agents import Agent, InputGuardrail, OutputGuardrail, GuardrailFunctionOutput

# Input guardrail - validate before processing
async def check_appropriate_content(input: str) -> GuardrailFunctionOutput:
    # Check for inappropriate content
    if contains_harmful_content(input):
        return GuardrailFunctionOutput(
            should_block=True,
            message="I can't help with that request."
        )
    return GuardrailFunctionOutput(should_block=False)

# Output guardrail - validate before returning
async def check_pii_leak(output: str) -> GuardrailFunctionOutput:
    if contains_pii(output):
        return GuardrailFunctionOutput(
            should_block=True,
            message="Response contained sensitive information."
        )
    return GuardrailFunctionOutput(should_block=False)

agent = Agent(
    name="SafeAssistant",
    instructions="You are a helpful assistant.",
    input_guardrails=[InputGuardrail(guardrail_function=check_appropriate_content)],
    output_guardrails=[OutputGuardrail(guardrail_function=check_pii_leak)],
)
```

### 7. Structured Output

Type-safe responses with Pydantic:

```python
from pydantic import BaseModel
from agents import Agent, Runner

class WeatherReport(BaseModel):
    city: str
    temperature: float
    conditions: str
    humidity: int

agent = Agent(
    name="WeatherReporter",
    instructions="Provide weather reports in structured format.",
    output_type=WeatherReport,
)

result = await Runner.run(agent, "Weather in San Francisco")
report: WeatherReport = result.final_output
print(f"{report.city}: {report.temperature}°F, {report.conditions}")
```

### 8. Tracing

Built-in observability for debugging:

```python
from agents import Agent, Runner, trace

# Traces are automatic - view in OpenAI dashboard
result = await Runner.run(agent, "Hello")

# Custom trace spans
with trace.span("custom_operation"):
    # Your code here
    result = await some_async_operation()

# External tracing (Logfire, AgentOps, etc.)
# Configure via environment or SDK settings
```

## Common Patterns

### Customer Support Bot

```python
from agents import Agent, function_tool, Runner

@function_tool
def search_knowledge_base(query: str) -> str:
    """Search support documentation."""
    # Implementation
    return "Found article: ..."

@function_tool
def create_support_ticket(
    subject: str,
    description: str,
    priority: str = "medium"
) -> dict:
    """Create a support ticket."""
    return {"ticket_id": "T-12345", "status": "created"}

support_agent = Agent(
    name="SupportBot",
    instructions="""You are a helpful support agent.
    1. First search the knowledge base for answers
    2. If you can't resolve, create a support ticket
    3. Always be polite and professional""",
    tools=[search_knowledge_base, create_support_ticket],
)
```

### Research Pipeline

```python
from agents import Agent

researcher = Agent(
    name="Researcher",
    instructions="Research topics thoroughly using web search.",
    tools=[web_search, fetch_url],
)

analyst = Agent(
    name="Analyst",
    instructions="Analyze research and extract key insights.",
    tools=[analyze_text, summarize],
)

writer = Agent(
    name="Writer",
    instructions="Write clear, well-structured reports.",
    handoffs=[researcher, analyst],  # Can delegate back
)

# Pipeline with handoffs
pipeline = Agent(
    name="ResearchPipeline",
    instructions="""Coordinate research projects:
    1. Researcher gathers information
    2. Analyst extracts insights
    3. Writer produces final report""",
    handoffs=[researcher, analyst, writer],
)
```

### Code Review Agent

```python
from agents import Agent, function_tool
from pydantic import BaseModel

class CodeReview(BaseModel):
    issues: list[str]
    suggestions: list[str]
    overall_quality: str  # "good", "needs_work", "critical"

@function_tool
def analyze_code(code: str, language: str) -> dict:
    """Analyze code for issues and patterns."""
    # Static analysis implementation
    return {"complexity": 5, "issues": [...]}

reviewer = Agent(
    name="CodeReviewer",
    instructions="""Review code for:
    - Bugs and potential issues
    - Performance concerns
    - Best practices
    - Security vulnerabilities""",
    tools=[analyze_code],
    output_type=CodeReview,
)
```

## Installation

```bash
# Basic installation
pip install openai-agents

# With voice support
pip install openai-agents[voice]

# With Redis sessions
pip install openai-agents[redis]

# All extras
pip install openai-agents[voice,redis]
```

## Environment Setup

```bash
# Required
export OPENAI_API_KEY="sk-..."

# Optional - for tracing
export OPENAI_AGENTS_TRACING_ENABLED=true
```

## Best Practices

1. **Single Responsibility**: Each agent should have one clear purpose
2. **Clear Instructions**: Write detailed, specific instructions
3. **Tool Design**: Keep tools focused and well-documented
4. **Error Handling**: Use guardrails for validation
5. **Session Management**: Use appropriate backend for your scale
6. **Tracing**: Enable tracing in development for debugging
7. **Structured Output**: Use Pydantic models for type safety

## References

- See `references/agents.md` for agent configuration details
- See `references/tools.md` for tool patterns and examples
- See `references/multi-agent.md` for orchestration patterns
- See `references/tracing.md` for observability setup

## Scripts

- `scripts/scaffold_agent.py` - Generate new agent boilerplate
- `scripts/add_tools.py` - Add tools to existing agent
- `scripts/setup_tracing.py` - Configure tracing backends

## Assets

- `assets/agent_template.py` - Basic agent template
- `assets/multi_agent_template.py` - Multi-agent system template
- `assets/tools_template.py` - Common tool patterns
