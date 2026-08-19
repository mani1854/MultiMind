"""
documents.py — Document Management Service (Phase 4 Integrated)
================================================================
WHAT THIS DOES:
  Provides business logic for document ingestion, text parsing, chunking,
  multi-tenant workspace isolation, document lifecycle management,
  and automatic vector index synchronization with the Vector Store (Phase 4).

ARCHITECTURE:
  - Multi-Tenancy: Documents are scoped strictly by `workspace_id`.
  - Auto-Indexing: Chunks are automatically embedded and indexed upon ingestion.
"""

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status

from app.schemas.documents import (
    ChunkDetail,
    DocumentDeleteResponse,
    DocumentDetailResponse,
    DocumentListItem,
    DocumentStatus,
    DocumentUploadResponse,
)
from app.services.rag.document_loader import (
    SUPPORTED_EXTENSIONS,
    chunk_text,
    extract_text_from_bytes,
)
from app.services.rag.vector_store import get_vector_store

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


class DocumentEntity:
    def __init__(
        self,
        doc_id: str,
        filename: str,
        content_type: str,
        size_bytes: int,
        status: DocumentStatus,
        workspace_id: str,
        uploaded_by: str | None,
        raw_text: str,
        chunks: list[str],
        created_at: str | None = None,
    ) -> None:
        self.id = doc_id
        self.filename = filename
        self.content_type = content_type
        self.size_bytes = size_bytes
        self.status = status
        self.workspace_id = workspace_id
        self.uploaded_by = uploaded_by
        self.raw_text = raw_text
        self.chunks = chunks
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()


class DocumentService:
    """
    Service responsible for document ingestion, text parsing, chunking,
    and vector database synchronization.
    """

    def __init__(self) -> None:
        self._documents: dict[str, DocumentEntity] = {}  # doc_id -> DocumentEntity

    async def upload_document(
        self,
        file: UploadFile,
        workspace_id: str,
        uploaded_by: str | None = None,
    ) -> DocumentUploadResponse:
        """
        Ingest a file: validate -> extract text -> segment into chunks -> index vectors -> store record.
        """
        filename = file.filename or "uploaded-document"
        content_type = file.content_type or "application/octet-stream"

        # Read binary data
        data = await file.read()
        size_bytes = len(data)

        if size_bytes > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB.",
            )

        # Extract text from supported formats
        extracted_text = extract_text_from_bytes(filename, data)

        # Chunk the text
        chunks = chunk_text(extracted_text, chunk_size=1000, overlap=150)
        doc_status = DocumentStatus.INDEXED if chunks else DocumentStatus.UPLOADED

        doc_id = str(uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        # Automatic vector indexing in Vector Store (Phase 4)
        if chunks:
            vector_db = get_vector_store()
            await vector_db.upsert_chunks(
                workspace_id=workspace_id,
                document_id=doc_id,
                title=filename,
                chunks=chunks,
                metadata={"content_type": content_type},
            )

        doc_entity = DocumentEntity(
            doc_id=doc_id,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            status=doc_status,
            workspace_id=workspace_id,
            uploaded_by=uploaded_by,
            raw_text=extracted_text,
            chunks=chunks,
            created_at=created_at,
        )

        self._documents[doc_id] = doc_entity

        return DocumentUploadResponse(
            id=doc_id,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            status=doc_status,
            chunks_count=len(chunks),
            workspace_id=workspace_id,
            created_at=created_at,
        )

    async def list_documents(self, workspace_id: str) -> list[DocumentListItem]:
        """List all documents belonging to the specified workspace."""
        return [
            DocumentListItem(
                id=doc.id,
                filename=doc.filename,
                content_type=doc.content_type,
                size_bytes=doc.size_bytes,
                status=doc.status,
                chunks_count=len(doc.chunks),
                workspace_id=doc.workspace_id,
                uploaded_by=doc.uploaded_by,
                created_at=doc.created_at,
            )
            for doc in self._documents.values()
            if doc.workspace_id == workspace_id
        ]

    async def get_document(self, document_id: str, workspace_id: str) -> DocumentDetailResponse:
        """Fetch document details and extracted chunks, ensuring workspace isolation."""
        doc = self._documents.get(document_id)
        if not doc or doc.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{document_id}' not found in this workspace.",
            )

        chunks_detail = [
            ChunkDetail(chunk_index=idx, text=chunk_str, char_count=len(chunk_str))
            for idx, chunk_str in enumerate(doc.chunks)
        ]

        return DocumentDetailResponse(
            id=doc.id,
            filename=doc.filename,
            content_type=doc.content_type,
            size_bytes=doc.size_bytes,
            status=doc.status,
            workspace_id=doc.workspace_id,
            uploaded_by=doc.uploaded_by,
            created_at=doc.created_at,
            chunks_count=len(doc.chunks),
            chunks=chunks_detail,
        )

    async def delete_document(self, document_id: str, workspace_id: str) -> DocumentDeleteResponse:
        """Delete document and its vector embeddings from workspace."""
        doc = self._documents.get(document_id)
        if not doc or doc.workspace_id != workspace_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID '{document_id}' not found in this workspace.",
            )

        # Delete associated vectors
        vector_db = get_vector_store()
        vector_db.delete_document_vectors(document_id=document_id, workspace_id=workspace_id)

        del self._documents[document_id]

        return DocumentDeleteResponse(
            success=True,
            message=f"Document '{doc.filename}' ({document_id}) deleted successfully.",
            deleted_id=document_id,
        )


# Singleton instance
document_service = DocumentService()


def get_document_service() -> DocumentService:
    return document_service
