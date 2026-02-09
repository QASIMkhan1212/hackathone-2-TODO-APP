#!/usr/bin/env python3
"""Set up tracing for OpenAI Agents SDK."""

import argparse


def generate_logfire_config() -> str:
    """Generate Logfire tracing configuration."""
    return '''"""Logfire tracing configuration for OpenAI Agents SDK."""

import os
from agents.tracing import LogfireTracer, trace

# =============================================================================
# Configuration
# =============================================================================

LOGFIRE_TOKEN = os.getenv("LOGFIRE_TOKEN")
LOGFIRE_PROJECT = os.getenv("LOGFIRE_PROJECT", "agents-project")

# =============================================================================
# Setup
# =============================================================================


def setup_logfire_tracing():
    """Initialize Logfire tracing."""
    if not LOGFIRE_TOKEN:
        print("Warning: LOGFIRE_TOKEN not set, tracing disabled")
        return

    tracer = LogfireTracer(
        token=LOGFIRE_TOKEN,
        project=LOGFIRE_PROJECT,
    )
    trace.set_tracer(tracer)
    print(f"Logfire tracing enabled for project: {LOGFIRE_PROJECT}")


# =============================================================================
# Usage Example
# =============================================================================

if __name__ == "__main__":
    setup_logfire_tracing()

    # Your agent code here
    from agents import Agent, Runner

    agent = Agent(name="TracedAgent", instructions="You are helpful.")

    async def main():
        result = await Runner.run(agent, "Hello!")
        print(result.final_output)

    import asyncio
    asyncio.run(main())
'''


def generate_agentops_config() -> str:
    """Generate AgentOps tracing configuration."""
    return '''"""AgentOps tracing configuration for OpenAI Agents SDK."""

import os
from agents.tracing import AgentOpsTracer, trace

# =============================================================================
# Configuration
# =============================================================================

AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")
AGENTOPS_PROJECT_ID = os.getenv("AGENTOPS_PROJECT_ID")

# =============================================================================
# Setup
# =============================================================================


def setup_agentops_tracing():
    """Initialize AgentOps tracing."""
    if not AGENTOPS_API_KEY:
        print("Warning: AGENTOPS_API_KEY not set, tracing disabled")
        return

    tracer = AgentOpsTracer(
        api_key=AGENTOPS_API_KEY,
        project_id=AGENTOPS_PROJECT_ID,
    )
    trace.set_tracer(tracer)
    print("AgentOps tracing enabled")


# =============================================================================
# Usage Example
# =============================================================================

if __name__ == "__main__":
    setup_agentops_tracing()

    from agents import Agent, Runner

    agent = Agent(name="TracedAgent", instructions="You are helpful.")

    async def main():
        result = await Runner.run(agent, "Hello!")
        print(result.final_output)

    import asyncio
    asyncio.run(main())
'''


def generate_custom_tracer() -> str:
    """Generate custom tracer template."""
    return '''"""Custom tracing configuration for OpenAI Agents SDK."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from agents.tracing import Tracer, Span, trace


# =============================================================================
# Custom Span Implementation
# =============================================================================


class FileSpan(Span):
    """Span that logs to a file."""

    def __init__(
        self,
        name: str,
        span_id: str,
        parent_id: Optional[str],
        logger: "FileTracer"
    ):
        self.name = name
        self.span_id = span_id
        self.parent_id = parent_id
        self.logger = logger
        self.start_time = time.time()
        self.attributes: dict[str, Any] = {}

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def record_exception(self, exception: Exception) -> None:
        self.attributes["error"] = str(exception)
        self.attributes["error_type"] = type(exception).__name__

    def end(self) -> None:
        duration = time.time() - self.start_time
        self.logger.log_span(
            span_id=self.span_id,
            parent_id=self.parent_id,
            name=self.name,
            duration_ms=duration * 1000,
            attributes=self.attributes,
        )


# =============================================================================
# Custom Tracer Implementation
# =============================================================================


class FileTracer(Tracer):
    """Tracer that writes traces to a JSON file."""

    def __init__(self, output_path: str = "traces.jsonl"):
        self.output_path = Path(output_path)
        self.span_counter = 0

    def start_span(
        self,
        name: str,
        parent: Optional[Span] = None,
        **kwargs
    ) -> Span:
        self.span_counter += 1
        span_id = f"span_{self.span_counter}"
        parent_id = parent.span_id if parent else None

        return FileSpan(name, span_id, parent_id, self)

    def log_span(
        self,
        span_id: str,
        parent_id: Optional[str],
        name: str,
        duration_ms: float,
        attributes: dict,
    ) -> None:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "span_id": span_id,
            "parent_id": parent_id,
            "name": name,
            "duration_ms": round(duration_ms, 2),
            "attributes": attributes,
        }

        with open(self.output_path, "a") as f:
            f.write(json.dumps(entry) + "\\n")


# =============================================================================
# Setup
# =============================================================================


def setup_file_tracing(output_path: str = "traces.jsonl"):
    """Initialize file-based tracing."""
    tracer = FileTracer(output_path)
    trace.set_tracer(tracer)
    print(f"File tracing enabled, output: {output_path}")


# =============================================================================
# Usage Example
# =============================================================================

if __name__ == "__main__":
    setup_file_tracing("agent_traces.jsonl")

    from agents import Agent, Runner

    agent = Agent(name="TracedAgent", instructions="You are helpful.")

    async def main():
        # Custom span
        with trace.span("my_workflow") as span:
            span.set_attribute("workflow_type", "test")

            result = await Runner.run(agent, "Hello!")
            span.set_attribute("output_length", len(result.final_output))

        print(result.final_output)

    import asyncio
    asyncio.run(main())
'''


def generate_env_template() -> str:
    """Generate environment template."""
    return '''# OpenAI Agents SDK Tracing Configuration

# Required: OpenAI API Key
OPENAI_API_KEY=sk-...

# Enable/disable tracing
OPENAI_AGENTS_TRACING_ENABLED=true

# Logfire configuration
LOGFIRE_TOKEN=your_logfire_token
LOGFIRE_PROJECT=my-agents-project

# AgentOps configuration
AGENTOPS_API_KEY=your_agentops_key
AGENTOPS_PROJECT_ID=project_123

# Braintrust configuration
BRAINTRUST_API_KEY=your_braintrust_key

# Custom file tracing
TRACE_OUTPUT_PATH=traces.jsonl
'''


def main():
    parser = argparse.ArgumentParser(
        description="Set up tracing for OpenAI Agents SDK"
    )
    parser.add_argument(
        "--backend", "-b",
        choices=["logfire", "agentops", "custom", "env"],
        default="custom",
        help="Tracing backend to configure"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path"
    )

    args = parser.parse_args()

    generators = {
        "logfire": generate_logfire_config,
        "agentops": generate_agentops_config,
        "custom": generate_custom_tracer,
        "env": generate_env_template,
    }

    code = generators[args.backend]()

    if args.output:
        Path(args.output).write_text(code, encoding="utf-8")
        print(f"Created: {args.output}")
    else:
        print(code)


if __name__ == "__main__":
    main()
