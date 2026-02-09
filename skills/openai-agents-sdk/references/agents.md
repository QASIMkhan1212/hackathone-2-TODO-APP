# Agent Configuration Reference

## Agent Class

```python
from agents import Agent

agent = Agent(
    # Required
    name: str,                          # Agent identifier

    # Optional - Core
    instructions: str | Callable,       # System prompt or dynamic function
    model: str = "gpt-4o",             # Model to use

    # Optional - Tools & Handoffs
    tools: list[Tool] = [],            # Available tools
    handoffs: list[Agent] = [],        # Agents to hand off to

    # Optional - Output
    output_type: Type[BaseModel],      # Structured output schema

    # Optional - Safety
    input_guardrails: list[InputGuardrail] = [],
    output_guardrails: list[OutputGuardrail] = [],

    # Optional - Advanced
    model_settings: ModelSettings,      # Temperature, max_tokens, etc.
    tool_use_behavior: ToolUseBehavior, # How tools are selected
)
```

## Dynamic Instructions

```python
def get_instructions(context: RunContext) -> str:
    """Generate instructions based on context."""
    user_tier = context.context.get("user_tier", "free")
    return f"""You are an assistant for {user_tier} users.
    {"Provide premium features." if user_tier == "premium" else ""}
    """

agent = Agent(
    name="DynamicAgent",
    instructions=get_instructions,
)

# Pass context at runtime
result = await Runner.run(
    agent,
    "Help me",
    context={"user_tier": "premium"}
)
```

## Model Settings

```python
from agents import Agent, ModelSettings

agent = Agent(
    name="CreativeWriter",
    instructions="Write creative stories.",
    model_settings=ModelSettings(
        temperature=0.9,      # Higher for creativity
        max_tokens=4096,      # Response length limit
        top_p=0.95,          # Nucleus sampling
        frequency_penalty=0.5,
        presence_penalty=0.5,
    ),
)
```

## Agent with All Features

```python
from agents import (
    Agent,
    function_tool,
    InputGuardrail,
    OutputGuardrail,
    GuardrailFunctionOutput,
    ModelSettings,
)
from pydantic import BaseModel

# Output schema
class TaskResult(BaseModel):
    status: str
    message: str
    data: dict | None = None

# Tools
@function_tool
def process_task(task_id: str) -> dict:
    """Process a task by ID."""
    return {"processed": True}

# Guardrails
async def validate_input(input: str) -> GuardrailFunctionOutput:
    if len(input) > 10000:
        return GuardrailFunctionOutput(
            should_block=True,
            message="Input too long"
        )
    return GuardrailFunctionOutput(should_block=False)

# Specialist for handoffs
specialist = Agent(
    name="Specialist",
    instructions="Handle specialized queries.",
)

# Full-featured agent
agent = Agent(
    name="MainAgent",
    instructions="""You are the main coordinator.
    - Process tasks using the process_task tool
    - Hand off complex queries to Specialist""",
    model="gpt-4o",
    tools=[process_task],
    handoffs=[specialist],
    output_type=TaskResult,
    input_guardrails=[InputGuardrail(guardrail_function=validate_input)],
    model_settings=ModelSettings(temperature=0.3),
)
```

## Clone and Modify

```python
# Create base agent
base_agent = Agent(
    name="BaseAssistant",
    instructions="You are a helpful assistant.",
    tools=[common_tool],
)

# Clone with modifications
specialized = base_agent.clone(
    name="SpecializedAssistant",
    instructions="You are a specialized assistant for finance.",
    tools=[common_tool, finance_tool],  # Add more tools
)
```

## Agent Loop Behavior

The agent loop runs until:
1. Agent returns final output (no tool calls)
2. Agent hands off to another agent
3. `max_turns` limit is reached
4. Guardrail blocks the response

```python
result = await Runner.run(
    agent,
    "Complex multi-step task",
    max_turns=10,  # Limit iterations
)

# Check how many turns were used
print(f"Completed in {len(result.raw_responses)} turns")
```
