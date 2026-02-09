#!/usr/bin/env python3
"""Initialize a new SpecKit Plus project structure."""

import argparse
import os
from pathlib import Path
from datetime import datetime


def create_directory(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    print(f"  Created: {path}")


def write_file(path: Path, content: str) -> None:
    """Write content to file."""
    path.write_text(content, encoding="utf-8")
    print(f"  Created: {path}")


def init_project(name: str, base_path: Path, ai_agent: str = "claude") -> None:
    """Initialize SpecKit Plus project structure."""

    project_path = base_path / name

    if project_path.exists():
        print(f"Error: Directory '{project_path}' already exists.")
        return

    print(f"\nInitializing SpecKit Plus project: {name}")
    print("=" * 50)

    # Create directory structure
    directories = [
        ".speckit/specifications",
        ".speckit/plans",
        ".speckit/tasks",
        ".speckit/history",
        "src",
        "tests",
        "docs",
    ]

    for dir_name in directories:
        create_directory(project_path / dir_name)

    # Create constitution template
    constitution_content = f"""# Project Constitution: {name}

Created: {datetime.now().strftime("%Y-%m-%d")}
AI Agent: {ai_agent}

## Mission

[Define the project's purpose and goals]

## Technical Stack

- **Language:** [e.g., Python 3.11+]
- **Framework:** [e.g., FastAPI, Django]
- **Database:** [e.g., PostgreSQL, MongoDB]
- **Deployment:** [e.g., Docker, Kubernetes]

## Quality Standards

- Test coverage: >80%
- Documentation: Required for all public APIs
- Code review: Required before merge
- Linting: [tool and rules]

## Security Requirements

- Authentication: [method]
- Authorization: [model]
- Data handling: [policies]

## Performance Targets

- Response time: [target]
- Throughput: [target]
- Availability: [target]

## Team Conventions

- Branch naming: [pattern]
- Commit messages: [format]
- PR process: [workflow]
"""
    write_file(project_path / ".speckit/constitution.md", constitution_content)

    # Create example specification
    spec_content = """# Feature: Example Feature

## Overview

[Brief description of the feature]

## User Stories

### US-001: Example User Story

**As a** user
**I want** to perform an action
**So that** I achieve a benefit

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Non-Functional Requirements

- **Performance:** [targets]
- **Security:** [requirements]
- **Scalability:** [expectations]

## Dependencies

- [List dependencies]

## Open Questions

- [Questions to resolve with /sp.clarify]
"""
    write_file(project_path / ".speckit/specifications/example.md", spec_content)

    # Create .gitignore
    gitignore_content = """# SpecKit Plus
.speckit/history/*.log

# Python
__pycache__/
*.py[cod]
*$py.class
.env
.venv/
venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Build
dist/
build/
*.egg-info/
"""
    write_file(project_path / ".gitignore", gitignore_content)

    # Create README
    readme_content = f"""# {name}

A SpecKit Plus project.

## Getting Started

1. Review the constitution: `.speckit/constitution.md`
2. Define specifications: `/sp.specify`
3. Create implementation plan: `/sp.plan`
4. Generate tasks: `/sp.tasks`
5. Implement: `/sp.implement`

## Project Structure

```
{name}/
├── .speckit/
│   ├── constitution.md     # Project principles
│   ├── specifications/     # Requirements & user stories
│   ├── plans/              # Technical plans
│   ├── tasks/              # Task lists
│   └── history/            # Prompt history
├── src/                    # Source code
├── tests/                  # Tests
└── docs/                   # Documentation
```

## Commands

| Command | Purpose |
|---------|---------|
| `/sp.constitution` | Update project principles |
| `/sp.specify` | Define requirements |
| `/sp.plan` | Create technical plan |
| `/sp.tasks` | Generate task list |
| `/sp.implement` | Execute tasks |
| `/sp.clarify` | Resolve ambiguities |
| `/sp.analyze` | Consistency check |
"""
    write_file(project_path / "README.md", readme_content)

    print("\n" + "=" * 50)
    print(f"Project '{name}' initialized successfully!")
    print(f"\nNext steps:")
    print(f"  1. cd {name}")
    print(f"  2. Edit .speckit/constitution.md")
    print(f"  3. Run /sp.specify to define requirements")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new SpecKit Plus project"
    )
    parser.add_argument("name", help="Project name")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Base path for project (default: current directory)"
    )
    parser.add_argument(
        "--ai",
        default="claude",
        choices=["claude", "gemini", "copilot", "cursor", "qwen"],
        help="Target AI agent (default: claude)"
    )

    args = parser.parse_args()
    init_project(args.name, args.path, args.ai)


if __name__ == "__main__":
    main()
