import logging
import os
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import Task, TaskCreate, TaskUpdate
from security import get_current_user, TokenData
from schemas import ChatRequest, ChatResponse, ToolCall
from agent.todo_agent import todo_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get allowed origins from environment or use defaults
def get_allowed_origins() -> List[str]:
    """Get CORS allowed origins from environment variable or defaults."""
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://[::1]:3000",
    ]
    # Add production frontend URL from environment
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)
    # Add Vercel preview URLs pattern
    better_auth_url = os.getenv("BETTER_AUTH_URL")
    if better_auth_url and better_auth_url not in origins:
        origins.append(better_auth_url)
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    try:
        create_db_and_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.warning(f"Could not connect to database during startup: {type(e).__name__}")
    yield


app = FastAPI(
    title="Q.TODO API",
    description="Task management API with AI assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Content-Length"],
)


def verify_user_access(current_user: TokenData, user_id: str) -> None:
    """Verify that the authenticated user has access to the requested resource."""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")


@app.get("/")
def read_root() -> dict:
    """Health check endpoint."""
    return {"message": "Q.TODO API", "status": "running"}


@app.get("/api/{user_id}/tasks", response_model=List[Task])
def list_tasks(
    user_id: str = Path(..., description="User ID"),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[Task]:
    """List all tasks for a user."""
    verify_user_access(current_user, user_id)
    tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
    return list(tasks)


@app.post("/api/{user_id}/tasks", response_model=Task, status_code=201)
def create_task(
    task: TaskCreate,
    user_id: str = Path(..., description="User ID"),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Task:
    """Create a new task."""
    verify_user_access(current_user, user_id)
    db_task = Task(content=task.content, completed=task.completed, user_id=user_id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.get("/api/{user_id}/tasks/{task_id}", response_model=Task)
def get_task_details(
    task_id: int = Path(..., description="Task ID"),
    user_id: str = Path(..., description="User ID"),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Task:
    """Get details of a specific task."""
    verify_user_access(current_user, user_id)
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/api/{user_id}/tasks/{task_id}", response_model=Task)
def update_task(
    task: TaskUpdate,
    task_id: int = Path(..., description="Task ID"),
    user_id: str = Path(..., description="User ID"),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Task:
    """Update an existing task."""
    verify_user_access(current_user, user_id)
    db_task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    task_data = task.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.delete("/api/{user_id}/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int = Path(..., description="Task ID"),
    user_id: str = Path(..., description="User ID"),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> None:
    """Delete a task."""
    verify_user_access(current_user, user_id)
    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()


@app.patch("/api/{user_id}/tasks/{task_id}/complete", response_model=Task)
def toggle_task_completion(
    task_id: int = Path(..., description="Task ID"),
    user_id: str = Path(..., description="User ID"),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Task:
    """Toggle the completion status of a task."""
    verify_user_access(current_user, user_id)
    db_task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.completed = not db_task.completed
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.post("/api/{user_id}/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    user_id: str = Path(..., description="User ID"),
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> ChatResponse:
    """Process a chat message with the AI assistant."""
    verify_user_access(current_user, user_id)

    try:
        response_text, tool_calls = todo_agent.process_message(
            session=session,
            user_id=user_id,
            message=request.message,
            chat_history=None
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process message")

    formatted_tool_calls = [
        ToolCall(
            name=tc["name"],
            arguments=tc["arguments"],
            result=tc["result"]
        )
        for tc in tool_calls
    ]

    return ChatResponse(
        response=response_text,
        tool_calls=formatted_tool_calls
    )
