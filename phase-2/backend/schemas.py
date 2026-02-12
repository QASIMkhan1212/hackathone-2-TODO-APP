"""Pydantic schemas for chat functionality."""
from typing import Optional, List, Any
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str


class ToolCall(BaseModel):
    """Model for a tool call made during chat processing."""
    name: str
    arguments: dict
    result: Any


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    tool_calls: List[ToolCall] = []
