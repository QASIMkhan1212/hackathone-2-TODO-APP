"""Agent memory store for AI agents using Neon PostgreSQL.

Provides persistent memory storage with semantic search capabilities.
"""

from datetime import datetime
from typing import Optional, Any
from sqlmodel import SQLModel, Field, Column, select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import Text, func
from sqlalchemy.dialects.postgresql import JSONB

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    Vector = None


# =============================================================================
# Memory Models
# =============================================================================


class AgentMemory(SQLModel, table=True):
    """Store agent conversation memory with optional embeddings."""
    __tablename__ = "agent_memories"

    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, max_length=100)
    agent_name: str = Field(max_length=100)
    role: str = Field(max_length=50)  # user, assistant, system, tool
    content: str = Field(sa_column=Column(Text, nullable=False))
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    turn_number: int = Field(default=0)
    tokens: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Note: Add embedding column via migration:
    # embedding: list[float] | None = Field(
    #     default=None,
    #     sa_column=Column(Vector(1536))
    # )


class MemoryCreate(SQLModel):
    """Schema for creating a memory entry."""
    session_id: str
    agent_name: str
    role: str
    content: str
    metadata: dict = {}
    turn_number: int = 0
    tokens: int = 0


class MemoryRead(SQLModel):
    """Schema for reading a memory entry."""
    id: int
    session_id: str
    agent_name: str
    role: str
    content: str
    metadata: dict
    turn_number: int
    tokens: int
    created_at: datetime


class MemoryWithScore(MemoryRead):
    """Memory with similarity score."""
    similarity: float


# =============================================================================
# Memory Store
# =============================================================================


