"""MCP tools for todo operations working with SQLModel."""
from typing import Any, Dict, List
from sqlmodel import Session, select

from models import Task


class MCPToolServer:
    """In-process MCP tool server for todo operations using SQLModel."""

    def __init__(self):
        self.tools = {
            "add_task": {
                "name": "add_task",
                "description": "Create a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user's ID"
                        },
                        "title": {
                            "type": "string",
                            "description": "The title/content of the task"
                        }
                    },
                    "required": ["user_id", "title"]
                }
            },
            "list_tasks": {
                "name": "list_tasks",
                "description": "List all tasks for a user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user's ID"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            "complete_task": {
                "name": "complete_task",
                "description": "Mark a task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user's ID"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to complete"
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            },
            "delete_task": {
                "name": "delete_task",
                "description": "Delete a task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user's ID"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to delete"
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            },
            "update_task": {
                "name": "update_task",
                "description": "Update a task's content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user's ID"
                        },
                        "task_id": {
                            "type": "integer",
                            "description": "The ID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New content for the task"
                        }
                    },
                    "required": ["user_id", "task_id", "title"]
                }
            }
        }

    def get_tools(self) -> List[Dict]:
        """Return list of available tools."""
        return list(self.tools.values())

    def call_tool(self, session: Session, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        if name == "add_task":
            return self._add_task(session, arguments)
        elif name == "list_tasks":
            return self._list_tasks(session, arguments)
        elif name == "complete_task":
            return self._complete_task(session, arguments)
        elif name == "delete_task":
            return self._delete_task(session, arguments)
        elif name == "update_task":
            return self._update_task(session, arguments)
        else:
            return {"error": f"Unknown tool: {name}"}

    def _add_task(self, session: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task."""
        user_id = args.get("user_id")
        title = args.get("title")

        # Create task using SQLModel
        task = Task(content=title, completed=False, user_id=user_id)
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.content
        }

    def _list_tasks(self, session: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """List tasks for a user."""
        user_id = args.get("user_id")

        # Get all tasks for user
        tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()

        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.content,
                    "completed": task.completed
                }
                for task in tasks
            ],
            "count": len(tasks)
        }

    def _complete_task(self, session: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """Mark a task as completed."""
        user_id = args.get("user_id")
        task_id = args.get("task_id")

        # Get task
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return {
                "task_id": task_id,
                "status": "not_found",
                "error": f"Task {task_id} not found"
            }

        # Toggle completion
        task.completed = not task.completed
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": task.id,
            "status": "completed" if task.completed else "uncompleted",
            "title": task.content
        }

    def _delete_task(self, session: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a task."""
        user_id = args.get("user_id")
        task_id = args.get("task_id")

        # Get task
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return {
                "task_id": task_id,
                "status": "not_found",
                "error": f"Task {task_id} not found"
            }

        title = task.content
        session.delete(task)
        session.commit()

        return {
            "task_id": task_id,
            "status": "deleted",
            "title": title
        }

    def _update_task(self, session: Session, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task."""
        user_id = args.get("user_id")
        task_id = args.get("task_id")
        title = args.get("title")

        # Get task
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return {
                "task_id": task_id,
                "status": "not_found",
                "error": f"Task {task_id} not found"
            }

        task.content = title
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.content
        }


# Global MCP server instance
mcp_server = MCPToolServer()


def call_mcp_tool(session: Session, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to call an MCP tool."""
    return mcp_server.call_tool(session, name, arguments)
