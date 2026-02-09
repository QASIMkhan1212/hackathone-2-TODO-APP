#!/usr/bin/env python3
"""Scaffold a new OpenAI Agents SDK agent."""

import argparse
from pathlib import Path


def generate_basic_agent(name: str, description: str) -> str:
    """Generate a basic single agent."""
    return f'''"""Agent: {name}

{description}
"""

from agents import Agent, Runner, function_tool


# =============================================================================
# Tools
# =============================================================================


@function_tool
def example_tool(query: str) -> str:
    """Example tool - replace with your implementation.

    Args:
        query: The input query to process

    Returns:
        Processed result
    """
    return f"Processed: {{query}}"


# =============================================================================
# Agent Definition
# =============================================================================


{name.lower()}_agent = Agent(
    name="{name}",
    instructions="""{description}

When responding:
1. Be helpful and concise
2. Use tools when appropriate
3. Ask for clarification if needed
""",
    tools=[example_tool],
)


# =============================================================================
# Runner
# =============================================================================


async def run_{name.lower()}(message: str) -> str:
    """Run the {name} agent with a message."""
    result = await Runner.run({name.lower()}_agent, message)
    return result.final_output


# Synchronous helper
def run_{name.lower()}_sync(message: str) -> str:
    """Run the {name} agent synchronously."""
    result = Runner.run_sync({name.lower()}_agent, message)
    return result.final_output


if __name__ == "__main__":
    import asyncio

    async def main():
        response = await run_{name.lower()}("Hello, how can you help me?")
        print(response)

    asyncio.run(main())
'''


def generate_multi_agent(name: str, specialists: list[str]) -> str:
    """Generate a multi-agent system with router."""
    specialist_defs = []
    specialist_names = []

    for spec in specialists:
        spec_lower = spec.lower()
        specialist_names.append(f"{spec_lower}_agent")
        specialist_defs.append(f'''
{spec_lower}_agent = Agent(
    name="{spec}Agent",
    instructions="""You are a specialist in {spec.lower()} tasks.
Handle all {spec.lower()}-related queries thoroughly.""",
    tools=[],  # Add {spec.lower()}-specific tools
)
''')

    specialists_str = "\n".join(specialist_defs)
    handoffs_str = ", ".join(specialist_names)

    return f'''"""Multi-Agent System: {name}

A router-based multi-agent system with specialized agents.
"""

from agents import Agent, Runner


# =============================================================================
# Specialist Agents
# =============================================================================

{specialists_str}

# =============================================================================
# Router Agent
# =============================================================================


router_agent = Agent(
    name="{name}Router",
    instructions="""You are a routing agent that directs requests to specialists.

Available specialists:
{chr(10).join(f"- {s}Agent: Handle {s.lower()}-related queries" for s in specialists)}

Analyze each request and hand off to the appropriate specialist.
If a request doesn't fit any specialist, handle it directly.
""",
    handoffs=[{handoffs_str}],
)


# =============================================================================
# Runner
# =============================================================================


async def run_system(message: str) -> str:
    """Run the multi-agent system."""
    result = await Runner.run(router_agent, message)
    return result.final_output


if __name__ == "__main__":
    import asyncio

    async def main():
        # Test routing
        test_messages = [
            "I have a {specialists[0].lower()} question",
            "Can you help with {specialists[-1].lower()}?",
        ]

        for msg in test_messages:
            print(f"User: {{msg}}")
            response = await run_system(msg)
            print(f"Agent: {{response}}\\n")

    asyncio.run(main())
'''


def generate_structured_agent(name: str, output_fields: list[str]) -> str:
    """Generate an agent with structured output."""
    fields_str = "\n    ".join(f'{f}: str' for f in output_fields)

    return f'''"""Agent with Structured Output: {name}

Returns responses in a defined schema.
"""

from pydantic import BaseModel
from agents import Agent, Runner


# =============================================================================
# Output Schema
# =============================================================================


class {name}Output(BaseModel):
    """Structured output for {name} agent."""
    {fields_str}


# =============================================================================
# Agent Definition
# =============================================================================


{name.lower()}_agent = Agent(
    name="{name}",
    instructions="""Provide responses in the required structured format.

Always include all required fields:
{chr(10).join(f"- {f}: Description of {f}" for f in output_fields)}
""",
    output_type={name}Output,
)


# =============================================================================
# Runner
# =============================================================================


async def run_{name.lower()}(message: str) -> {name}Output:
    """Run the agent and get structured output."""
    result = await Runner.run({name.lower()}_agent, message)
    return result.final_output  # Type: {name}Output


if __name__ == "__main__":
    import asyncio

    async def main():
        result = await run_{name.lower()}("Analyze this request")

        # Access structured fields
        print(f"Output type: {{type(result)}}")
        for field in {output_fields}:
            print(f"{{field}}: {{getattr(result, field)}}")

    asyncio.run(main())
'''


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold an OpenAI Agents SDK agent"
    )
    parser.add_argument("name", help="Agent name (PascalCase)")
    parser.add_argument(
        "--description", "-d",
        default="A helpful AI assistant",
        help="Agent description"
    )
    parser.add_argument(
        "--type", "-t",
        choices=["basic", "multi", "structured"],
        default="basic",
        help="Agent type to generate"
    )
    parser.add_argument(
        "--specialists",
        nargs="+",
        default=["Support", "Sales"],
        help="Specialist names for multi-agent (e.g., Support Sales Technical)"
    )
    parser.add_argument(
        "--output-fields",
        nargs="+",
        default=["summary", "details", "recommendations"],
        help="Output fields for structured agent"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file path"
    )

    args = parser.parse_args()

    if args.type == "basic":
        code = generate_basic_agent(args.name, args.description)
    elif args.type == "multi":
        code = generate_multi_agent(args.name, args.specialists)
    elif args.type == "structured":
        code = generate_structured_agent(args.name, args.output_fields)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(code, encoding="utf-8")
        print(f"Created: {args.output}")
    else:
        print(code)


if __name__ == "__main__":
    main()