class AgentMemoryStore:
    """
    Memory store for AI agents with semantic search.

    Usage:
        store = AgentMemoryStore(session_factory)

        # Add memory
        await store.add_memory(
            session_id="conv_123",
            agent_name="Assistant",
            role="user",
            content="Hello, how are you?",
        )

        # Get recent memories
        memories = await store.get_recent(session_id="conv_123", limit=20)

        # Search memories semantically
        results = await store.search(
            session_id="conv_123",
            query_embedding=embedding,
            limit=5,
        )
    """

    def __init__(self, session_factory):
        """
        Initialize memory store.

        Args:
            session_factory: Async session factory from database.py
        """
        self.session_factory = session_factory

    async def add_memory(
        self,
        session_id: str,
        agent_name: str,
        role: str,
        content: str,
        metadata: dict | None = None,
        turn_number: int = 0,
        tokens: int = 0,
        embedding: list[float] | None = None,
    ) -> AgentMemory:
        """
        Add a memory entry.

        Args:
            session_id: Unique session identifier
            agent_name: Name of the agent
            role: Message role (user, assistant, system, tool)
            content: Message content
            metadata: Optional metadata dict
            turn_number: Conversation turn number
            tokens: Token count for the message
            embedding: Optional embedding vector

        Returns:
            Created memory entry
        """
        async with self.session_factory() as session:
            memory = AgentMemory(
                session_id=session_id,
                agent_name=agent_name,
                role=role,
                content=content,
                metadata=metadata or {},
                turn_number=turn_number,
                tokens=tokens,
            )

            # Add embedding if provided and column exists
            if embedding and hasattr(memory, 'embedding'):
                memory.embedding = embedding

            session.add(memory)
            await session.commit()
            await session.refresh(memory)
            return memory

    async def add_memories_batch(
        self,
        memories: list[MemoryCreate],
        embeddings: list[list[float]] | None = None,
    ) -> list[AgentMemory]:
        """
        Add multiple memory entries in batch.

        Args:
            memories: List of memory create schemas
            embeddings: Optional list of embeddings (same length as memories)

        Returns:
            List of created memory entries
        """
        async with self.session_factory() as session:
            db_memories = []
            for i, mem in enumerate(memories):
                memory = AgentMemory(**mem.model_dump())
                if embeddings and i < len(embeddings) and hasattr(memory, 'embedding'):
                    memory.embedding = embeddings[i]
                session.add(memory)
                db_memories.append(memory)

            await session.commit()
            for memory in db_memories:
                await session.refresh(memory)
            return db_memories

    async def get_recent(
        self,
        session_id: str,
        limit: int = 20,
        agent_name: str | None = None,
        roles: list[str] | None = None,
    ) -> list[AgentMemory]:
        """
        Get recent memories for a session.

        Args:
            session_id: Session identifier
            limit: Maximum memories to return
            agent_name: Optional filter by agent
            roles: Optional filter by roles

        Returns:
            List of memories (oldest first for context building)
        """
        async with self.session_factory() as session:
            statement = (
                select(AgentMemory)
                .where(AgentMemory.session_id == session_id)
            )

            if agent_name:
                statement = statement.where(AgentMemory.agent_name == agent_name)

            if roles:
                statement = statement.where(AgentMemory.role.in_(roles))

            statement = (
                statement
                .order_by(AgentMemory.created_at.desc())
                .limit(limit)
            )

            result = await session.exec(statement)
            # Reverse to get chronological order
            return list(reversed(result.all()))

    async def search(
        self,
        session_id: str,
        query_embedding: list[float],
        limit: int = 5,
        threshold: float | None = None,
    ) -> list[MemoryWithScore]:
        """
        Search memories by semantic similarity.

        Args:
            session_id: Session identifier
            query_embedding: Query vector
            limit: Maximum results
            threshold: Minimum similarity (0-1)

        Returns:
            Memories with similarity scores
        """
        async with self.session_factory() as session:
            # Check if embedding column exists
            if not HAS_PGVECTOR:
                raise RuntimeError("pgvector not installed")

            distance = AgentMemory.embedding.cosine_distance(query_embedding)
            similarity = (1 - distance).label("similarity")

            statement = (
                select(AgentMemory, similarity)
                .where(AgentMemory.session_id == session_id)
                .where(AgentMemory.embedding.is_not(None))
                .order_by(distance)
                .limit(limit)
            )

            if threshold:
                statement = statement.where(distance < (1 - threshold))

            result = await session.execute(statement)
            return [
                MemoryWithScore(
                    **mem.model_dump(),
                    similarity=float(score)
                )
                for mem, score in result.all()
            ]

    async def get_context(
        self,
        session_id: str,
        query_embedding: list[float] | None = None,
        recent_limit: int = 10,
        semantic_limit: int = 5,
    ) -> list[AgentMemory]:
        """
        Get context for an agent: recent + semantically relevant memories.

        Args:
            session_id: Session identifier
            query_embedding: Optional query for semantic search
            recent_limit: Number of recent memories
            semantic_limit: Number of semantic matches

        Returns:
            Combined context memories (deduplicated, chronological)
        """
        # Get recent memories
        recent = await self.get_recent(session_id, limit=recent_limit)
        recent_ids = {m.id for m in recent}

        # Add semantic matches if embedding provided
        if query_embedding:
            try:
                semantic = await self.search(
                    session_id,
                    query_embedding,
                    limit=semantic_limit,
                )
                # Add non-duplicate semantic matches
                for mem in semantic:
                    if mem.id not in recent_ids:
                        recent.append(AgentMemory(**mem.model_dump(exclude={"similarity"})))
                        recent_ids.add(mem.id)
            except Exception:
                pass  # Skip if pgvector not available

        # Sort by creation time
        recent.sort(key=lambda m: m.created_at)
        return recent

    async def count(
        self,
        session_id: str,
        agent_name: str | None = None,
    ) -> int:
        """Count memories in a session."""
        async with self.session_factory() as session:
            statement = select(func.count(AgentMemory.id)).where(
                AgentMemory.session_id == session_id
            )
            if agent_name:
                statement = statement.where(AgentMemory.agent_name == agent_name)

            result = await session.execute(statement)
            return result.scalar() or 0

    async def get_token_count(self, session_id: str) -> int:
        """Get total tokens used in a session."""
        async with self.session_factory() as session:
            statement = select(func.sum(AgentMemory.tokens)).where(
                AgentMemory.session_id == session_id
            )
            result = await session.execute(statement)
            return result.scalar() or 0

    async def clear_session(self, session_id: str) -> int:
        """
        Clear all memories for a session.

        Returns:
            Number of deleted memories
        """
        async with self.session_factory() as session:
            statement = delete(AgentMemory).where(
                AgentMemory.session_id == session_id
            )
            result = await session.execute(statement)
            await session.commit()
            return result.rowcount

    async def delete_old_memories(
        self,
        older_than: datetime,
        session_id: str | None = None,
    ) -> int:
        """
        Delete memories older than specified date.

        Args:
            older_than: Delete memories before this date
            session_id: Optional filter by session

        Returns:
            Number of deleted memories
        """
        async with self.session_factory() as session:
            statement = delete(AgentMemory).where(
                AgentMemory.created_at < older_than
            )
            if session_id:
                statement = statement.where(AgentMemory.session_id == session_id)

            result = await session.execute(statement)
            await session.commit()
            return result.rowcount


# =============================================================================
# Convenience Functions
# =============================================================================


def create_memory_store(session_factory) -> AgentMemoryStore:
    """Create a memory store instance."""
    return AgentMemoryStore(session_factory)


async def format_memories_for_prompt(
    memories: list[AgentMemory],
    include_metadata: bool = False,
) -> str:
    """
    Format memories as a string for LLM context.

    Args:
        memories: List of memories
        include_metadata: Include metadata in output

    Returns:
        Formatted conversation string
    """
    lines = []
    for mem in memories:
        role = mem.role.capitalize()
        content = mem.content

        if include_metadata and mem.metadata:
            meta_str = ", ".join(f"{k}={v}" for k, v in mem.metadata.items())
            lines.append(f"[{role}] ({meta_str}): {content}")
        else:
            lines.append(f"[{role}]: {content}")

    return "\n".join(lines)
