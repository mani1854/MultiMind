"""
memory.py — Memory System Schemas
==================================
WHAT THIS DOES:
  Defines Pydantic models for persistent user facts, episodic conversation events,
  preferences, and memory recall queries.

CONCEPTS:
  - Semantic Memory: Factual knowledge (e.g. "User is Lead Data Scientist on Project Apollo").
  - Episodic Memory: Event sequences (e.g. "User approved Q3 budget on Friday").
  - User Preference: Behavioral instructions (e.g. "Prefers responses in bullet points").
  - Importance Score: Weight from 0.0 to 1.0 used to prioritize high-value facts during recall.
"""

from enum import Enum
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    SEMANTIC_FACT = "semantic_fact"
    EPISODIC_EVENT = "episodic_event"
    USER_PREFERENCE = "user_preference"
    SESSION_CONTEXT = "session_context"


class MemoryCreateRequest(BaseModel):
    """Payload for POST /api/v1/memory"""
    content: str = Field(min_length=1, max_length=4000, description="Fact, event, or preference to remember")
    memory_type: MemoryType = Field(default=MemoryType.SEMANTIC_FACT, description="Category of memory")
    importance_score: float = Field(default=0.7, ge=0.0, le=1.0, description="Subjective value / priority")
    tags: list[str] = Field(default_factory=list, description="Categorization tags (e.g. ['project', 'lead'])")
    session_id: str | None = Field(default=None, description="Optional conversation session ID")


class MemoryResponse(BaseModel):
    """Memory representation returned from storage."""
    id: str
    user_id: str
    workspace_id: str
    content: str
    memory_type: MemoryType
    importance_score: float
    tags: list[str]
    created_at: str


class MemoryRecallItem(BaseModel):
    """A scored recalled memory."""
    id: str
    content: str
    memory_type: str
    relevance_score: float
    importance_score: float
    tags: list[str]


class MemoryRecallResponse(BaseModel):
    """Response returned for memory recall queries."""
    query: str
    count: int
    memories: list[MemoryRecallItem]
