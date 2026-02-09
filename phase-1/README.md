# Todo In-Memory Python Console App

## Description

This is a simple todo application that stores tasks in memory.

## Requirements

*   Python 3.13+
*   typer

## Installation

1.  Clone the repository.
2.  Create a virtual environment: `uv venv`
3.  Activate the virtual environment: `.venv/Scripts/activate`
4.  Install dependencies: `uv pip install typer`

## Usage

Run the application: `python src/main.py [command] [options]`

Available commands:

*   `add`: Add a new task.
*   `view`: View all tasks.
*   `update`: Update a task.
*   `delete`: Delete a task.
*   `complete`: Mark a task as complete.
*   `incomplete`: Mark a task as incomplete.

## Example

```
python src/main.py add --title "Buy groceries" --description "Milk, eggs, bread"
```