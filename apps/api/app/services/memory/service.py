"""
service.py — Memory Management Service (Multi-Layered Memory)
=============================================================
WHAT THIS DOES:
  Provides persistent memory storage across 3 layers:
  1. Semantic Memory: Long-term persistent user facts & profile attributes.
  2. Episodic Memory: Historical interaction logs and milestones.
  3. User Preferences: Directives shaping tone, formatting, and behavior.

HYBRID RECALL ALGORITHM (INTERVIEW TOPIC):
  Combines Semantic Vector Similarity with Importance Decay Scoring:
  Score = (Cosine_Similarity * 0.70) + (Importance_Score * 0.30)
  Ensures that highly critical facts (e.g. "User allergic to nuts", "Project is Top Secret")
  are recalled even with slight semantic keyword divergence.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from fastapi import HTTPException, status

from app.schemas.memory import (
    MemoryCreateRequest,
    MemoryRecallItem,
    MemoryRecallResponse,
    MemoryResponse,
    MemoryType,
)
from app.services.rag.vector_store import (
    compute_cosine_similarity,
    generate_dense_embedding,
)


class MemoryEntity:
    def __init__(
        self,
        memory_id: str,
        user_id: str,
        workspace_id: str,
        content: str,
        memory_type: MemoryType,
        importance_score: float,
        tags: list[str],
        embedding: list[float],
        created_at: str | None = None,
        session_id: str | None = None,
    ) -> None:
        self.id = memory_id
        self.user_id = user_id
        self.workspace_id = workspace_id
        self.content = content
        self.memory_type = memory_type
        self.importance_score = importance_score
        self.tags = tags
        self.embedding = embedding
        self.session_id = session_id
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()


class MemoryService:
    """
    Central Service for storing, indexing, and recalling user memories.
    """

    def __init__(self) -> None:
        # In-memory memory store (memory_id -> MemoryEntity)
        self._memories: dict[str, MemoryEntity] = {}

    async def remember(
        self,
        user_id: str,
        workspace_id: str,
        payload: MemoryCreateRequest,
    ) -> MemoryResponse:
        """Store a new fact, event, or preference in the memory store."""
        memory_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        # Compute semantic vector embedding
        embedding = generate_dense_embedding(payload.content, dimension=384)

        entity = MemoryEntity(
            memory_id=memory_id,
            user_id=user_id,
            workspace_id=workspace_id,
            content=payload.content,
            memory_type=payload.memory_type,
            importance_score=payload.importance_score,
            tags=payload.tags,
            embedding=embedding,
            session_id=payload.session_id,
            created_at=created_at,
        )

        self._memories[memory_id] = entity

        return MemoryResponse(
            id=entity.id,
            user_id=entity.user_id,
            workspace_id=entity.workspace_id,
            content=entity.content,
            memory_type=entity.memory_type,
            importance_score=entity.importance_score,
            tags=entity.tags,
            created_at=entity.created_at,
        )

    async def recall(
        self,
        user_id: str,
        workspace_id: str,
        query: str,
        limit: int = 5,
        memory_type: MemoryType | None = None,
    ) -> MemoryRecallResponse:
        """
        Recall relevant memories matching the query using hybrid scoring.
        Score = (Cosine_Similarity * 0.70) + (Importance_Score * 0.30)
        """
        query_vector = generate_dense_embedding(query, dimension=384)
        scored: list[tuple[float, MemoryEntity]] = []

        for mem in self._memories.values():
            if mem.user_id != user_id or mem.workspace_id != workspace_id:
                continue
            if memory_type and mem.memory_type != memory_type:
                continue

            similarity = compute_cosine_similarity(query_vector, mem.embedding)
            # Hybrid rank score
            hybrid_score = (similarity * 0.70) + (mem.importance_score * 0.30)

            if similarity > 0.05 or mem.importance_score >= 0.8:
                scored.append((hybrid_score, mem))

        # Sort descending by hybrid relevance score
        scored.sort(key=lambda x: x[0], reverse=True)

        items = [
            MemoryRecallItem(
                id=mem.id,
                content=mem.content,
                memory_type=mem.memory_type.value,
                relevance_score=round(score, 4),
                importance_score=mem.importance_score,
                tags=mem.tags,
            )
            for score, mem in scored[:limit]
        ]

        return MemoryRecallResponse(query=query, count=len(items), memories=items)

    async def list_memories(
        self,
        user_id: str,
        workspace_id: str,
        memory_type: MemoryType | None = None,
    ) -> list[MemoryResponse]:
        """List all memories belonging to a specific user and workspace."""
        return [
            MemoryResponse(
                id=mem.id,
                user_id=mem.user_id,
                workspace_id=mem.workspace_id,
                content=mem.content,
                memory_type=mem.memory_type,
                importance_score=mem.importance_score,
                tags=mem.tags,
                created_at=mem.created_at,
            )
            for mem in self._memories.values()
            if mem.user_id == user_id
            and mem.workspace_id == workspace_id
            and (memory_type is None or mem.memory_type == memory_type)
        ]

    async def delete_memory(self, memory_id: str, user_id: str, workspace_id: str) -> bool:
        """Delete a memory entry ensuring user & workspace tenancy checks."""
        mem = self._memories.get(memory_id)
        if not mem or mem.user_id != user_id or mem.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memory '{memory_id}' not found.",
            )

        del self._memories[memory_id]
        return True


# Global singleton
memory_service = MemoryService()


def get_memory_service() -> MemoryService:
    return memory_service
