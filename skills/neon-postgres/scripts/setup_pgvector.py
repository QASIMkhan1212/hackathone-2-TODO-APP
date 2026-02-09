#!/usr/bin/env python3
"""Set up pgvector for vector similarity search."""

import argparse
from pathlib import Path


def generate_vector_models() -> str:
    """Generate SQLModel models with vector support."""
    return '''"""Vector-enabled models for semantic search."""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector


class Document(SQLModel, table=True):
    """Document with vector embedding for semantic search."""
    __tablename__ = "documents"

    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(sa_column=Column(Text, nullable=False))
    title: str | None = Field(default=None, max_length=500)
    source: str | None = Field(default=None, max_length=500)
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(1536))  # OpenAI text-embedding-3-small
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentCreate(SQLModel):
    """Schema for creating a document."""
    content: str
    title: str | None = None
    source: str | None = None
    metadata: dict = {}


class DocumentRead(SQLModel):
    """Schema for reading a document."""
    id: int
    content: str
    title: str | None
    source: str | None
    metadata: dict
    created_at: datetime


class DocumentWithScore(DocumentRead):
    """Document with similarity score."""
    similarity: float


class Chunk(SQLModel, table=True):
    """Text chunk with embedding for RAG."""
    __tablename__ = "chunks"

    id: int | None = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="documents.id", index=True)
    content: str = Field(sa_column=Column(Text, nullable=False))
    chunk_index: int = Field(default=0)
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    embedding: list[float] | None = Field(
        default=None,
        sa_column=Column(Vector(1536))
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
'''


def generate_vector_search() -> str:
    """Generate vector search utilities."""
    return '''"""Vector search utilities for pgvector."""

from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text, func

from .vector_models import Document, Chunk, DocumentWithScore


class VectorSearch:
    """Vector similarity search operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def similarity_search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        threshold: float | None = None,
    ) -> list[DocumentWithScore]:
        """
        Find similar documents using cosine similarity.

        Args:
            query_embedding: Query vector
            limit: Maximum results
            threshold: Minimum similarity (0-1)

        Returns:
            Documents with similarity scores
        """
        distance = Document.embedding.cosine_distance(query_embedding)
        similarity = (1 - distance).label("similarity")

        statement = (
            select(Document, similarity)
            .where(Document.embedding.is_not(None))
            .order_by(distance)
            .limit(limit)
        )

        if threshold:
            statement = statement.where(distance < (1 - threshold))

        result = await self.session.execute(statement)
        return [
            DocumentWithScore(
                **doc.model_dump(),
                similarity=float(score)
            )
            for doc, score in result.all()
        ]

    async def filtered_search(
        self,
        query_embedding: list[float],
        filters: dict,
        limit: int = 10,
    ) -> list[DocumentWithScore]:
        """
        Search with metadata filters.

        Args:
            query_embedding: Query vector
            filters: JSONB filters (e.g., {"category": "tech"})
            limit: Maximum results

        Returns:
            Filtered documents with scores
        """
        distance = Document.embedding.cosine_distance(query_embedding)
        similarity = (1 - distance).label("similarity")

        statement = (
            select(Document, similarity)
            .where(Document.embedding.is_not(None))
        )

        # Apply JSONB filters
        for key, value in filters.items():
            statement = statement.where(
                Document.metadata[key].astext == str(value)
            )

        statement = statement.order_by(distance).limit(limit)

        result = await self.session.execute(statement)
        return [
            DocumentWithScore(**doc.model_dump(), similarity=float(score))
            for doc, score in result.all()
        ]

    async def hybrid_search(
        self,
        query: str,
        query_embedding: list[float],
        limit: int = 10,
        semantic_weight: float = 0.7,
    ) -> list[DocumentWithScore]:
        """
        Combine vector and full-text search using RRF.

        Args:
            query: Text query for full-text search
            query_embedding: Query vector for semantic search
            limit: Maximum results
            semantic_weight: Weight for semantic vs text (0-1)

        Returns:
            Documents ranked by combined score
        """
        text_weight = 1 - semantic_weight
        k = 60  # RRF constant

        sql = text("""
            WITH semantic AS (
                SELECT
                    id,
                    content,
                    title,
                    source,
                    metadata,
                    created_at,
                    1 - (embedding <=> :embedding::vector) as semantic_score,
                    ROW_NUMBER() OVER (ORDER BY embedding <=> :embedding::vector) as semantic_rank
                FROM documents
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> :embedding::vector
                LIMIT :limit * 3
            ),
            fulltext AS (
                SELECT
                    id,
                    content,
                    title,
                    source,
                    metadata,
                    created_at,
                    ts_rank_cd(
                        to_tsvector('english', content),
                        plainto_tsquery('english', :query)
                    ) as text_score,
                    ROW_NUMBER() OVER (
                        ORDER BY ts_rank_cd(
                            to_tsvector('english', content),
                            plainto_tsquery('english', :query)
                        ) DESC
                    ) as text_rank
                FROM documents
                WHERE to_tsvector('english', content) @@ plainto_tsquery('english', :query)
                LIMIT :limit * 3
            )
            SELECT
                COALESCE(s.id, f.id) as id,
                COALESCE(s.content, f.content) as content,
                COALESCE(s.title, f.title) as title,
                COALESCE(s.source, f.source) as source,
                COALESCE(s.metadata, f.metadata) as metadata,
                COALESCE(s.created_at, f.created_at) as created_at,
                (
                    COALESCE(:semantic_weight / (:k + s.semantic_rank), 0) +
                    COALESCE(:text_weight / (:k + f.text_rank), 0)
                ) as similarity
            FROM semantic s
            FULL OUTER JOIN fulltext f ON s.id = f.id
            ORDER BY similarity DESC
            LIMIT :limit
        """)

        result = await self.session.execute(
            sql,
            {
                "embedding": query_embedding,
                "query": query,
                "limit": limit,
                "semantic_weight": semantic_weight,
                "text_weight": text_weight,
                "k": k,
            }
        )

        return [
            DocumentWithScore(
                id=row.id,
                content=row.content,
                title=row.title,
                source=row.source,
                metadata=row.metadata,
                created_at=row.created_at,
                similarity=float(row.similarity),
            )
            for row in result.fetchall()
        ]

    async def chunk_search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        document_id: int | None = None,
    ) -> list[Chunk]:
        """
        Search chunks for RAG.

        Args:
            query_embedding: Query vector
            limit: Maximum results
            document_id: Optional filter by document

        Returns:
            Most relevant chunks
        """
        statement = (
            select(Chunk)
            .where(Chunk.embedding.is_not(None))
            .order_by(Chunk.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        if document_id:
            statement = statement.where(Chunk.document_id == document_id)

        result = await self.session.exec(statement)
        return result.all()
'''


