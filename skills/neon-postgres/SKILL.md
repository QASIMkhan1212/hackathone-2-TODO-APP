---
name: neon-postgres
description: Neon serverless PostgreSQL for modern applications and AI agents. Use when users want to (1) set up serverless PostgreSQL databases, (2) implement database branching for development, (3) add vector search with pgvector, (4) build agent memory systems, (5) configure connection pooling for serverless, (6) implement RAG pipelines, (7) manage database migrations. Triggers on mentions of "neon", "serverless postgres", "pgvector", "database branching", "agent memory", "vector embeddings", or PostgreSQL for AI applications.
---

# Neon PostgreSQL

Serverless PostgreSQL platform with branching, autoscaling, and AI-native features for modern applications and agentic workflows.

## When to Use This Skill

- Setting up serverless PostgreSQL databases
- Implementing database branching workflows
- Adding vector search capabilities (pgvector)
- Building agent memory and context storage
- Configuring connection pooling for serverless
- Implementing RAG (Retrieval-Augmented Generation)
- Managing schema migrations with branching

## Core Concepts

### 1. Neon Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Neon Platform                     │
├─────────────────────────────────────────────────────┤
│  Compute Layer (Stateless)                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Branch  │  │ Branch  │  │ Branch  │            │
│  │  main   │  │  dev    │  │ feature │            │
│  └────┬────┘  └────┬────┘  └────┬────┘            │
│       │            │            │                  │
├───────┴────────────┴────────────┴──────────────────┤
│  Storage Layer (Shared, Copy-on-Write)              │
│  ┌─────────────────────────────────────────────┐   │
│  │           Pageserver + Safekeepers           │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 2. Connection Setup

```python
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Neon connection string format:
# postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require

DATABASE_URL = os.getenv("DATABASE_URL")

# For serverless (recommended): disable SQLAlchemy pooling
# Neon has built-in connection pooling via pgBouncer
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Let Neon handle pooling
    echo=False,
)

# Session factory
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)
```

### 3. Connection Pooling Options

```python
# Option 1: Direct connection (for long-running processes)
# Use: postgresql://user:pass@ep-xxx.neon.tech/db

# Option 2: Pooled connection (for serverless/edge)
# Use: postgresql://user:pass@ep-xxx.neon.tech/db?pgbouncer=true

# Option 3: Pooled with transaction mode
POOLED_URL = os.getenv("DATABASE_URL").replace(
    ".neon.tech",
    "-pooler.neon.tech"
)

# Connection string examples:
DIRECT_URL = "postgresql://user:pass@ep-cool-forest-123.us-east-1.aws.neon.tech/mydb"
POOLED_URL = "postgresql://user:pass@ep-cool-forest-123-pooler.us-east-1.aws.neon.tech/mydb"
```

### 4. Database Branching

Neon branches are instant, copy-on-write database copies:

```python
import httpx

NEON_API_KEY = os.getenv("NEON_API_KEY")
PROJECT_ID = os.getenv("NEON_PROJECT_ID")

async def create_branch(
    branch_name: str,
    parent_branch: str = "main"
) -> dict:
    """Create a new database branch."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://console.neon.tech/api/v2/projects/{PROJECT_ID}/branches",
            headers={"Authorization": f"Bearer {NEON_API_KEY}"},
            json={
                "branch": {
                    "name": branch_name,
                    "parent_id": parent_branch,
                },
                "endpoints": [{"type": "read_write"}],
            },
        )
        return response.json()

async def delete_branch(branch_id: str) -> bool:
    """Delete a database branch."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"https://console.neon.tech/api/v2/projects/{PROJECT_ID}/branches/{branch_id}",
            headers={"Authorization": f"Bearer {NEON_API_KEY}"},
        )
        return response.status_code == 204
```

### 5. pgvector for AI/Embeddings

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table with vector column
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),  -- OpenAI ada-002 dimension
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for fast similarity search
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Or use HNSW index (faster queries, slower builds)
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text
from pgvector.sqlalchemy import Vector

class Document(SQLModel, table=True):
    """Document with vector embedding."""
    __tablename__ = "documents"

    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Column(Text))
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(1536))
    )
```

### 6. Vector Search Queries

```python
from sqlmodel import select
from sqlalchemy import text

