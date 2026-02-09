"""Business logic for todo application."""

import json
import os
from pydantic import BaseModel
from typing import List

# Define the path for the tasks data file
TASKS_FILE = "tasks.json"

class Task(BaseModel):
    title: str
    description: str
    id: int | None = None
    status: bool = False

    def to_dict(self):
        return self.dict()

# Global variables for tasks and the next task ID
_tasks: List[Task] = []
_task_id_counter = 1

def _load_tasks() -> None:
    """Loads tasks from the JSON file."""
    global _tasks, _task_id_counter
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            try:
                tasks_data = json.load(f)
                _tasks = [Task(**task) for task in tasks_data]
                if _tasks:
                    # Ensure task IDs are sequential and determine the next ID
                    _tasks.sort(key=lambda x: x.id)
                    _task_id_counter = _tasks[-1].id + 1
                else:
                    _task_id_counter = 1
            except json.JSONDecodeError:
                # If the file is empty or corrupted, start with an empty list
                _tasks = []
                _task_id_counter = 1
    else:
        # If the file doesn't exist, start with an empty list
        _tasks = []
        _task_id_counter = 1

def _save_tasks() -> None:
    """Saves the current tasks to the JSON file."""
    with open(TASKS_FILE, "w") as f:
        json.dump([task.model_dump() for task in _tasks], f, indent=4)

# Load tasks when the module is imported
_load_tasks()

def add_task(title: str, description: str) -> Task:
    global _task_id_counter
    task = Task(title=title, description=description, id=_task_id_counter)
    _tasks.append(task)
    _task_id_counter += 1
    _save_tasks()  # Save changes
    return task

def get_task(task_id: int) -> Task:
    for task in _tasks:
        if task.id == task_id:
            return task
    raise ValueError(f"Task with id {task_id} not found")

def update_task(task_id: int, title: str = None, description: str = None) -> Task:
    task = get_task(task_id)
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    _save_tasks()  # Save changes
    return task

def delete_task(task_id: int) -> Task:
    task = get_task(task_id)
    _tasks.remove(task)
    _save_tasks()  # Save changes
    return task

def complete_task(task_id: int) -> Task:
    task = get_task(task_id)
    task.status = True
    _save_tasks()  # Save changes
    return task

def incomplete_task(task_id: int) -> Task:
    task = get_task(task_id)
    task.status = False
    _save_tasks()  # Save changes
    return task

def list_tasks() -> List[Task]:
    return _tasks
