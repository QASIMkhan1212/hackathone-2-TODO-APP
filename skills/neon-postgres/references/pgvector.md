# pgvector Reference

## Overview

pgvector is a PostgreSQL extension for vector similarity search, enabling AI applications like semantic search, recommendations, and RAG (Retrieval-Augmented Generation).

## Setup

```sql
-- Enable the extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
```

## Vector Data Types

```sql
-- Fixed dimension vector
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    embedding vector(1536)  -- OpenAI text-embedding-3-small
);

-- Common embedding dimensions:
-- OpenAI text-embedding-3-small: 1536
-- OpenAI text-embedding-3-large: 3072
-- Cohere embed-v3: 1024
-- sentence-transformers: 384-768
-- Anthropic: 1024
```

## Creating Tables

### Basic Document Table

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### With SQLModel/SQLAlchemy

```python
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector

class Document(SQLModel, table=True):
    __tablename__ = "documents"

    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Column(Text, nullable=False))
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(1536))
    )
```

## Indexing Strategies

### IVFFlat Index

Best for: Memory-constrained environments, large datasets

```sql
-- Create IVFFlat index
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Guideline: lists = sqrt(row_count)
-- 1M rows → lists = 1000
-- 100K rows → lists = 316
```

**Operators for IVFFlat:**
- `vector_l2_ops` - Euclidean distance (L2)
- `vector_ip_ops` - Inner product
- `vector_cosine_ops` - Cosine distance

### HNSW Index

Best for: Fast queries, production workloads

```sql
-- Create HNSW index
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Parameters:
-- m: Max connections per layer (default 16, higher = more accurate, more memory)
-- ef_construction: Build-time candidate list size (default 64, higher = better quality)
```

### Index Selection Guide

| Factor | IVFFlat | HNSW |
|--------|---------|------|
| Query Speed | Good | Excellent |
| Build Speed | Fast | Slow |
| Memory Usage | Low | High |
| Recall | Good | Excellent |
| Updates | Requires rebuild | Incremental |

## Distance Functions

```sql
-- L2 (Euclidean) distance - lower is better
SELECT * FROM documents
ORDER BY embedding <-> '[0.1, 0.2, ...]'::vector
LIMIT 10;

-- Inner product - higher is better (negate for ORDER BY)
SELECT * FROM documents
ORDER BY embedding <#> '[0.1, 0.2, ...]'::vector
LIMIT 10;

-- Cosine distance - lower is better (0 = identical)
SELECT * FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;

-- Cosine similarity (1 - cosine distance)
SELECT
    content,
    1 - (embedding <=> '[0.1, 0.2, ...]'::vector) as similarity
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;
```

## Query Patterns

### Basic Similarity Search

```python
from sqlmodel import select

async def similarity_search(
    session: AsyncSession,
    query_embedding: list[float],
    limit: int = 10,
) -> list[Document]:
    """Find most similar documents."""
    statement = (
        select(Document)
        .order_by(Document.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()
```

### With Similarity Score

```python
from sqlalchemy import func, literal

async def search_with_score(
    session: AsyncSession,
    query_embedding: list[float],
    limit: int = 10,
) -> list[tuple[Document, float]]:
    """Search with similarity scores."""
    distance = Document.embedding.cosine_distance(query_embedding)
    similarity = (1 - distance).label("similarity")

    statement = (
        select(Document, similarity)
        .order_by(distance)
        .limit(limit)
    )
    result = await session.execute(statement)
    return result.all()
```

### Filtered Search

```python
async def filtered_search(
    session: AsyncSession,
    query_embedding: list[float],
    category: str,
    min_date: datetime,
    limit: int = 10,
) -> list[Document]:
    """Search with metadata filters."""
    statement = (
        select(Document)
        .where(Document.metadata["category"].astext == category)
        .where(Document.created_at >= min_date)
        .order_by(Document.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()
```

### Threshold-Based Search

