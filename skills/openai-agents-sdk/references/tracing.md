# Tracing and Observability Reference

## Built-in Tracing

Tracing is enabled by default and captures:
- Agent runs and their inputs/outputs
- Tool calls and results
- Handoffs between agents
- Token usage and latency

```python
from agents import Agent, Runner

# Traces are automatic
result = await Runner.run(agent, "Hello")

# View traces in OpenAI dashboard or configured backend
```

## Environment Configuration

```bash
# Enable/disable tracing
export OPENAI_AGENTS_TRACING_ENABLED=true

# Set tracing backend
export OPENAI_AGENTS_TRACING_BACKEND=logfire

# API keys for external backends
export LOGFIRE_TOKEN=your_token
export AGENTOPS_API_KEY=your_key
```

## Custom Trace Spans

Add custom spans for your own operations:

```python
from agents import trace

async def my_workflow():
    # Automatic span for entire workflow
    with trace.span("my_workflow"):

        # Nested span for database operations
        with trace.span("database_query"):
            data = await database.fetch_data()

        # Nested span for processing
        with trace.span("data_processing"):
            result = process(data)

        return result
```

## Adding Metadata to Spans

```python
from agents import trace

with trace.span("user_request") as span:
    span.set_attribute("user_id", "user_123")
    span.set_attribute("request_type", "search")
    span.set_attribute("query_length", len(query))

    result = await process_request(query)

    span.set_attribute("result_count", len(result))
```

## External Tracing Backends

### Logfire

```python
from agents.tracing import LogfireTracer

# Configure Logfire
tracer = LogfireTracer(
    token="your_logfire_token",
    project="my-agents-project"
)

# Set as default tracer
trace.set_tracer(tracer)
```

### AgentOps

```python
from agents.tracing import AgentOpsTracer

tracer = AgentOpsTracer(
    api_key="your_agentops_key",
    project_id="project_123"
)

trace.set_tracer(tracer)
```

### Custom Backend

```python
from agents.tracing import Tracer, Span

class CustomTracer(Tracer):
    def start_span(self, name: str, **kwargs) -> Span:
        # Create span in your system
        span_id = your_tracing_system.start(name)
        return CustomSpan(span_id)

    def end_span(self, span: Span) -> None:
        your_tracing_system.end(span.span_id)

class CustomSpan(Span):
    def __init__(self, span_id: str):
        self.span_id = span_id

    def set_attribute(self, key: str, value: any) -> None:
        your_tracing_system.set_attr(self.span_id, key, value)

    def record_exception(self, exception: Exception) -> None:
        your_tracing_system.record_error(self.span_id, exception)

# Use custom tracer
trace.set_tracer(CustomTracer())
```

## Tracing Multi-Agent Workflows

```python
from agents import Agent, Runner, trace

router = Agent(name="Router", handoffs=[agent_a, agent_b])

async def traced_workflow(request: str):
    with trace.span("customer_support_flow") as root:
        root.set_attribute("request_id", generate_id())
        root.set_attribute("customer_tier", "premium")

        # Runner automatically creates child spans for:
        # - router execution
        # - tool calls
        # - handoffs to agent_a or agent_b
        result = await Runner.run(router, request)

        root.set_attribute("final_agent", result.agent.name)
        root.set_attribute("total_turns", len(result.raw_responses))

        return result
```

## Debugging with Traces

```python
from agents import Agent, Runner, trace

async def debug_agent_run():
    with trace.span("debug_session") as span:
        try:
            result = await Runner.run(agent, "Test query")

            # Log success metrics
            span.set_attribute("success", True)
            span.set_attribute("output_length", len(result.final_output))

        except Exception as e:
            # Record exception in trace
            span.record_exception(e)
            span.set_attribute("success", False)
            raise

        return result
```

## Performance Monitoring

```python
import time
from agents import trace

async def monitored_operation():
    with trace.span("operation") as span:
        start = time.time()

        result = await expensive_operation()

        duration = time.time() - start
        span.set_attribute("duration_ms", duration * 1000)
        span.set_attribute("result_size_bytes", len(str(result)))

        return result
```

## Trace Filtering

Filter what gets traced:

```python
from agents.tracing import TraceFilter

# Only trace specific agents
filter = TraceFilter(
    include_agents=["ImportantAgent", "CriticalAgent"],
    exclude_tools=["debug_tool"],
    min_duration_ms=100,  # Skip fast operations
)

trace.set_filter(filter)
```

## Exporting Traces

```python
from agents import trace

# Export trace data
traces = trace.export(
    format="json",
    start_time=start,
    end_time=end,
)

# Save to file
with open("traces.json", "w") as f:
    json.dump(traces, f)

# Or send to your analytics system
analytics.ingest(traces)
```

## Best Practices

1. **Meaningful Span Names**: Use descriptive names like `user_authentication` not `span1`
2. **Relevant Attributes**: Add context that helps debugging
3. **Error Recording**: Always record exceptions in spans
4. **Appropriate Granularity**: Don't create spans for trivial operations
5. **Sensitive Data**: Avoid logging PII or secrets in traces
6. **Sampling**: Use sampling for high-volume production

```python
# Good tracing example
with trace.span("process_order") as span:
    span.set_attribute("order_id", order.id)
    span.set_attribute("item_count", len(order.items))
    # Don't log: customer email, credit card, etc.

    try:
        result = await process(order)
        span.set_attribute("status", "success")
    except Exception as e:
        span.set_attribute("status", "error")
        span.record_exception(e)
        raise
```
