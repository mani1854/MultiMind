"""
service.py — Retrieval-Augmented Generation (RAG) Service
==========================================================
WHAT THIS DOES:
  Coordinates the document knowledge base with vector indexing
  and semantic top-K context retrieval.

ARCHITECTURE PATTERN:
  Façade & Service layer pattern: Connects the Document Management module (Phase 3)
  with the Vector Store & Embedding Engine (Phase 4).
"""

from typing import Any
from fastapi import HTTPException, status

from app.schemas.knowledge import (
    IndexDocumentResponse,
    KnowledgeStatsResponse,
    SearchResult,
)
from app.services.documents import DocumentService, get_document_service
from app.services.rag.vector_store import VectorStore, get_vector_store


class RAGService:
    """
    High-level service coordinating document indexing and semantic vector retrieval.
    """

    def __init__(
        self,
        vector_store_inst: VectorStore | None = None,
        doc_service_inst: DocumentService | None = None,
    ) -> None:
        self.vector_store = vector_store_inst or get_vector_store()
        self.doc_service = doc_service_inst or get_document_service()

    async def index_document(self, document_id: str, workspace_id: str) -> IndexDocumentResponse:
        """
        Fetch a document's chunks and index them into the vector database.
        """
        doc_detail = await self.doc_service.get_document(document_id, workspace_id)
        if not doc_detail.chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document '{doc_detail.filename}' contains no extractable text chunks.",
            )

        chunks_text = [chunk.text for chunk in doc_detail.chunks]

        indexed_count = await self.vector_store.upsert_chunks(
            workspace_id=workspace_id,
            document_id=document_id,
            title=doc_detail.filename,
            chunks=chunks_text,
            metadata={"content_type": doc_detail.content_type},
        )

        return IndexDocumentResponse(
            document_id=document_id,
            filename=doc_detail.filename,
            chunks_indexed=indexed_count,
            status="indexed",
        )

    async def search(
        self,
        query: str,
        workspace_id: str,
        top_k: int = 5,
        document_id: str | None = None,
        filters: dict[str, str] | None = None,
    ) -> list[SearchResult]:
        """
        Semantic query execution returning top-k relevant document chunks with citations.
        """
        return await self.vector_store.search(
            query=query,
            workspace_id=workspace_id,
            top_k=top_k,
            document_id=document_id,
            filters=filters,
        )

    def get_stats(self) -> KnowledgeStatsResponse:
        """Return knowledge base vector stats."""
        stats = self.vector_store.get_stats()
        return KnowledgeStatsResponse(
            collection_name=stats["collection_name"],
            total_vectors_indexed=stats["total_vectors_indexed"],
            vector_dimension=stats["vector_dimension"],
            engine=stats["engine"],
        )


# Global singleton
rag_service = RAGService()


def get_rag_service() -> RAGService:
    return rag_service
