"""
knowledge.py — Semantic Search & Vector Knowledge Schemas
==========================================================
WHAT THIS DOES:
  Defines Pydantic models for semantic vector search requests,
  ranked search results with citations and scores, and vector index statistics.

CONCEPTS:
  - top_k: The number of most semantically relevant text chunks to retrieve.
  - score: Cosine similarity metric measuring alignment between the query vector
    and stored document vectors (1.0 = exact match, 0.0 = completely unrelated).
"""

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Payload for POST /api/v1/knowledge/search"""
    query: str = Field(min_length=1, max_length=2000, description="Natural language search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Maximum number of relevant chunks to return")
    document_id: str | None = Field(default=None, description="Optional document ID to restrict search scope")
    workspace_id: str | None = Field(default=None, description="Workspace ID (defaults to user's workspace)")
    filters: dict[str, str] = Field(default_factory=dict, description="Optional key-value metadata filters")


class SearchResult(BaseModel):
    """Ranked relevant chunk returned from vector similarity search."""
    source_id: str = Field(description="Document ID of the source document")
    title: str = Field(description="Filename or title of the source document")
    snippet: str = Field(description="Extracted text chunk content")
    score: float = Field(description="Vector similarity score (Cosine distance)")
    chunk_index: int = Field(default=0, description="Zero-based index of this chunk in the document")
    metadata: dict = Field(default_factory=dict, description="Additional document metadata")


class IndexDocumentResponse(BaseModel):
    """Response returned when indexing a document into the vector store."""
    document_id: str
    filename: str
    chunks_indexed: int
    status: str


class KnowledgeStatsResponse(BaseModel):
    """Status and statistics of the vector knowledge base."""
    collection_name: str
    total_vectors_indexed: int
    vector_dimension: int
    engine: str
