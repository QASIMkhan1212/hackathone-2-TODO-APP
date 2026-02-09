"""Vector search utilities for RAG with Neon PostgreSQL and pgvector.

Provides semantic search, hybrid search, and RAG pipeline helpers.
"""

import os
from typing import Optional, Any, Callable, Awaitable
from datetime import datetime
from dataclasses import dataclass

from sqlmodel import SQLModel, Field, Column, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import Text, text
from sqlalchemy.dialects.postgresql import JSONB

try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    Vector = None

try:
    from openai import AsyncOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    AsyncOpenAI = None


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class VectorConfig:
    """Configuration for vector search."""
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    default_limit: int = 10
    default_threshold: float = 0.7
    chunk_size: int = 1000
    chunk_overlap: int = 200


DEFAULT_CONFIG = VectorConfig()


# =============================================================================
# Embedding Generation
# =============================================================================


class EmbeddingGenerator:
    """Generate embeddings using OpenAI API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "text-embedding-3-small",
    ):
        if not HAS_OPENAI:
            raise ImportError("openai package required: pip install openai")

        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 100,
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await self.client.embeddings.create(
                model=self.model,
                input=batch,
            )
            embeddings.extend([item.embedding for item in response.data])

        return embeddings


# Global embedding generator
_embedder: EmbeddingGenerator | None = None


def get_embedder() -> EmbeddingGenerator:
    """Get or create embedding generator."""
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingGenerator()
    return _embedder


async def get_embedding(text: str) -> list[float]:
    """Convenience function to get embedding."""
    return await get_embedder().embed(text)


# =============================================================================
# Text Chunking
# =============================================================================


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separators: list[str] | None = None,
) -> list[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Text to chunk
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between chunks
        separators: Sentence/paragraph separators to break at

    Returns:
        List of text chunks
    """
    if separators is None:
        separators = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Try to break at a separator
        if end < len(text):
            best_break = end
            for sep in separators:
                last_sep = text[start:end].rfind(sep)
                if last_sep > chunk_size // 2:
                    best_break = start + last_sep + len(sep)
                    break
            end = best_break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start with overlap
        start = max(start + 1, end - chunk_overlap)

    return chunks


# =============================================================================
# Vector Search
# =============================================================================


@dataclass
class SearchResult:
    """Search result with metadata."""
    id: int
    content: str
    similarity: float
    metadata: dict
    source: str | None = None


