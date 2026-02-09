#!/usr/bin/env python3
"""Generate task list from SpecKit Plus specifications."""

import argparse
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass


@dataclass
class UserStory:
    """Parsed user story."""
    id: str
    title: str
    role: str
    want: str
    benefit: str
    criteria: list[str]


@dataclass
class Task:
    """Generated task."""
    id: str
    title: str
    description: str
    story_id: str
    priority: str
    criteria: list[str]


def extract_user_stories(content: str) -> list[UserStory]:
    """Extract user stories from specification content."""
    stories = []

    # Pattern to match user story blocks
    story_pattern = r'###\s+(US-\d+):\s*(.+?)(?=###|## |$)'
    matches = re.findall(story_pattern, content, re.DOTALL)

    for match in matches:
        story_id = match[0]
        story_content = match[1]

        # Extract As a / I want / So that
        role_match = re.search(r'\*\*As a\*\*\s*(.+?)(?=\*\*|$)', story_content)
        want_match = re.search(r'\*\*I want\*\*\s*(.+?)(?=\*\*|$)', story_content)
        benefit_match = re.search(r'\*\*So that\*\*\s*(.+?)(?=\*\*|$)', story_content)

        role = role_match.group(1).strip() if role_match else ""
        want = want_match.group(1).strip() if want_match else ""
        benefit = benefit_match.group(1).strip() if benefit_match else ""

        # Extract acceptance criteria
        criteria = re.findall(r'-\s*\[\s*\]\s*(.+)', story_content)

        # Get title from first line after ID
        title_match = re.search(r'^(.+?)(?:\n|$)', story_content.strip())
        title = title_match.group(1).strip() if title_match else story_id

        stories.append(UserStory(
            id=story_id,
            title=title,
            role=role,
            want=want,
            benefit=benefit,
            criteria=criteria
        ))

    return stories


def generate_tasks_from_story(story: UserStory, task_counter: int) -> list[Task]:
    """Generate tasks from a user story."""
    tasks = []

    # Main implementation task
    tasks.append(Task(
        id=f"TASK-{task_counter:03d}",
        title=f"Implement: {story.title}",
        description=f"Implement functionality for {story.role} to {story.want}",
        story_id=story.id,
        priority="High",
        criteria=story.criteria[:2] if story.criteria else []
    ))
    task_counter += 1

    # Test task
    tasks.append(Task(
        id=f"TASK-{task_counter:03d}",
        title=f"Test: {story.title}",
        description=f"Write tests for {story.id}",
        story_id=story.id,
        priority="Medium",
        criteria=["Unit tests written", "Integration tests if applicable"]
    ))
    task_counter += 1

    # Documentation task if complex
    if len(story.criteria) > 3:
        tasks.append(Task(
            id=f"TASK-{task_counter:03d}",
            title=f"Document: {story.title}",
            description=f"Document the implementation of {story.id}",
            story_id=story.id,
            priority="Low",
            criteria=["API documentation updated", "Usage examples added"]
        ))

    return tasks


def generate_task_document(spec_path: Path, tasks: list[Task], stories: list[UserStory]) -> str:
    """Generate markdown task document."""
    spec_name = spec_path.stem

    doc = f"""# Tasks: {spec_name}

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Source: {spec_path.name}

## Summary

- **Total Tasks:** {len(tasks)}
- **User Stories:** {len(stories)}

---

## Task List

"""

    current_story = None
    for task in tasks:
        if task.story_id != current_story:
            current_story = task.story_id
            doc += f"\n### From {current_story}\n\n"

        doc += f"""#### {task.id}: {task.title}

- **Priority:** {task.priority}
- **Story:** {task.story_id}
- **Status:** Pending

**Description:**
{task.description}

**Acceptance Criteria:**
"""
        for criterion in task.criteria:
            doc += f"- [ ] {criterion}\n"

        doc += "\n---\n"

    return doc


def process_specification(spec_path: Path, output_path: Path) -> None:
    """Process a specification file and generate tasks."""
    print(f"Processing: {spec_path}")

    content = spec_path.read_text(encoding="utf-8")
    stories = extract_user_stories(content)

    if not stories:
        print(f"  Warning: No user stories found in {spec_path.name}")
        return

    print(f"  Found {len(stories)} user stories")

    # Generate tasks
    tasks = []
    task_counter = 1
    for story in stories:
        story_tasks = generate_tasks_from_story(story, task_counter)
        tasks.extend(story_tasks)
        task_counter += len(story_tasks)

    print(f"  Generated {len(tasks)} tasks")

    # Generate output document
    doc = generate_task_document(spec_path, tasks, stories)

    # Write output
    output_file = output_path / f"{spec_path.stem}-tasks.md"
    output_file.write_text(doc, encoding="utf-8")
    print(f"  Output: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate tasks from SpecKit Plus specifications"
    )
    parser.add_argument(
        "spec",
        type=Path,
        help="Specification file or directory"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output directory (default: .speckit/tasks)"
    )

    args = parser.parse_args()
    spec_path = args.spec

    # Determine output path
    if args.output:
        output_path = args.output
    elif spec_path.is_file():
        output_path = spec_path.parent.parent / "tasks"
    else:
        output_path = spec_path / ".speckit" / "tasks"

    output_path.mkdir(parents=True, exist_ok=True)

    # Process specifications
    if spec_path.is_file():
        process_specification(spec_path, output_path)
    else:
        spec_dir = spec_path / ".speckit" / "specifications"
        if not spec_dir.exists():
            print(f"Error: No specifications directory found at {spec_dir}")
            return

        for spec_file in spec_dir.glob("*.md"):
            process_specification(spec_file, output_path)

    print(f"\nTask generation complete!")


if __name__ == "__main__":
    main()
