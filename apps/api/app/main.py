"""
main.py — Application Factory & Observability Middleware (Phase 10)
====================================================================
WHAT THIS DOES:
  Creates and configures the MultiMind FastAPI application.
  Mounts:
  - Prometheus `/metrics` endpoint
  - Request Correlation ID & Latency Logging Middleware
  - CORS Middleware for Next.js frontend communication
  - Versioned API router `/api/v1`
  - Root Liveness & Readiness Probes (`/health`, `/ready`)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, logger
from app.observability.metrics import get_metrics_collector
from app.observability.middleware import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager (Startup and Shutdown hooks).
    """
    logger.info("api.starting", environment=get_settings().environment)
    yield
    logger.info("api.stopped")


def create_app() -> FastAPI:
    """
    Application Factory configuring middleware, routers, and observability.
    """
    # 1. Initialize structured logging
    configure_logging()
    settings = get_settings()

    # 2. Instantiate FastAPI app
    app = FastAPI(
        title="MultiMind — Enterprise Knowledge Copilot",
        version="0.1.0",
        description="Multi-Agent RAG, Long-Term Memory, and Workflow Automation Platform.",
        lifespan=lifespan,
    )

    # 3. Add Request Logging & Correlation ID Middleware
    app.add_middleware(RequestLoggingMiddleware)

    # 4. Add CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 5. Mount Prometheus Metrics Endpoint
    @app.get("/metrics", response_class=PlainTextResponse, summary="Prometheus Metrics Exposition")
    async def prometheus_metrics() -> str:
        """Exposes Prometheus-compatible scrapable metrics."""
        return get_metrics_collector().export_prometheus()

    # 6. Root Liveness & Readiness Probes
    @app.get("/health", summary="Root Liveness Probe")
    async def root_health() -> dict:
        return {"status": "ok", "environment": settings.environment}

    @app.get("/ready", summary="Root Readiness Probe")
    async def root_ready() -> dict:
        return {"status": "ready", "environment": settings.environment}

    # 7. Mount Master v1 Router
    app.include_router(api_router)

    return app


# Create the application instance
app = create_app()