```python
async def threshold_search(
    session: AsyncSession,
    query_embedding: list[float],
    threshold: float = 0.8,  # Minimum similarity
    limit: int = 100,
) -> list[Document]:
    """Only return results above similarity threshold."""
    # Cosine distance threshold (1 - similarity)
    distance_threshold = 1 - threshold

    statement = (
        select(Document)
        .where(
            Document.embedding.cosine_distance(query_embedding) < distance_threshold
        )
        .order_by(Document.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()
```

### Hybrid Search (Vector + Full-Text)

```sql
-- Create full-text search index
CREATE INDEX ON documents USING gin(to_tsvector('english', content));

-- Hybrid search query
WITH semantic AS (
    SELECT
        id,
        content,
        1 - (embedding <=> $1::vector) as semantic_score,
        ROW_NUMBER() OVER (ORDER BY embedding <=> $1::vector) as semantic_rank
    FROM documents
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> $1::vector
    LIMIT 20
),
fulltext AS (
    SELECT
        id,
        content,
        ts_rank_cd(to_tsvector('english', content), plainto_tsquery('english', $2)) as text_score,
        ROW_NUMBER() OVER (ORDER BY ts_rank_cd(to_tsvector('english', content), plainto_tsquery('english', $2)) DESC) as text_rank
    FROM documents
    WHERE to_tsvector('english', content) @@ plainto_tsquery('english', $2)
    LIMIT 20
)
SELECT
    COALESCE(s.id, f.id) as id,
    COALESCE(s.content, f.content) as content,
    COALESCE(s.semantic_score, 0) as semantic_score,
    COALESCE(f.text_score, 0) as text_score,
    -- RRF (Reciprocal Rank Fusion) scoring
    COALESCE(1.0 / (60 + s.semantic_rank), 0) +
    COALESCE(1.0 / (60 + f.text_rank), 0) as rrf_score
FROM semantic s
FULL OUTER JOIN fulltext f ON s.id = f.id
ORDER BY rrf_score DESC
LIMIT 10;
```

## Embedding Generation

### OpenAI

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """Generate embedding using OpenAI."""
    response = await client.embeddings.create(
        model=model,
        input=text,
    )
    return response.data[0].embedding


async def get_embeddings_batch(
    texts: list[str],
    model: str = "text-embedding-3-small"
) -> list[list[float]]:
    """Generate embeddings for multiple texts."""
    response = await client.embeddings.create(
        model=model,
        input=texts,
    )
    return [item.embedding for item in response.data]
```

### Local Models (sentence-transformers)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding_local(text: str) -> list[float]:
    """Generate embedding using local model."""
    embedding = model.encode(text)
    return embedding.tolist()
```

## Performance Tuning

### Set Search Parameters

```sql
-- For IVFFlat: increase probes for better recall
SET ivfflat.probes = 10;  -- Default is 1

-- For HNSW: increase ef_search for better recall
SET hnsw.ef_search = 100;  -- Default is 40
```

### In Application

```python
async def search_with_tuned_params(
    session: AsyncSession,
    query_embedding: list[float],
    probes: int = 10,
) -> list[Document]:
    """Search with tuned parameters."""
    # Set search parameters for this session
    await session.execute(text(f"SET ivfflat.probes = {probes}"))

    statement = (
        select(Document)
        .order_by(Document.embedding.cosine_distance(query_embedding))
        .limit(10)
    )
    result = await session.exec(statement)
    return result.all()
```

### Maintenance

```sql
-- Reindex after significant data changes (IVFFlat)
REINDEX INDEX documents_embedding_idx;

-- Analyze for query planner
ANALYZE documents;

-- Check index size
SELECT pg_size_pretty(pg_relation_size('documents_embedding_idx'));
```

## Best Practices

1. **Choose Right Dimensions**: Use smaller models when possible (1536 vs 3072)
2. **Batch Embeddings**: Generate embeddings in batches to reduce API calls
3. **Index After Bulk Load**: Create index after inserting large datasets
4. **Monitor Recall**: Test recall vs speed tradeoffs with your data
5. **Use HNSW for Production**: Better query performance
6. **Normalize Vectors**: Some models require normalized vectors
7. **Partition Large Tables**: Consider partitioning for very large datasets
