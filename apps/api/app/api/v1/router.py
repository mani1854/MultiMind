"""
router.py — API v1 Master Router (Phase 8)
===========================================
WHAT THIS DOES:
  Aggregates all versioned endpoints under `/api/v1`.

MOUNTED IN PHASE 8:
  - /api/v1/health    → Infrastructure heartbeat
  - /api/v1/auth      → User registration, login, refresh, profile
  - /api/v1/admin     → Privileged governance & RBAC administration
  - /api/v1/documents → Knowledge management, multi-format upload, text extraction, chunking
  - /api/v1/knowledge → RAG pipeline, dense vector embeddings, Qdrant semantic search
  - /api/v1/chat      → Grounded Conversational AI, LLM Gateway, SSE token streaming
  - /api/v1/memory    → Multi-layered memory system (semantic facts, episodic logs, recall)
  - /api/v1/workflows → Automated enterprise workflows, tool execution DAGs, run history
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    auth,
    chat,
    documents,
    health,
    knowledge,
    memory,
    workflows,
)

api_router = APIRouter(prefix="/api/v1")

# Mount endpoints
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(documents.router)
api_router.include_router(knowledge.router)
api_router.include_router(chat.router)
api_router.include_router(memory.router)
api_router.include_router(workflows.router)