def generate_embedding_utils() -> str:
    """Generate embedding generation utilities."""
    return '''"""Embedding generation utilities."""

import os
from typing import Optional
from openai import AsyncOpenAI

# Initialize OpenAI client
_client: Optional[AsyncOpenAI] = None


def get_openai_client() -> AsyncOpenAI:
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


async def get_embedding(
    text: str,
    model: str = "text-embedding-3-small",
) -> list[float]:
    """
    Generate embedding for text using OpenAI.

    Args:
        text: Text to embed
        model: Embedding model

    Returns:
        Embedding vector
    """
    client = get_openai_client()
    response = await client.embeddings.create(
        model=model,
        input=text,
    )
    return response.data[0].embedding


async def get_embeddings_batch(
    texts: list[str],
    model: str = "text-embedding-3-small",
    batch_size: int = 100,
) -> list[list[float]]:
    """
    Generate embeddings for multiple texts.

    Args:
        texts: List of texts to embed
        model: Embedding model
        batch_size: Maximum texts per API call

    Returns:
        List of embedding vectors
    """
    client = get_openai_client()
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = await client.embeddings.create(
            model=model,
            input=batch,
        )
        embeddings.extend([item.embedding for item in response.data])

    return embeddings


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to chunk
        chunk_size: Maximum chunk size in characters
        chunk_overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence ending
            for sep in [". ", "! ", "? ", "\\n\\n", "\\n"]:
                last_sep = text[start:end].rfind(sep)
                if last_sep > chunk_size // 2:
                    end = start + last_sep + len(sep)
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - chunk_overlap

    return chunks
'''


def generate_migration() -> str:
    """Generate Alembic migration for pgvector."""
    return '''"""Enable pgvector and create document tables

Revision ID: 001_pgvector
Revises:
Create Date: 2025-01-15
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = '001_pgvector'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('source', sa.String(500), nullable=True),
        sa.Column('metadata', sa.dialects.postgresql.JSONB(), server_default='{}'),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create chunks table
    op.create_table(
        'chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), server_default='0'),
        sa.Column('metadata', sa.dialects.postgresql.JSONB(), server_default='{}'),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
    )

    # Create indexes
    op.create_index('ix_documents_source', 'documents', ['source'])
    op.create_index('ix_chunks_document_id', 'chunks', ['document_id'])

    # Create HNSW index for fast vector search
    op.execute("""
        CREATE INDEX documents_embedding_idx
        ON documents
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    op.execute("""
        CREATE INDEX chunks_embedding_idx
        ON chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    # Create full-text search index
    op.execute("""
        CREATE INDEX documents_content_fts_idx
        ON documents
        USING gin(to_tsvector('english', content))
    """)


def downgrade() -> None:
    op.drop_index('documents_content_fts_idx')
    op.drop_index('chunks_embedding_idx')
    op.drop_index('documents_embedding_idx')
    op.drop_index('ix_chunks_document_id')
    op.drop_index('ix_documents_source')
    op.drop_table('chunks')
    op.drop_table('documents')
    op.execute('DROP EXTENSION IF EXISTS vector')
'''


def setup_pgvector(output_path: Path) -> None:
    """Set up pgvector files."""
    print("Setting up pgvector for vector similarity search")
    print("=" * 50)

    # Create directories
    app_path = output_path / "app"
    migrations_path = output_path / "alembic" / "versions"
    app_path.mkdir(parents=True, exist_ok=True)
    migrations_path.mkdir(parents=True, exist_ok=True)

    # Generate files
    files = [
        (app_path / "vector_models.py", generate_vector_models()),
        (app_path / "vector_search.py", generate_vector_search()),
        (app_path / "embeddings.py", generate_embedding_utils()),
        (migrations_path / "001_pgvector.py", generate_migration()),
    ]

    for file_path, content in files:
        file_path.write_text(content, encoding="utf-8")
        print(f"  Created: {file_path}")

    print("\n" + "=" * 50)
    print("pgvector setup complete!")
    print("\nNext steps:")
    print("  1. Install dependencies:")
    print("     pip install pgvector openai")
    print("  2. Run migration:")
    print("     alembic upgrade head")
    print("  3. Set OPENAI_API_KEY in environment")


def main():
    parser = argparse.ArgumentParser(
        description="Set up pgvector for vector similarity search"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path.cwd(),
        help="Output directory (default: current directory)"
    )

    args = parser.parse_args()
    setup_pgvector(args.output)


if __name__ == "__main__":
    main()
