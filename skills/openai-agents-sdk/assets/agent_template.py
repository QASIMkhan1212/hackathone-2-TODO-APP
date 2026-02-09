"""Basic OpenAI Agents SDK agent template.

This template provides a starting point for building a single agent
with tools, guardrails, and structured output.
"""

import os
from typing import Optional

from pydantic import BaseModel
from agents import (
    Agent,
    Runner,
    function_tool,
    InputGuardrail,
    OutputGuardrail,
    GuardrailFunctionOutput,
    ModelSettings,
)


# =============================================================================
# Configuration
# =============================================================================

# Ensure API key is set
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY environment variable required"


# =============================================================================
# Output Schema (Optional - for structured output)
# =============================================================================


class AgentResponse(BaseModel):
    """Structured response from the agent."""
    answer: str
    confidence: float  # 0.0 to 1.0
    sources: list[str] = []


# =============================================================================
# Tools
# =============================================================================


@function_tool
def search_knowledge_base(query: str, limit: int = 5) -> list[dict]:
    """Search the knowledge base for relevant information.

    Args:
        query: Search query string
        limit: Maximum number of results to return

    Returns:
        List of matching documents with title and content
    """
    # TODO: Implement actual search logic
    # This is a placeholder implementation
    return [
        {"title": f"Result {i}", "content": f"Content for {query}"}
        for i in range(min(limit, 3))
    ]


@function_tool
def get_current_time() -> str:
    """Get the current date and time.

    Returns:
        Current datetime as ISO string
    """
    from datetime import datetime
    return datetime.now().isoformat()


@function_tool
async def fetch_external_data(url: str) -> dict:
    """Fetch data from an external API.

    Args:
        url: The API endpoint URL

    Returns:
        API response data
    """
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()


# =============================================================================
# Guardrails
# =============================================================================


async def validate_input(input_text: str) -> GuardrailFunctionOutput:
    """Validate user input before processing.

    Args:
        input_text: The user's input message

    Returns:
        Guardrail output indicating whether to block
    """
    # Check for empty input
    if not input_text.strip():
        return GuardrailFunctionOutput(
            should_block=True,
            message="Please provide a valid question or request."
        )

    # Check for excessive length
    if len(input_text) > 10000:
        return GuardrailFunctionOutput(
            should_block=True,
            message="Input is too long. Please limit to 10,000 characters."
        )

    # Add more validation as needed
    return GuardrailFunctionOutput(should_block=False)


async def validate_output(output_text: str) -> GuardrailFunctionOutput:
    """Validate agent output before returning.

    Args:
        output_text: The agent's response

    Returns:
        Guardrail output indicating whether to block
    """
    # Check for potential PII patterns (simplified)
    import re

    # Example: block if response contains email-like patterns
    # In production, use more sophisticated PII detection
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', output_text):
        return GuardrailFunctionOutput(
            should_block=True,
            message="Response contained potentially sensitive information."
        )

    return GuardrailFunctionOutput(should_block=False)


# =============================================================================
# Agent Definition
# =============================================================================


assistant_agent = Agent(
    name="Assistant",
    instructions="""You are a helpful AI assistant.

Your capabilities:
- Search the knowledge base for information
- Fetch external data when needed
- Provide current date/time

Guidelines:
1. Be concise and accurate
2. Use tools when they would help answer the question
3. If unsure, say so rather than guessing
4. Cite sources when using knowledge base results
""",
    model="gpt-4o",
    tools=[
        search_knowledge_base,
        get_current_time,
        fetch_external_data,
    ],
    input_guardrails=[
        InputGuardrail(guardrail_function=validate_input),
    ],
    output_guardrails=[
        OutputGuardrail(guardrail_function=validate_output),
    ],
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=2048,
    ),
    # Uncomment for structured output:
    # output_type=AgentResponse,
)


# =============================================================================
# Runner Functions
# =============================================================================


async def run_agent(
    message: str,
    context: Optional[dict] = None,
    max_turns: int = 10,
) -> str:
    """Run the agent asynchronously.

    Args:
        message: User message to process
        context: Optional context data
        max_turns: Maximum conversation turns

    Returns:
        Agent's response
    """
    result = await Runner.run(
        assistant_agent,
        message,
        context=context,
        max_turns=max_turns,
    )
    return result.final_output


def run_agent_sync(
    message: str,
    context: Optional[dict] = None,
    max_turns: int = 10,
) -> str:
    """Run the agent synchronously.

    Args:
        message: User message to process
        context: Optional context data
        max_turns: Maximum conversation turns

    Returns:
        Agent's response
    """
    result = Runner.run_sync(
        assistant_agent,
        message,
        context=context,
        max_turns=max_turns,
    )
    return result.final_output


# =============================================================================
# Main
# =============================================================================


if __name__ == "__main__":
    import asyncio

    async def main():
        # Example usage
        questions = [
            "What time is it?",
            "Search the knowledge base for Python best practices",
            "Help me understand async programming",
        ]

        for question in questions:
            print(f"\nUser: {question}")
            response = await run_agent(question)
            print(f"Agent: {response}")

    asyncio.run(main())
