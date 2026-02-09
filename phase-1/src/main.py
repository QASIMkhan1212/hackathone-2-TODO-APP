"""CLI entry point for the Todo application using Typer."""

import json
import sys
from typing import List

import typer
from todo import (
    add_task,
    delete_task,
    get_task,
    incomplete_task,
    list_tasks,
    update_task,
    complete_task,
)

app = typer.Typer(add_completion=False)


def _print_tasks(tasks: List[dict]) -> None:
    """Pretty print a list of tasks."""
    if not tasks:
        typer.echo("No tasks found.")
        return
    for task in tasks:
        status = "completed" if task["status"] else "incomplete"
        typer.echo(
            f"ID: {task['id']}, Title: {task['title']}, Description: {task['description']}, Status: {status}"
        )


@app.command()
def add(title: str = typer.Argument(..., help="Title of the task"), description: str = typer.Argument(..., help="Description of the task")):
    """Add a new task."""
    task = add_task(title=title, description=description)
    typer.echo("Created task:")
    typer.echo(json.dumps(task.model_dump(), indent=2))


@app.command()
def view():
    """View all tasks."""
    tasks = list_tasks()
    tasks_dict = [task.model_dump() for task in tasks]
    _print_tasks(tasks_dict)


@app.command()
def update(
    task_id: int = typer.Argument(..., help="ID of the task to update"),
    title: str = None,
    description: str = None,
):
    """Update a task's title and/or description."""
    updated = update_task(task_id=task_id, title=title, description=description)
    typer.echo("Updated task:")
    typer.echo(json.dumps(updated.model_dump(), indent=2))


@app.command()
def delete(task_id: int = typer.Argument(..., help="ID of the task to delete")):
    """Delete a task."""
    deleted = delete_task(task_id=task_id)
    typer.echo("Deleted task:")
    typer.echo(json.dumps(deleted.model_dump(), indent=2))


@app.command()
def complete(task_id: int = typer.Argument(..., help="ID of the task to mark as complete")):
    """Mark a task as complete."""
    completed = complete_task(task_id=task_id)
    typer.echo("Completed task:")
    typer.echo(json.dumps(completed.model_dump(), indent=2))


@app.command()
def incomplete(task_id: int = typer.Argument(..., help="ID of the task to mark as incomplete")):
    """Mark a task as incomplete."""
    incomplete = incomplete_task(task_id=task_id)
    typer.echo("Incomplete task:")
    typer.echo(json.dumps(incomplete.model_dump(), indent=2))


def main() -> None:
    """Run the CLI application."""
    app()


if __name__ == "__main__":
    main()