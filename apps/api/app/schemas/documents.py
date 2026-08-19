"""
documents.py — Document Management & Knowledge Base Schemas
============================================================
WHAT THIS DOES:
  Defines Pydantic models for document ingestion, metadata inspection,
  chunk representations, and listing endpoints.

CONCEPTS:
  - DocumentStatus: Tracks the ingestion lifecycle (uploaded -> processing -> indexed / failed).
  - ChunkDetail: Granular piece of text produced by chunking algorithms, ready for vectorization (Phase 4).
"""

from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class ChunkDetail(BaseModel):
    """Represents an extracted and segmented piece of a document."""
    chunk_index: int
    text: str
    char_count: int


class DocumentUploadResponse(BaseModel):
    """Response returned upon uploading and processing a document."""
    id: str
    filename: str
    content_type: str
    size_bytes: int
    status: DocumentStatus
    chunks_count: int
    workspace_id: str
    created_at: str


class DocumentListItem(BaseModel):
    """Summarized item for document listing."""
    id: str
    filename: str
    content_type: str
    size_bytes: int
    status: DocumentStatus
    chunks_count: int
    workspace_id: str
    uploaded_by: str | None = None
    created_at: str


class DocumentDetailResponse(BaseModel):
    """Full detail of a document including its extracted chunks."""
    id: str
    filename: str
    content_type: str
    size_bytes: int
    status: DocumentStatus
    workspace_id: str
    uploaded_by: str | None = None
    created_at: str
    chunks_count: int
    chunks: list[ChunkDetail] = Field(default_factory=list)


class DocumentDeleteResponse(BaseModel):
    """Response returned upon successful document deletion."""
    success: bool
    message: str
    deleted_id: str
