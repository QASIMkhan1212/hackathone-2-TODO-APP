"""Common SQLModel patterns for Neon PostgreSQL.

Includes base models, mixins, and common patterns.
"""

from datetime import datetime
from typing import Optional, Any
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, event
from sqlalchemy.dialects.postgresql import JSONB


# =============================================================================
# Mixins
# =============================================================================


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
    )


class SoftDeleteMixin(SQLModel):
    """Mixin for soft delete functionality."""
    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = Field(default=False)


# =============================================================================
# User Models
# =============================================================================


class UserBase(SQLModel):
    """User base schema with shared fields."""
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=100)
    is_active: bool = Field(default=True)


class User(UserBase, TimestampMixin, table=True):
    """User database model."""
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str = Field(max_length=255)
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))


class UserCreate(SQLModel):
    """Schema for creating a user."""
    email: str
    name: str
    password: str = Field(min_length=8)


class UserRead(UserBase):
    """Schema for reading a user (API response)."""
    id: int
    created_at: datetime


class UserUpdate(SQLModel):
    """Schema for updating a user. All fields optional."""
    email: str | None = None
    name: str | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8)


# =============================================================================
# Document Models (for RAG/Vector Search)
# =============================================================================


class DocumentBase(SQLModel):
    """Document base schema."""
    title: str | None = Field(default=None, max_length=500)
    content: str = Field(sa_column=Column(Text, nullable=False))
    source: str | None = Field(default=None, max_length=500)
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))


class Document(DocumentBase, TimestampMixin, table=True):
    """Document database model with optional vector embedding."""
    __tablename__ = "documents"

    id: int | None = Field(default=None, primary_key=True)
    # Add embedding column via migration with pgvector


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    pass


class DocumentRead(DocumentBase):
    """Schema for reading a document."""
    id: int
    created_at: datetime


class DocumentWithScore(DocumentRead):
    """Document with similarity score."""
    similarity: float


# =============================================================================
# API Key Models (for agent authentication)
# =============================================================================


class APIKeyBase(SQLModel):
    """API key base schema."""
    name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    scopes: list[str] = Field(default_factory=list, sa_column=Column(JSONB))


class APIKey(APIKeyBase, TimestampMixin, table=True):
    """API key database model."""
    __tablename__ = "api_keys"

    id: int | None = Field(default=None, primary_key=True)
    key_hash: str = Field(max_length=255, unique=True, index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    last_used_at: datetime | None = Field(default=None)
    expires_at: datetime | None = Field(default=None)


class APIKeyCreate(SQLModel):
    """Schema for creating an API key."""
    name: str
    scopes: list[str] = []
    expires_at: datetime | None = None


class APIKeyRead(APIKeyBase):
    """Schema for reading an API key."""
    id: int
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime | None


# =============================================================================
# Session/Memory Models (for agent state)
# =============================================================================


class AgentSessionBase(SQLModel):
    """Agent session base schema."""
    session_id: str = Field(index=True, max_length=100)
    agent_name: str = Field(max_length=100)
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))


class AgentSession(AgentSessionBase, TimestampMixin, table=True):
    """Agent session for tracking conversations."""
    __tablename__ = "agent_sessions"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    ended_at: datetime | None = Field(default=None)
    total_tokens: int = Field(default=0)
    total_turns: int = Field(default=0)


class AgentMessageBase(SQLModel):
    """Agent message base schema."""
    role: str = Field(max_length=50)  # user, assistant, system, tool
    content: str = Field(sa_column=Column(Text))
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))


class AgentMessage(AgentMessageBase, table=True):
    """Individual message in agent conversation."""
    __tablename__ = "agent_messages"

    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="agent_sessions.id", index=True)
    turn_number: int = Field(default=0)
    tokens: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Add embedding column via migration for semantic search


# =============================================================================
# Audit Log Models
# =============================================================================


class AuditLog(SQLModel, table=True):
    """Audit log for tracking changes."""
    __tablename__ = "audit_logs"

    id: int | None = Field(default=None, primary_key=True)
    table_name: str = Field(max_length=100, index=True)
    record_id: int = Field(index=True)
    action: str = Field(max_length=20)  # INSERT, UPDATE, DELETE
    old_data: dict | None = Field(default=None, sa_column=Column(JSONB))
    new_data: dict | None = Field(default=None, sa_column=Column(JSONB))
    user_id: int | None = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# =============================================================================
# Generic Patterns
# =============================================================================


def create_crud_schemas(
    model_name: str,
    base_fields: dict[str, Any],
    read_extra: dict[str, Any] | None = None,
) -> tuple[type, type, type, type]:
    """
    Dynamically create CRUD schemas for a model.

    Usage:
        Base, Create, Read, Update = create_crud_schemas(
            "Product",
            {"name": (str, ...), "price": (float, ...)},
            {"id": (int, ...), "created_at": (datetime, ...)}
        )
    """
    # This is a simplified example - in practice, use SQLModel directly
    pass


# =============================================================================
# Model Registration
# =============================================================================

# List all models for SQLModel.metadata
__all__ = [
    "User",
    "UserCreate",
    "UserRead",
    "UserUpdate",
    "Document",
    "DocumentCreate",
    "DocumentRead",
    "DocumentWithScore",
    "APIKey",
    "APIKeyCreate",
    "APIKeyRead",
    "AgentSession",
    "AgentMessage",
    "AuditLog",
]
