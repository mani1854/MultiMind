"""
knowledge.py — Semantic Vector Search & Knowledge Base Endpoints
=================================================================
WHAT THIS DOES:
  Exposes REST APIs for vector semantic search, document re-indexing,
  and vector database collection statistics.

ENDPOINTS:
  - POST /api/v1/knowledge/search          → Semantic query matching against dense chunk embeddings
  - POST /api/v1/knowledge/index/{doc_id}  → Explicitly index a document's chunks into vector DB
  - GET  /api/v1/knowledge/stats           → View vector collection dimension, point counts, engine
"""

from fastapi import APIRouter, Depends

from app.core.security import require_principal
from app.schemas.knowledge import (
    IndexDocumentResponse,
    KnowledgeStatsResponse,
    SearchRequest,
    SearchResult,
)
from app.services.rag.service import RAGService, get_rag_service

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post(
    "/search",
    response_model=list[SearchResult],
    summary="Semantic vector search across workspace knowledge chunks",
)
async def search_knowledge_base(
    payload: SearchRequest,
    principal: dict = Depends(require_principal),
    rag: RAGService = Depends(get_rag_service),
) -> list[SearchResult]:
    """
    Executes dense vector similarity search:
    1. Converts query text into a 384-dimensional dense embedding vector.
    2. Performs Cosine Similarity lookup against indexed chunks.
    3. Filters by workspace_id and optional document_id.
    4. Returns top-K most relevant chunks with similarity confidence scores.
    """
    workspace_id = payload.workspace_id or principal.get("workspace_id", "demo-workspace")

    return await rag.search(
        query=payload.query,
        workspace_id=workspace_id,
        top_k=payload.top_k,
        document_id=payload.document_id,
        filters=payload.filters,
    )


@router.post(
    "/index/{document_id}",
    response_model=IndexDocumentResponse,
    summary="Index or re-index a document into the vector database",
)
async def index_document(
    document_id: str,
    principal: dict = Depends(require_principal),
    rag: RAGService = Depends(get_rag_service),
) -> IndexDocumentResponse:
    """
    Explicitly embeds all text chunks of a document and upserts them
    into the vector store.
    """
    workspace_id = principal.get("workspace_id", "demo-workspace")
    return await rag.index_document(document_id=document_id, workspace_id=workspace_id)


@router.get(
    "/stats",
    response_model=KnowledgeStatsResponse,
    summary="Get vector database collection statistics",
)
async def get_knowledge_stats(
    _: dict = Depends(require_principal),
    rag: RAGService = Depends(get_rag_service),
) -> KnowledgeStatsResponse:
    """Returns vector database collection name, dimension, and total indexed points."""
    return rag.get_stats()