async def semantic_search(
    session: AsyncSession,
    query_embedding: list[float],
    limit: int = 10,
    threshold: float = 0.7,
) -> list[Document]:
    """Find similar documents using cosine similarity."""

    # Method 1: Using SQLAlchemy
    statement = (
        select(Document)
        .order_by(Document.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()

async def hybrid_search(
    session: AsyncSession,
    query: str,
    query_embedding: list[float],
    limit: int = 10,
) -> list[dict]:
    """Combine full-text and vector search."""

    sql = text("""
        WITH semantic AS (
            SELECT id, content, metadata,
                   1 - (embedding <=> :embedding::vector) as semantic_score
            FROM documents
            ORDER BY embedding <=> :embedding::vector
            LIMIT :limit * 2
        ),
        fulltext AS (
            SELECT id, content, metadata,
                   ts_rank(to_tsvector('english', content),
                          plainto_tsquery('english', :query)) as text_score
            FROM documents
            WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :query)
            LIMIT :limit * 2
        )
        SELECT COALESCE(s.id, f.id) as id,
               COALESCE(s.content, f.content) as content,
               COALESCE(s.metadata, f.metadata) as metadata,
               COALESCE(s.semantic_score, 0) * 0.7 +
               COALESCE(f.text_score, 0) * 0.3 as combined_score
        FROM semantic s
        FULL OUTER JOIN fulltext f ON s.id = f.id
        ORDER BY combined_score DESC
        LIMIT :limit
    """)

    result = await session.execute(
        sql,
        {"embedding": query_embedding, "query": query, "limit": limit}
    )
    return [dict(row) for row in result.fetchall()]
```

### 7. Agent Memory System

```python
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

class AgentMemory(SQLModel, table=True):
    """Store agent conversation memory."""
    __tablename__ = "agent_memories"

    id: int | None = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    agent_name: str
    role: str  # "user", "assistant", "system", "tool"
    content: str
    metadata: dict = Field(default_factory=dict)
    embedding: list[float] | None = Field(default=None, sa_column=Column(Vector(1536)))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentMemoryStore:
    """Memory store for AI agents."""

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def add_memory(
        self,
        session_id: str,
        agent_name: str,
        role: str,
        content: str,
        embedding: list[float] | None = None,
        metadata: dict | None = None,
    ) -> AgentMemory:
        """Add a memory entry."""
        async with self.session_factory() as session:
            memory = AgentMemory(
                session_id=session_id,
                agent_name=agent_name,
                role=role,
                content=content,
                embedding=embedding,
                metadata=metadata or {},
            )
            session.add(memory)
            await session.commit()
            await session.refresh(memory)
            return memory

    async def get_recent_memories(
        self,
        session_id: str,
        limit: int = 20,
    ) -> list[AgentMemory]:
        """Get recent memories for a session."""
        async with self.session_factory() as session:
            statement = (
                select(AgentMemory)
                .where(AgentMemory.session_id == session_id)
                .order_by(AgentMemory.created_at.desc())
                .limit(limit)
            )
            result = await session.exec(statement)
            return list(reversed(result.all()))

    async def search_memories(
        self,
        session_id: str,
        query_embedding: list[float],
        limit: int = 5,
    ) -> list[AgentMemory]:
        """Search memories by semantic similarity."""
        async with self.session_factory() as session:
            statement = (
                select(AgentMemory)
                .where(AgentMemory.session_id == session_id)
                .where(AgentMemory.embedding.is_not(None))
                .order_by(AgentMemory.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )
            result = await session.exec(statement)
            return result.all()

    async def clear_session(self, session_id: str) -> int:
        """Clear all memories for a session."""
        async with self.session_factory() as session:
            statement = (
                delete(AgentMemory)
                .where(AgentMemory.session_id == session_id)
            )
            result = await session.execute(statement)
            await session.commit()
            return result.rowcount
```

### 8. RAG Pipeline

```python
from openai import AsyncOpenAI

openai_client = AsyncOpenAI()

async def get_embedding(text: str) -> list[float]:
    """Generate embedding using OpenAI."""
    response = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


async def rag_query(
    session: AsyncSession,
    query: str,
    system_prompt: str = "Answer based on the provided context.",
    top_k: int = 5,
) -> str:
    """RAG: Retrieve context and generate response."""

    # 1. Generate query embedding
    query_embedding = await get_embedding(query)

    # 2. Retrieve relevant documents
    docs = await semantic_search(session, query_embedding, limit=top_k)

    # 3. Build context
    context = "\n\n".join([
        f"Document {i+1}:\n{doc.content}"
        for i, doc in enumerate(docs)
    ])

    # 4. Generate response
    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
        ],
    )

    return response.choices[0].message.content


async def ingest_document(
    session: AsyncSession,
    content: str,
    metadata: dict | None = None,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[Document]:
    """Ingest document with chunking and embedding."""

    # Simple chunking (use langchain or similar for production)
    chunks = []
    for i in range(0, len(content), chunk_size - chunk_overlap):
        chunk = content[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)

    # Generate embeddings and store
    documents = []
    for chunk in chunks:
        embedding = await get_embedding(chunk)
        doc = Document(
            content=chunk,
            metadata=metadata or {},
            embedding=embedding,
        )
        session.add(doc)
        documents.append(doc)

    await session.commit()
    return documents
```

## Neon MCP Server

Configure Neon MCP server for AI agents:

```json
{
  "mcpServers": {
    "neon": {
      "command": "npx",
      "args": ["-y", "@neondatabase/mcp-server-neon"],
      "env": {
        "NEON_API_KEY": "your-neon-api-key"
      }
    }
  }
}
```

### MCP Server Capabilities

- `list_projects` - List all Neon projects
- `create_project` - Create new project
- `create_branch` - Create database branch
- `run_sql` - Execute SQL queries
- `get_connection_string` - Get connection details
- `describe_table` - Get table schema

## Branch-Based Development Workflow

```
main (production)
  │
  ├── staging
  │     │
  │     └── feature/user-auth
  │           │
  │           └── test/user-auth-unit
  │
  └── dev
        │
        ├── feature/payments
        └── feature/notifications
```

```python
# Development workflow
async def feature_branch_workflow():
    # 1. Create feature branch from main
    branch = await create_branch("feature/new-feature", parent="main")

    # 2. Get connection string for branch
    conn_string = branch["endpoints"][0]["connection_uri"]

    # 3. Developer works on branch...
    # 4. Run tests against branch
    # 5. Merge = apply migrations to main

    # 6. Delete branch after merge
    await delete_branch(branch["id"])
```

## Environment Variables

```bash
# Neon connection
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require

# Pooled connection (for serverless)
DATABASE_URL_POOLED=postgresql://user:pass@ep-xxx-pooler.neon.tech/dbname?sslmode=require

# Neon API (for branching)
NEON_API_KEY=neon_api_key_xxx
NEON_PROJECT_ID=project-xxx

# OpenAI (for embeddings)
OPENAI_API_KEY=sk-xxx
```

## Installation

```bash
# Core dependencies
pip install sqlmodel asyncpg sqlalchemy[asyncio]

# For pgvector
pip install pgvector

# For Neon API
pip install httpx

# For embeddings
pip install openai
```

## Best Practices

1. **Use Pooled Connections**: For serverless/edge, always use `-pooler` endpoint
2. **Enable pgvector Early**: Add extension before creating tables
3. **Index Vectors**: Use HNSW for fast queries, IVFFlat for memory efficiency
4. **Branch for Features**: Create branches for isolated development
5. **Chunk Documents**: Split large documents for better retrieval
6. **Hybrid Search**: Combine vector + full-text for best results
7. **Monitor Compute**: Use scale-to-zero for cost optimization

## References

- See `references/branching.md` for branch workflow patterns
- See `references/pgvector.md` for vector search optimization
- See `references/connection-pooling.md` for serverless setup
- See `references/migrations.md` for schema migration strategies

## Scripts

- `scripts/setup_neon.py` - Initialize Neon project and database
- `scripts/generate_migrations.py` - Generate Alembic migrations
- `scripts/setup_pgvector.py` - Configure pgvector extension

## Assets

- `assets/database.py` - Database connection template
- `assets/models.py` - Common model patterns
- `assets/agent_memory.py` - Agent memory store implementation
- `assets/vector_search.py` - Vector search utilities
