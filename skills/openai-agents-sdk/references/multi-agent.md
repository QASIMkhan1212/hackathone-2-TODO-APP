# Multi-Agent Patterns Reference

## Basic Handoffs

Transfer control between specialized agents:

```python
from agents import Agent, Runner

# Specialized agents
billing_agent = Agent(
    name="BillingAgent",
    instructions="""Handle billing inquiries:
    - Account balance
    - Payment methods
    - Invoice questions""",
    tools=[get_balance, update_payment, get_invoices],
)

technical_agent = Agent(
    name="TechnicalAgent",
    instructions="""Handle technical support:
    - Bug reports
    - Feature questions
    - Troubleshooting""",
    tools=[search_docs, create_ticket, check_status],
)

# Router agent
router = Agent(
    name="SupportRouter",
    instructions="""Route customer requests:
    - Billing/payment questions -> BillingAgent
    - Technical issues/bugs -> TechnicalAgent
    - General questions: answer directly""",
    handoffs=[billing_agent, technical_agent],
)

# Automatic routing
result = await Runner.run(router, "I have a question about my invoice")
# Automatically hands off to BillingAgent
```

## Hierarchical Multi-Agent

```python
# Level 1: Specialist agents
researcher = Agent(
    name="Researcher",
    instructions="Gather information on topics.",
    tools=[web_search, fetch_url],
)

analyst = Agent(
    name="Analyst",
    instructions="Analyze data and extract insights.",
    tools=[analyze_data, create_chart],
)

writer = Agent(
    name="Writer",
    instructions="Write clear, engaging content.",
    tools=[format_document, add_citations],
)

# Level 2: Team lead
content_lead = Agent(
    name="ContentLead",
    instructions="""Coordinate content creation:
    1. Delegate research to Researcher
    2. Have Analyst process findings
    3. Direct Writer to create final content""",
    handoffs=[researcher, analyst, writer],
)

# Level 3: Executive
executive = Agent(
    name="Executive",
    instructions="""Handle high-level requests.
    Delegate content work to ContentLead.""",
    handoffs=[content_lead],
)
```

## Bidirectional Handoffs

Agents can hand back to the original:

```python
qa_agent = Agent(
    name="QAAgent",
    instructions="""Review and validate work.
    If issues found, hand back to Developer for fixes.""",
)

developer = Agent(
    name="Developer",
    instructions="""Write code solutions.
    When done, hand to QAAgent for review.""",
)

# Set up bidirectional handoffs
qa_agent.handoffs = [developer]
developer.handoffs = [qa_agent]

# Start with developer
result = await Runner.run(developer, "Implement a sorting function")
# Developer -> QA -> Developer (if issues) -> QA -> Done
```

## Parallel Agent Execution

Run multiple agents concurrently:

```python
import asyncio
from agents import Agent, Runner

# Independent specialist agents
agents = [
    Agent(name="SecurityReviewer", instructions="Review for security issues."),
    Agent(name="PerformanceReviewer", instructions="Review for performance."),
    Agent(name="StyleReviewer", instructions="Review code style."),
]

async def parallel_review(code: str) -> list[str]:
    """Run all reviewers in parallel."""
    tasks = [
        Runner.run(agent, f"Review this code:\n{code}")
        for agent in agents
    ]
    results = await asyncio.gather(*tasks)
    return [r.final_output for r in results]

# Usage
reviews = await parallel_review(code_to_review)
```

## Agent with Conditional Handoffs

```python
from agents import Agent, function_tool

@function_tool
def check_complexity(task: str) -> str:
    """Assess task complexity."""
    # Simple heuristic
    if len(task) > 500 or "complex" in task.lower():
        return "complex"
    return "simple"

simple_agent = Agent(
    name="SimpleAgent",
    instructions="Handle straightforward tasks quickly.",
)

complex_agent = Agent(
    name="ComplexAgent",
    instructions="Handle complex, multi-step tasks thoroughly.",
)

router = Agent(
    name="Router",
    instructions="""Assess incoming tasks:
    1. Use check_complexity tool
    2. If complex -> ComplexAgent
    3. If simple -> SimpleAgent""",
    tools=[check_complexity],
    handoffs=[simple_agent, complex_agent],
)
```

## Stateful Multi-Agent Workflow

```python
from agents import Agent, Runner, SQLiteSession

# Shared session for state
session = SQLiteSession("workflow_123")

intake_agent = Agent(
    name="IntakeAgent",
    instructions="Gather initial requirements from user.",
)

planning_agent = Agent(
    name="PlanningAgent",
    instructions="Create execution plan based on requirements.",
)

execution_agent = Agent(
    name="ExecutionAgent",
    instructions="Execute the plan step by step.",
)

# Workflow with shared memory
async def run_workflow(request: str):
    # Step 1: Intake
    await Runner.run(intake_agent, request, session=session)

    # Step 2: Planning (has access to intake context)
    await Runner.run(
        planning_agent,
        "Create a plan based on the gathered requirements.",
        session=session
    )

    # Step 3: Execution (has access to plan)
    result = await Runner.run(
        execution_agent,
        "Execute the plan.",
        session=session
    )

    return result.final_output
```

## Multi-Agent Patterns Summary

| Pattern | Use Case |
|---------|----------|
| **Router** | Classify and delegate to specialists |
| **Pipeline** | Sequential processing through agents |
| **Hierarchical** | Multi-level delegation |
| **Parallel** | Concurrent independent tasks |
| **Bidirectional** | Review/revision cycles |
| **Stateful** | Shared context across agents |

## Best Practices

1. **Clear Boundaries**: Each agent should have distinct responsibilities
2. **Explicit Instructions**: Tell agents exactly when to hand off
3. **Shared Context**: Use sessions for state that spans agents
4. **Limit Depth**: Avoid too many levels of handoffs
5. **Monitor Handoffs**: Use tracing to debug agent interactions
6. **Graceful Fallbacks**: Handle cases where no agent is suitable

```python
# Good: Clear handoff instructions
router = Agent(
    name="Router",
    instructions="""Route requests:
    - BILLING keywords (invoice, payment, refund) -> BillingAgent
    - TECHNICAL keywords (bug, error, crash) -> TechnicalAgent
    - If unclear, ask the user to clarify.
    - NEVER make assumptions about which agent to use.""",
    handoffs=[billing_agent, technical_agent],
)
```
