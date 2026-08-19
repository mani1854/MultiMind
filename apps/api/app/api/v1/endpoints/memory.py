"""
memory.py — Memory Management & Semantic Recall Endpoints
==========================================================
WHAT THIS DOES:
  Exposes REST APIs to persist, search, and manage long-term user memories,
  preferences, and episodic interaction context.

ENDPOINTS:
  - POST   /api/v1/memory        → Store a new user fact, preference, or event
  - GET    /api/v1/memory        → List all stored memories for the authenticated user
  - POST   /api/v1/memory/recall → Semantic & importance-weighted memory lookup
  - DELETE /api/v1/memory/{id}   → Remove a memory record
"""

from fastapi import APIRouter, Depends, Query, status

from app.core.security import require_principal
from app.schemas.memory import (
    MemoryCreateRequest,
    MemoryRecallResponse,
    MemoryResponse,
    MemoryType,
)
from app.services.memory.service import MemoryService, get_memory_service

router = APIRouter(prefix="/memory", tags=["memory"])


@router.post(
    "",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Store a new memory, preference, or fact",
)
async def create_memory(
    payload: MemoryCreateRequest,
    principal: dict = Depends(require_principal),
    service: MemoryService = Depends(get_memory_service),
) -> MemoryResponse:
    """
    Saves a persistent memory record:
    1. Computes vector embedding for semantic search.
    2. Tags with importance score and memory type.
    3. Scopes strictly to caller's `user_id` and `workspace_id`.
    """
    user_id = principal.get("sub", "demo-admin")
    workspace_id = principal.get("workspace_id", "demo-workspace")

    return await service.remember(
        user_id=user_id,
        workspace_id=workspace_id,
        payload=payload,
    )


@router.get(
    "",
    response_model=list[MemoryResponse],
    summary="List all memories for the authenticated user",
)
async def list_memories(
    memory_type: MemoryType | None = Query(default=None, description="Optional filter by memory category"),
    principal: dict = Depends(require_principal),
    service: MemoryService = Depends(get_memory_service),
) -> list[MemoryResponse]:
    """Returns stored facts, episodic logs, and preferences for the calling user."""
    user_id = principal.get("sub", "demo-admin")
    workspace_id = principal.get("workspace_id", "demo-workspace")

    return await service.list_memories(
        user_id=user_id,
        workspace_id=workspace_id,
        memory_type=memory_type,
    )


@router.post(
    "/recall",
    response_model=MemoryRecallResponse,
    summary="Recall relevant memories using hybrid vector similarity and importance scoring",
)
async def recall_memories(
    query: str = Query(..., description="Query prompt to recall relevant memories for"),
    limit: int = Query(default=5, ge=1, le=20),
    memory_type: MemoryType | None = Query(default=None),
    principal: dict = Depends(require_principal),
    service: MemoryService = Depends(get_memory_service),
) -> MemoryRecallResponse:
    """
    Executes hybrid retrieval:
    Relevance Score = (Cosine_Similarity * 0.70) + (Importance_Score * 0.30)
    """
    user_id = principal.get("sub", "demo-admin")
    workspace_id = principal.get("workspace_id", "demo-workspace")

    return await service.recall(
        user_id=user_id,
        workspace_id=workspace_id,
        query=query,
        limit=limit,
        memory_type=memory_type,
    )


@router.delete(
    "/{memory_id}",
    summary="Delete a memory record",
)
async def delete_memory(
    memory_id: str,
    principal: dict = Depends(require_principal),
    service: MemoryService = Depends(get_memory_service),
) -> dict:
    """Deletes a memory entry belonging to the authenticated user."""
    user_id = principal.get("sub", "demo-admin")
    workspace_id = principal.get("workspace_id", "demo-workspace")

    await service.delete_memory(memory_id=memory_id, user_id=user_id, workspace_id=workspace_id)
    return {"success": True, "deleted_id": memory_id}
