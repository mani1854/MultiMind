"""
chat.py — Conversational AI & Chat Schemas
===========================================
WHAT THIS DOES:
  Defines Pydantic models for chat messages, session context,
  grounded citations, and agent execution events.

CONCEPTS:
  - Citation: Traceable link connecting the LLM answer to exact source chunks in the knowledge base.
  - stream: Boolean flag enabling Server-Sent Events (SSE) token streaming.
"""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single turn in the conversation history."""
    role: str = Field(description="'user', 'assistant', or 'system'")
    content: str = Field(description="Message body text")


class Citation(BaseModel):
    """Source reference attributed to an answer."""
    title: str = Field(description="Document filename or title")
    source_id: str = Field(description="Document ID")
    snippet: str = Field(description="Exact retrieved chunk snippet used as context")
    score: float = Field(description="Cosine similarity confidence score")
    chunk_index: int = Field(default=0, description="Index of chunk in document")


class AgentEvent(BaseModel):
    """Lifecycle event emitted during request processing (for observability)."""
    agent: str = Field(description="Name of the agent/service module")
    status: str = Field(description="'started', 'completed', 'skipped', 'failed'")
    detail: str = Field(description="Human-readable description of the step")


class ChatRequest(BaseModel):
    """Payload for POST /api/v1/chat"""
    message: str = Field(min_length=1, max_length=12000, description="User's prompt or question")
    session_id: str = Field(default="default", description="Conversation session identifier")
    workspace_id: str | None = Field(default=None, description="Workspace ID (defaults to user workspace)")
    history: list[ChatMessage] = Field(default_factory=list, description="Prior conversation turns")
    stream: bool = Field(default=False, description="Whether to stream response tokens via SSE")
    top_k: int = Field(default=4, ge=1, le=20, description="Number of context chunks to retrieve")


class ChatResponse(BaseModel):
    """Response returned for synchronous chat requests."""
    answer: str = Field(description="Synthesized LLM response")
    intent: str = Field(default="rag_chat", description="Classified intent of the request")
    citations: list[Citation] = Field(default_factory=list, description="Grounded source citations")
    agent_events: list[AgentEvent] = Field(default_factory=list, description="Execution trace events")
