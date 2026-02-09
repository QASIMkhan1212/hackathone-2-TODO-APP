from typing import Optional
from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    content: str = Field(index=True)
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # Better Auth uses string UUIDs for user IDs


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    content: Optional[str] = None
    completed: Optional[bool] = None
