from typing import Optional, List, Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ToolCall(BaseModel):
    name: str
    arguments: dict
    result: Any


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: List[ToolCall] = []
