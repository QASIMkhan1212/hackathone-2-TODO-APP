from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import Task, TaskCreate, TaskUpdate
from security import get_current_user, TokenData
from schemas import ChatRequest, ChatResponse, ToolCall
from agent.todo_agent import todo_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Try to create tables, but don't fail if database is unavailable
    try:
        create_db_and_tables()
    except Exception as e:
        print(f"Warning: Could not connect to database during startup: {e}")
        print("The database will be initialized on first request.")
    yield


app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow frontend requests
# Allow specific origins with credentials, or all origins without credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://[::1]:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "TaskFlow API", "status": "running"}


@app.get("/api/{user_id}/tasks", response_model=List[Task])
def list_tasks(
    user_id: str,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
    return tasks


@app.post("/api/{user_id}/tasks", response_model=Task, status_code=201)
def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    db_task = Task(content=task.content, completed=task.completed, user_id=user_id)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.get("/api/{user_id}/tasks/{task_id}", response_model=Task)
def get_task_details(
    user_id: str,
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/api/{user_id}/tasks/{task_id}", response_model=Task)
def update_task(
    user_id: str,
    task_id: int,
    task: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

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
    user_id: str,
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    task = session.exec(select(Task).where(Task.id == task_id, Task.user_id == user_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return None


@app.patch("/api/{user_id}/tasks/{task_id}/complete", response_model=Task)
def toggle_task_completion(
    user_id: str,
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

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
    user_id: str,
    request: ChatRequest,
    current_user: TokenData = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Process a chat message and return the AI response.

    Uses Groq LLM with function calling for task management.
    No conversation persistence - fresh chat each session.
    """
    # Verify the user_id matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Process with AI agent (no chat history - stateless)
    try:
        response_text, tool_calls = todo_agent.process_message(
            session=session,
            user_id=user_id,
            message=request.message,
            chat_history=None
        )
    except Exception as e:
        print(f"AI processing error: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

    # Format tool calls for response
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
