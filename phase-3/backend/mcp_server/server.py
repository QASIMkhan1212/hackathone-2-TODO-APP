"""MCP Server for Todo Chatbot with 5 tools."""
import json
from typing import Any, Optional
from sqlalchemy.orm import Session

from app.crud.task import task_crud
from app.schemas.task import TaskCreate, TaskUpdate


class MCPToolServer:
    """In-process MCP tool server for todo operations."""

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
                            "description": "The title of the task"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the task"
                        }
                    },
                    "required": ["user_id", "title"]
                }
            },
            "list_tasks": {
                "name": "list_tasks",
                "description": "List all tasks for a user, optionally filtered by status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "The user's ID"
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status: 'pending', 'completed', or omit for all",
                            "enum": ["pending", "completed"]
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
                "description": "Update a task's title or description",
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
                            "description": "New title for the task"
                        },
                        "description": {
                            "type": "string",
                            "description": "New description for the task"
                        }
                    },
                    "required": ["user_id", "task_id"]
                }
            }
        }

    def get_tools(self) -> list:
        """Return list of available tools."""
        return list(self.tools.values())

    def call_tool(
        self,
        db: Session,
        name: str,
        arguments: dict
    ) -> dict:
        """Execute a tool and return the result."""
        if name == "add_task":
            return self._add_task(db, arguments)
        elif name == "list_tasks":
            return self._list_tasks(db, arguments)
        elif name == "complete_task":
            return self._complete_task(db, arguments)
        elif name == "delete_task":
            return self._delete_task(db, arguments)
        elif name == "update_task":
            return self._update_task(db, arguments)
        else:
            return {"error": f"Unknown tool: {name}"}

    def _add_task(self, db: Session, args: dict) -> dict:
        """Create a new task."""
        user_id = args.get("user_id")
        title = args.get("title")
        description = args.get("description")

        task_data = TaskCreate(title=title, description=description)
        task = task_crud.create(db, user_id, task_data)

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }

    def _list_tasks(self, db: Session, args: dict) -> dict:
        """List tasks for a user."""
        user_id = args.get("user_id")
        status = args.get("status")

        tasks = task_crud.get_all(db, user_id, status)

        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if task.created_at else None
                }
                for task in tasks
            ],
            "count": len(tasks)
        }

    def _complete_task(self, db: Session, args: dict) -> dict:
        """Mark a task as completed."""
        user_id = args.get("user_id")
        task_id = args.get("task_id")

        task = task_crud.complete(db, user_id, task_id)

        if not task:
            return {
                "task_id": task_id,
                "status": "not_found",
                "error": f"Task {task_id} not found"
            }

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title
        }

    def _delete_task(self, db: Session, args: dict) -> dict:
        """Delete a task."""
        user_id = args.get("user_id")
        task_id = args.get("task_id")

        task = task_crud.delete(db, user_id, task_id)

        if not task:
            return {
                "task_id": task_id,
                "status": "not_found",
                "error": f"Task {task_id} not found"
            }

        return {
            "task_id": task.id,
            "status": "deleted",
            "title": task.title
        }

    def _update_task(self, db: Session, args: dict) -> dict:
        """Update a task."""
        user_id = args.get("user_id")
        task_id = args.get("task_id")
        title = args.get("title")
        description = args.get("description")

        task_data = TaskUpdate(title=title, description=description)
        task = task_crud.update(db, user_id, task_id, task_data)

        if not task:
            return {
                "task_id": task_id,
                "status": "not_found",
                "error": f"Task {task_id} not found"
            }

        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title
        }


# Global MCP server instance
mcp_server = MCPToolServer()


def call_mcp_tool(db: Session, name: str, arguments: dict) -> dict:
    """Convenience function to call an MCP tool."""
    return mcp_server.call_tool(db, name, arguments)
