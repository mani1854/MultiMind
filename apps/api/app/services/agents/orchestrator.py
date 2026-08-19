"""
orchestrator.py — Multi-Agent Pipeline Orchestrator (Supervisor Pattern)
========================================================================
WHAT THIS DOES:
  Executes the sequential blackboard pipeline across 11 specialist agents:
  Router → Memory → Retrieval → Research → Meeting → Summarization →
  Report → Workflow → Response → Validation → AdminMonitoring

STREAMING ARCHITECTURE:
  As each agent finishes its task, an SSE event (`event: agent`) is pushed to the client,
  giving users real-time visibility into the multi-agent cognitive process.
"""

from collections.abc import AsyncGenerator
import json
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agents.base import AgentState
from app.services.agents.specialists import (
    AdminMonitoringAgent,
    MeetingIntelligenceAgent,
    MemoryAgent,
    ReportGenerationAgent,
    ResearchAgent,
    ResponseAgent,
    RetrievalAgent,
    RouterAgent,
    SummarizationAgent,
    ValidationAgent,
    WorkflowAutomationAgent,
)
from app.services.llm import get_llm_gateway
from app.services.memory.service import get_memory_service
from app.services.rag.service import get_rag_service
from app.services.workflows.engine import WorkflowEngine


class AgentOrchestrator:
    """
    Central Multi-Agent Pipeline Orchestrator.
    Coordinates the 11 specialists across shared AgentState.
    """

    def __init__(self) -> None:
        self.router = RouterAgent()
        self.memory = MemoryAgent(get_memory_service())
        self.retrieval = RetrievalAgent(get_rag_service())
        self.research = ResearchAgent()
        self.meeting = MeetingIntelligenceAgent()
        self.summarization = SummarizationAgent()
        self.report = ReportGenerationAgent()
        self.workflow = WorkflowAutomationAgent(WorkflowEngine())
        self.response = ResponseAgent(get_llm_gateway())
        self.validation = ValidationAgent()
        self.admin = AdminMonitoringAgent()

        self.pipeline = [
            self.router,
            self.memory,
            self.retrieval,
            self.research,
            self.meeting,
            self.summarization,
            self.report,
            self.workflow,
            self.response,
            self.validation,
            self.admin,
        ]

    async def run(
        self,
        request: ChatRequest,
        workspace_id: str | None = None,
        user_id: str = "demo-admin",
    ) -> ChatResponse:
        """Synchronous batch execution across all 11 agents."""
        ws_id = workspace_id or request.workspace_id or "demo-workspace"
        state = AgentState(
            message=request.message,
            workspace_id=ws_id,
            user_id=user_id,
            session_id=request.session_id,
        )

        for agent in self.pipeline:
            state = await agent.run(state)

        return ChatResponse(
            answer=state.answer,
            intent=state.intent,
            citations=state.context,
            agent_events=state.events,
        )

    async def stream(
        self,
        request: ChatRequest,
        workspace_id: str | None = None,
        user_id: str = "demo-admin",
    ) -> AsyncGenerator[str, None]:
        """
        Real-time SSE streaming across the 11-agent execution pipeline.
        Emits live agent status updates, citations, and LLM token deltas.
        """
        ws_id = workspace_id or request.workspace_id or "demo-workspace"
        state = AgentState(
            message=request.message,
            workspace_id=ws_id,
            user_id=user_id,
            session_id=request.session_id,
        )

        # Run pre-response agents (Router -> Memory -> Retrieval -> Research -> Meeting -> Summarization -> Report -> Workflow)
        pre_agents = [
            self.router,
            self.memory,
            self.retrieval,
            self.research,
            self.meeting,
            self.summarization,
            self.report,
            self.workflow,
        ]

        for agent in pre_agents:
            prev_len = len(state.events)
            state = await agent.run(state)
            # Emit newly added agent events
            for evt in state.events[prev_len:]:
                yield f"event: agent\ndata: {evt.model_dump_json()}\n\n"

        # Emit citations
        for citation in state.context:
            yield f"event: citation\ndata: {citation.model_dump_json()}\n\n"

        # Run Response Agent with token streaming
        system_prompt = (
            "You are MultiMind, an Enterprise Multi-Agent Copilot.\n"
            "Ground your answers in the provided context.\n"
            "GUIDELINES:\n"
            "1. Base answers STRICTLY on the RETRIEVED KNOWLEDGE CONTEXT and USER MEMORIES.\n"
            "2. If context is absent, state: 'I could not find information regarding this in company documents.'"
        )

        context_blocks = [f"[{c.title} | Chunk {c.chunk_index}]:\n{c.snippet}" for c in state.context]
        context_text = "\n\n".join(context_blocks) if context_blocks else "No relevant documents found."
        memory_text = "\n".join(f"- {m}" for m in state.memories) if state.memories else "None."
        research_text = "\n".join(f"- {n}" for n in state.research_notes) if state.research_notes else "None."

        user_prompt = (
            f"User Intent: {state.intent}\n\n"
            f"--- USER PROFILE & MEMORIES ---\n{memory_text}\n---\n\n"
            f"--- SYNTHESIZED RESEARCH NOTES ---\n{research_text}\n---\n\n"
            f"--- RETRIEVED KNOWLEDGE CONTEXT ---\n{context_text}\n--- END CONTEXT ---\n\n"
            f"User Question: {state.message}\n\n"
            f"Answer:"
        )

        tokens: list[str] = []
        async for token in self.response.llm.stream_complete(user_prompt, system=system_prompt):
            tokens.append(token)
            yield f"event: token\ndata: {json.dumps(token)}\n\n"

        state.answer = "".join(tokens).strip()
        state.event("ResponseSynthesizer", "completed", "Streamed final response")

        # Run post-response agents (Validation, AdminMonitoring)
        post_agents = [self.validation, self.admin]
        for agent in post_agents:
            prev_len = len(state.events)
            state = await agent.run(state)
            for evt in state.events[prev_len:]:
                yield f"event: agent\ndata: {evt.model_dump_json()}\n\n"

        # Final done event
        final_response = ChatResponse(
            answer=state.answer,
            intent=state.intent,
            citations=state.context,
            agent_events=state.events,
        )
        yield f"event: done\ndata: {final_response.model_dump_json()}\n\n"


# Global singleton
orchestrator = AgentOrchestrator()


def get_agent_orchestrator() -> AgentOrchestrator:
    return orchestrator