class VectorSearcher:
    """
    Vector similarity search operations.

    Usage:
        searcher = VectorSearcher(session)
        results = await searcher.search(query_embedding, limit=10)
    """

    def __init__(
        self,
        session: AsyncSession,
        table_name: str = "documents",
        content_column: str = "content",
        embedding_column: str = "embedding",
    ):
        self.session = session
        self.table_name = table_name
        self.content_column = content_column
        self.embedding_column = embedding_column

    async def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        threshold: float | None = None,
        filters: dict | None = None,
    ) -> list[SearchResult]:
        """
        Semantic similarity search.

        Args:
            query_embedding: Query vector
            limit: Maximum results
            threshold: Minimum similarity (0-1)
            filters: Metadata filters

        Returns:
            Search results with scores
        """
        # Build query
        filter_clause = ""
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"metadata->>'{key}' = '{value}'")
            filter_clause = "AND " + " AND ".join(conditions)

        threshold_clause = ""
        if threshold:
            threshold_clause = f"AND 1 - ({self.embedding_column} <=> :embedding::vector) >= {threshold}"

        sql = text(f"""
            SELECT
                id,
                {self.content_column} as content,
                source,
                metadata,
                1 - ({self.embedding_column} <=> :embedding::vector) as similarity
            FROM {self.table_name}
            WHERE {self.embedding_column} IS NOT NULL
            {filter_clause}
            {threshold_clause}
            ORDER BY {self.embedding_column} <=> :embedding::vector
            LIMIT :limit
        """)

        result = await self.session.execute(
            sql,
            {"embedding": query_embedding, "limit": limit}
        )

        return [
            SearchResult(
                id=row.id,
                content=row.content,
                similarity=float(row.similarity),
                metadata=row.metadata or {},
                source=row.source,
            )
            for row in result.fetchall()
        ]

    async def hybrid_search(
        self,
        query: str,
        query_embedding: list[float],
        limit: int = 10,
        semantic_weight: float = 0.7,
    ) -> list[SearchResult]:
        """
        Hybrid search combining vector and full-text search.

        Args:
            query: Text query for full-text
            query_embedding: Query vector for semantic
            limit: Maximum results
            semantic_weight: Weight for semantic vs text (0-1)

        Returns:
            Combined results ranked by RRF score
        """
        text_weight = 1 - semantic_weight
        k = 60  # RRF constant

        sql = text(f"""
            WITH semantic AS (
                SELECT
                    id,
                    {self.content_column} as content,
                    source,
                    metadata,
                    1 - ({self.embedding_column} <=> :embedding::vector) as score,
                    ROW_NUMBER() OVER (ORDER BY {self.embedding_column} <=> :embedding::vector) as rank
                FROM {self.table_name}
                WHERE {self.embedding_column} IS NOT NULL
                ORDER BY {self.embedding_column} <=> :embedding::vector
                LIMIT :limit * 3
            ),
            fulltext AS (
                SELECT
                    id,
                    {self.content_column} as content,
                    source,
                    metadata,
                    ts_rank_cd(
                        to_tsvector('english', {self.content_column}),
                        plainto_tsquery('english', :query)
                    ) as score,
                    ROW_NUMBER() OVER (
                        ORDER BY ts_rank_cd(
                            to_tsvector('english', {self.content_column}),
                            plainto_tsquery('english', :query)
                        ) DESC
                    ) as rank
                FROM {self.table_name}
                WHERE to_tsvector('english', {self.content_column}) @@ plainto_tsquery('english', :query)
                LIMIT :limit * 3
            )
            SELECT
                COALESCE(s.id, f.id) as id,
                COALESCE(s.content, f.content) as content,
                COALESCE(s.source, f.source) as source,
                COALESCE(s.metadata, f.metadata) as metadata,
                (
                    COALESCE(:semantic_weight / (:k + s.rank), 0) +
                    COALESCE(:text_weight / (:k + f.rank), 0)
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
            SearchResult(
                id=row.id,
                content=row.content,
                similarity=float(row.similarity),
                metadata=row.metadata or {},
                source=row.source,
            )
            for row in result.fetchall()
        ]


# =============================================================================
# RAG Pipeline
# =============================================================================


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline.

    Usage:
        rag = RAGPipeline(session)
        response = await rag.query("What is machine learning?")
    """

    def __init__(
        self,
        session: AsyncSession,
        embedder: EmbeddingGenerator | None = None,
        llm_client: Any = None,
        table_name: str = "documents",
    ):
        self.session = session
        self.embedder = embedder or get_embedder()
        self.llm_client = llm_client
        self.searcher = VectorSearcher(session, table_name)

    async def retrieve(
        self,
        query: str,
        limit: int = 5,
        use_hybrid: bool = True,
    ) -> list[SearchResult]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: User query
            limit: Maximum documents
            use_hybrid: Use hybrid search

        Returns:
            Relevant documents
        """
        query_embedding = await self.embedder.embed(query)

        if use_hybrid:
            return await self.searcher.hybrid_search(
                query=query,
                query_embedding=query_embedding,
                limit=limit,
            )
        else:
            return await self.searcher.search(
                query_embedding=query_embedding,
                limit=limit,
            )

    def format_context(
        self,
        results: list[SearchResult],
        max_tokens: int = 4000,
    ) -> str:
        """Format retrieved documents as context string."""
        context_parts = []
        estimated_tokens = 0

        for i, result in enumerate(results):
            doc_text = f"[Document {i+1}]\n{result.content}\n"
            doc_tokens = len(doc_text) // 4  # Rough estimate

            if estimated_tokens + doc_tokens > max_tokens:
                break

            context_parts.append(doc_text)
            estimated_tokens += doc_tokens

        return "\n".join(context_parts)

    async def query(
        self,
        query: str,
        system_prompt: str | None = None,
        limit: int = 5,
        use_hybrid: bool = True,
        llm_model: str = "gpt-4o",
    ) -> dict:
        """
        Full RAG query: retrieve and generate.

        Args:
            query: User question
            system_prompt: Optional system prompt
            limit: Documents to retrieve
            use_hybrid: Use hybrid search
            llm_model: LLM model for generation

        Returns:
            Dict with answer, sources, and context
        """
        # Retrieve
        results = await self.retrieve(query, limit, use_hybrid)
        context = self.format_context(results)

        # Generate
        if system_prompt is None:
            system_prompt = """Answer the question based on the provided context.
If the answer is not in the context, say so.
Cite relevant document numbers when possible."""

        if self.llm_client is None:
            self.llm_client = AsyncOpenAI()

        response = await self.llm_client.chat.completions.create(
            model=llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
            ],
        )

        return {
            "answer": response.choices[0].message.content,
            "sources": [
                {"id": r.id, "source": r.source, "similarity": r.similarity}
                for r in results
            ],
            "context": context,
            "model": llm_model,
        }

    async def ingest(
        self,
        content: str,
        metadata: dict | None = None,
        source: str | None = None,
        chunk_size: int = 1000,
    ) -> int:
        """
        Ingest document with chunking and embedding.

        Args:
            content: Document content
            metadata: Document metadata
            source: Document source/URL
            chunk_size: Chunk size for splitting

        Returns:
            Number of chunks created
        """
        # Chunk the content
        chunks = chunk_text(content, chunk_size=chunk_size)

        # Generate embeddings
        embeddings = await self.embedder.embed_batch(chunks)

        # Insert chunks
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            await self.session.execute(
                text("""
                    INSERT INTO documents (content, source, metadata, embedding, created_at)
                    VALUES (:content, :source, :metadata, :embedding::vector, NOW())
                """),
                {
                    "content": chunk,
                    "source": source,
                    "metadata": {**(metadata or {}), "chunk_index": i},
                    "embedding": embedding,
                }
            )

        await self.session.commit()
        return len(chunks)


# =============================================================================
# Convenience Functions
# =============================================================================


async def semantic_search(
    session: AsyncSession,
    query: str,
    limit: int = 10,
    table_name: str = "documents",
) -> list[SearchResult]:
    """
    Quick semantic search function.

    Args:
        session: Database session
        query: Search query
        limit: Maximum results
        table_name: Table to search

    Returns:
        Search results
    """
    embedding = await get_embedding(query)
    searcher = VectorSearcher(session, table_name)
    return await searcher.search(embedding, limit)


async def create_rag_pipeline(
    session: AsyncSession,
    table_name: str = "documents",
) -> RAGPipeline:
    """Create a RAG pipeline instance."""
    return RAGPipeline(session, table_name=table_name)
