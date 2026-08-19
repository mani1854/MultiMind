"""
chat.py — Conversational AI & Streaming Endpoints
==================================================
WHAT THIS DOES:
  Exposes REST and SSE streaming endpoints for interacting with the AI Copilot.

ENDPOINTS:
  - POST /api/v1/chat        → Batch JSON response (or SSE stream if `stream: true`)
  - POST /api/v1/chat/stream → Explicit Server-Sent Events (SSE) token streaming endpoint
  - WS   /api/v1/chat/ws     → Real-time bi-directional WebSocket streaming
"""

from fastapi import APIRouter, Depends, WebSocket
from fastapi.responses import StreamingResponse

from app.core.security import require_principal
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat import ChatService, get_chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Ask a question and receive a personalized, grounded answer with citations",
)
async def chat_endpoint(
    payload: ChatRequest,
    principal: dict = Depends(require_principal),
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse | StreamingResponse:
    """
    Core Chat Endpoint:
    - If `stream: false` -> returns complete JSON `ChatResponse` with answer, citations, and trace events.
    - If `stream: true` -> returns a real-time Server-Sent Events (SSE) `text/event-stream`.
    """
    workspace_id = payload.workspace_id or principal.get("workspace_id", "demo-workspace")
    user_id = principal.get("sub", "demo-admin")

    if payload.stream:
        return StreamingResponse(
            service.stream(payload, workspace_id=workspace_id, user_id=user_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return await service.run(payload, workspace_id=workspace_id, user_id=user_id)


@router.post(
    "/stream",
    summary="Stream AI tokens and retrieval events in real-time via Server-Sent Events (SSE)",
)
async def chat_stream_endpoint(
    payload: ChatRequest,
    principal: dict = Depends(require_principal),
    service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """
    Dedicated SSE streaming route returning `text/event-stream`.
    Emits `agent`, `citation`, `token`, and `done` events.
    """
    workspace_id = payload.workspace_id or principal.get("workspace_id", "demo-workspace")
    user_id = principal.get("sub", "demo-admin")

    return StreamingResponse(
        service.stream(payload, workspace_id=workspace_id, user_id=user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.websocket("/ws")
async def chat_websocket(
    websocket: WebSocket,
    service: ChatService = Depends(get_chat_service),
) -> None:
    """
    Bidirectional WebSocket connection for ultra low-latency conversational UI.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            payload = ChatRequest(**data)
            workspace_id = payload.workspace_id or "demo-workspace"
            user_id = "demo-admin"

            async for sse_chunk in service.stream(payload, workspace_id=workspace_id, user_id=user_id):
                await websocket.send_text(sse_chunk)
    except Exception:
        await websocket.close()
