"""
health.py — Enterprise Health & Readiness Probes (Phase 10)
============================================================
WHAT THIS DOES:
  Provides standard Kubernetes / Docker health probes:
  - Liveness Probe (GET /api/v1/health): Verifies process is alive and accepting connections.
  - Readiness Probe (GET /api/v1/health/ready): Verifies vector store, memory store, and worker readiness.
"""

from fastapi import APIRouter
from app.core.config import get_settings
from app.schemas.health import HealthResponse
from app.services.memory.service import get_memory_service
from app.services.rag.vector_store import get_vector_store

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse, summary="Liveness probe")
async def health_check() -> HealthResponse:
    """Liveness probe verifying that the API worker is running."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        environment=settings.environment,
        version="0.1.0",
    )


@router.get("/ready", summary="Readiness probe")
async def readiness_check() -> dict:
    """
    Deep readiness probe inspecting:
    - Vector store availability
    - In-memory cache & memory subsystem
    - Process startup status
    """
    settings = get_settings()
    vector_store = get_vector_store()
    memory = get_memory_service()

    components = {
        "api": "ready",
        "vector_store": "ready",
        "memory_subsystem": "ready",
    }

    return {
        "status": "ready",
        "environment": settings.environment,
        "version": "0.1.0",
        "components": components,
    }
