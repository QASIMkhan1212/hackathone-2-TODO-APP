import os
import json
import pytest
from src.todo import (
    Task,
    add_task,
    get_task,
    update_task,
    delete_task,
    complete_task,
    incomplete_task,
    list_tasks,
    _tasks, # Accessing internal for test setup/teardown
    _task_id_counter, # Accessing internal for test setup/teardown
    TASKS_FILE,
)

# Fixture to set up and tear down the tasks file for each test
@pytest.fixture(autouse=True)
def manage_tasks_file():
    # Before test: ensure tasks.json is clean or empty
    if os.path.exists(TASKS_FILE):
        os.remove(TASKS_FILE)
    # Re-initialize _tasks and _task_id_counter for a clean state
    _tasks.clear()
    global _task_id_counter
    _task_id_counter = 1
    # Explicitly call _load_tasks to ensure the module's state is reset based on a potentially empty file
    from src.todo import _load_tasks
    _load_tasks()
    yield
    # After test: clean up tasks.json
    if os.path.exists(TASKS_FILE):
        os.remove(TASKS_FILE)

def test_add_task():
    task = add_task("Test Title", "Test Description")
    assert task.id == 1
    assert task.title == "Test Title"
    assert task.description == "Test Description"
    assert task.status is False
    assert len(list_tasks()) == 1
    assert list_tasks()[0].id == 1

def test_get_task():
    add_task("Test Title 1", "Test Description 1")
    task = get_task(1)
    assert task.title == "Test Title 1"
    with pytest.raises(ValueError):
        get_task(99)

def test_update_task():
    add_task("Old Title", "Old Description")
    updated_task = update_task(1, "New Title", "New Description")
    assert updated_task.title == "New Title"
    assert updated_task.description == "New Description"
    fetched_task = get_task(1)
    assert fetched_task.title == "New Title"
    assert fetched_task.description == "New Description"

def test_delete_task():
    add_task("Task to Delete", "Description to Delete")
    deleted_task = delete_task(1)
    assert deleted_task.id == 1
    assert len(list_tasks()) == 0
    with pytest.raises(ValueError):
        get_task(1)

def test_complete_task():
    add_task("Task to Complete", "Description")
    completed_task = complete_task(1)
    assert completed_task.status is True
    assert get_task(1).status is True

def test_incomplete_task():
    add_task("Task to Incomplete", "Description")
    complete_task(1) # First complete it
    incomplete_task_obj = incomplete_task(1)
    assert incomplete_task_obj.status is False
    assert get_task(1).status is False

def test_list_tasks():
    assert len(list_tasks()) == 0
    add_task("Task 1", "Desc 1")
    add_task("Task 2", "Desc 2")
    tasks = list_tasks()
    assert len(tasks) == 2
    assert tasks[0].title == "Task 1"
    assert tasks[1].title == "Task 2"

def test_task_persistence():
    add_task("Persistent Task", "This should stay")
    # Simulate reloading the module to check persistence
    # In a real scenario, this might involve re-importing or restarting the app.
    # For this test, we'll manually clear _tasks and reload.
    _tasks.clear()
    global _task_id_counter
    _task_id_counter = 1

    # This part would typically involve re-importing the module, which is tricky in pytest.
    # Instead, we will directly call the internal _load_tasks method after clearing.
    # This mimics the behavior of the application starting up and loading tasks.
    from src.todo import _load_tasks as reload_tasks
    reload_tasks()

    reloaded_tasks = list_tasks()
    assert len(reloaded_tasks) == 1
    assert reloaded_tasks[0].title == "Persistent Task"
    assert reloaded_tasks[0].id == 1

def test_task_id_counter_on_load():
    # Add some tasks
    add_task("Task A", "Desc A")
    add_task("Task B", "Desc B")
    # Clear and reload to simulate app restart
    _tasks.clear()
    global _task_id_counter
    _task_id_counter = 1

    from src.todo import _load_tasks as reload_tasks
    reload_tasks()

    # Add a new task after reload, its ID should be based on existing max ID + 1
    new_task = add_task("Task C", "Desc C")
    assert new_task.id == 3
    assert len(list_tasks()) == 3

