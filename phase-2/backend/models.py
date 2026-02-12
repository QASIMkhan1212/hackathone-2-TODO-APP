from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import field_validator


class TaskBase(SQLModel):
    content: str = Field(index=True, min_length=1, max_length=500)
    completed: bool = Field(default=False)

    @field_validator('content')
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, min_length=1)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    content: Optional[str] = Field(default=None, min_length=1, max_length=500)
    completed: Optional[bool] = None

    @field_validator('content')
    @classmethod
    def content_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip() if v else v
