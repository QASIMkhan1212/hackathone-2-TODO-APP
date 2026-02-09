from datetime import datetime
from pydantic import BaseModel


class MessageCreate(BaseModel):
    role: str
    content: str


class MessageResponse(BaseModel):
    id: int
    user_id: str
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
