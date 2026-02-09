---
name: speckitplus
description: Spec-driven AI development workflow using SpecKit Plus. Use when users want to (1) initialize a new project with structured specifications, (2) create project constitutions, requirements, or user stories, (3) plan technical implementations, (4) generate task lists from specs, (5) implement features following spec-driven methodology, (6) analyze cross-artifact consistency, or (7) follow structured multi-agent development patterns. Triggers on mentions of "speckit", "spec-driven", "specification workflow", or slash commands like /sp.specify, /sp.plan, /sp.tasks.
---

# SpecKit Plus

Spec-driven development workflow combining rapid AI code generation with structured architectural patterns.

## Core Workflow

Follow this sequence for spec-driven development:

1. **Constitution** → Establish governing principles (`/sp.constitution`)
2. **Specification** → Define requirements and user stories (`/sp.specify`)
3. **Plan** → Create technical implementation strategy (`/sp.plan`)
4. **Tasks** → Generate actionable task lists (`/sp.tasks`)
5. **Implementation** → Execute tasks and build features (`/sp.implement`)

Use `/sp.clarify` and `/sp.analyze` at any point for validation.

## Installation

```bash
# Persistent install
pip install specifyplus
# or
uv tool install specifyplus

# One-time use
uvx specifyplus init <PROJECT_NAME>
```

### Init Options

```bash
specifyplus init <name> [options]
  --ai [claude|gemini|copilot|cursor|qwen|...]  # Target AI agent
  --script [sh|ps]                               # Shell script type
  --here                                         # Initialize in current dir
  --force                                        # Skip confirmation
```

## Slash Commands Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/sp.constitution` | Establish project principles | Project start, governance setup |
| `/sp.specify` | Define requirements/stories | Requirements gathering phase |
| `/sp.plan` | Technical implementation plan | After specs are defined |
| `/sp.tasks` | Generate task lists | Before implementation |
| `/sp.implement` | Execute tasks | During development |
| `/sp.clarify` | Resolve ambiguities | When specs are unclear |
| `/sp.analyze` | Cross-artifact consistency | Validation checkpoints |
| `/sp.checklist` | Quality validation | Before milestones |

**Detailed command usage**: See [references/commands.md](references/commands.md)

## Project Structure

After initialization, SpecKit Plus creates:

```
project-name/
├── .speckit/
│   ├── constitution.md     # Project principles
│   ├── specifications/     # Requirements & user stories
│   ├── plans/              # Technical plans
│   ├── tasks/              # Generated task lists
│   └── history/            # Prompt & architecture history
├── src/                    # Source code
├── tests/                  # Test files
└── docs/                   # Documentation
```

## Development Phases

### Phase 1: Greenfield (0-to-1)
Generate new applications from requirements:
1. Run `/sp.constitution` to establish principles
2. Run `/sp.specify` to define requirements
3. Run `/sp.plan` for technical strategy
4. Run `/sp.tasks` to generate work items
5. Run `/sp.implement` to build features

### Phase 2: Brownfield (Enhancement)
Modernize or expand existing systems:
1. Run `/sp.analyze` to understand current state
2. Run `/sp.specify` for new requirements
3. Run `/sp.plan` integrating with existing architecture
4. Run `/sp.tasks` and `/sp.implement`

### Phase 3: Creative Exploration
Test parallel implementations:
1. Define base specification
2. Generate variants across tech stacks
3. Compare and evaluate outputs

## Best Practices

1. **Spec First**: Always define specifications before coding
2. **Iterative Refinement**: Use multi-step refinement over one-shot generation
3. **Living Documentation**: Keep specs version-controlled alongside code
4. **Consistency Checks**: Run `/sp.analyze` at major checkpoints
5. **Task Granularity**: Break large specs into atomic tasks

## Templates

Pre-built templates available for common patterns:
- **API Services**: REST/GraphQL endpoints
- **Multi-Agent Systems**: OpenAI Agents SDK patterns
- **Kubernetes Deployments**: Container orchestration
- **Dapr Applications**: Distributed application runtime

**Template details**: See [references/templates.md](references/templates.md)

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init_project.py` | Initialize new SpecKit Plus project |
| `scripts/validate_specs.py` | Validate specification consistency |
| `scripts/generate_tasks.py` | Generate tasks from specifications |
