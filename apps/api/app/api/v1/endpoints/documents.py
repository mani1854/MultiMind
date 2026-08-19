"""
documents.py — Document Management Endpoints
=============================================
WHAT THIS DOES:
  Exposes REST APIs for document uploads, listing, chunk inspection, and deletion.

ENDPOINTS:
  - POST   /api/v1/documents/upload → Upload & process document (PDF, DOCX, CSV, PPTX, TXT, MD)
  - GET    /api/v1/documents        → List all documents in the user's workspace
  - GET    /api/v1/documents/{id}   → Get document metadata and extracted text chunks
  - DELETE /api/v1/documents/{id}   → Remove document and chunks from workspace
"""

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.security import require_principal
from app.schemas.documents import (
    DocumentDeleteResponse,
    DocumentDetailResponse,
    DocumentListItem,
    DocumentUploadResponse,
)
from app.services.documents import DocumentService, get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and ingest a document into the workspace knowledge base",
)
async def upload_document(
    file: UploadFile = File(..., description="Document file (.pdf, .docx, .txt, .md, .pptx, .csv)"),
    principal: dict = Depends(require_principal),
    service: DocumentService = Depends(get_document_service),
) -> DocumentUploadResponse:
    """
    Ingests a document for the authenticated user's workspace:
    1. Validates format and size limits.
    2. Extracts structured text.
    3. Segments text into overlapping chunks for downstream vector indexing.
    """
    workspace_id = principal.get("workspace_id", "demo-workspace")
    uploaded_by = principal.get("email")

    return await service.upload_document(
        file=file,
        workspace_id=workspace_id,
        uploaded_by=uploaded_by,
    )


@router.get(
    "",
    response_model=list[DocumentListItem],
    summary="List all documents in the current workspace",
)
async def list_documents(
    principal: dict = Depends(require_principal),
    service: DocumentService = Depends(get_document_service),
) -> list[DocumentListItem]:
    """Returns all documents ingested within the caller's workspace."""
    workspace_id = principal.get("workspace_id", "demo-workspace")
    return await service.list_documents(workspace_id=workspace_id)


@router.get(
    "/{document_id}",
    response_model=DocumentDetailResponse,
    summary="Get document details and extracted chunks",
)
async def get_document_details(
    document_id: str,
    principal: dict = Depends(require_principal),
    service: DocumentService = Depends(get_document_service),
) -> DocumentDetailResponse:
    """Fetches full metadata and individual chunk contents for a specific document."""
    workspace_id = principal.get("workspace_id", "demo-workspace")
    return await service.get_document(document_id=document_id, workspace_id=workspace_id)


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    summary="Delete a document from the workspace knowledge base",
)
async def delete_document(
    document_id: str,
    principal: dict = Depends(require_principal),
    service: DocumentService = Depends(get_document_service),
) -> DocumentDeleteResponse:
    """Deletes a document and its chunks, scoped to the caller's workspace."""
    workspace_id = principal.get("workspace_id", "demo-workspace")
    return await service.delete_document(document_id=document_id, workspace_id=workspace_id)
