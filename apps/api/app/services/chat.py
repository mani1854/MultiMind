"""
chat.py — Conversational AI Service powered by Multi-Agent Orchestrator
========================================================================
WHAT THIS DOES:
  Acts as the primary application service for AI Chat interactions.
  Delegates all reasoning, knowledge retrieval, memory recall, and synthesis
  to the 11-Agent Orchestrator.
"""

from collections.abc import AsyncGenerator
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agents.orchestrator import AgentOrchestrator, get_agent_orchestrator


class ChatService:
    """
    Chat Service façade bridging the API layer with the Multi-Agent Orchestrator.
    """

    def __init__(self, orchestrator_inst: AgentOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator_inst or get_agent_orchestrator()

    async def run(
        self,
        request: ChatRequest,
        workspace_id: str,
        user_id: str = "demo-admin",
    ) -> ChatResponse:
        """Executes full multi-agent cognitive pipeline synchronously."""
        return await self.orchestrator.run(
            request=request,
            workspace_id=workspace_id,
            user_id=user_id,
        )

    async def stream(
        self,
        request: ChatRequest,
        workspace_id: str,
        user_id: str = "demo-admin",
    ) -> AsyncGenerator[str, None]:
        """Streams multi-agent lifecycle events, citations, and tokens in real-time."""
        async for chunk in self.orchestrator.stream(
            request=request,
            workspace_id=workspace_id,
            user_id=user_id,
        ):
            yield chunk


# Global singleton
chat_service = ChatService()


def get_chat_service() -> ChatService:
    return chat_service
