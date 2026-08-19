from functools import lru_cache

from app.services.agents.orchestrator import AgentOrchestrator
from app.services.memory.service import MemoryService
from app.services.rag.service import RAGService
from app.services.workflows.engine import WorkflowEngine


@lru_cache
def get_orchestrator() -> AgentOrchestrator:
    return AgentOrchestrator()


@lru_cache
def get_rag_service() -> RAGService:
    return RAGService()


@lru_cache
def get_memory_service() -> MemoryService:
    return MemoryService()


@lru_cache
def get_workflow_engine() -> WorkflowEngine:
    return WorkflowEngine()

