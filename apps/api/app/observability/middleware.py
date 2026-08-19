"""
middleware.py — Request Correlation ID & Telemetry Middleware
==============================================================
WHAT THIS DOES:
  - Injects a unique `X-Request-ID` into every HTTP transaction.
  - Measures request latency with sub-millisecond precision.
  - Updates Prometheus metrics counters.
  - Emits structured JSON access logs for log aggregation (Datadog, Loki, CloudWatch).
"""

import time
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import logger
from app.observability.metrics import get_metrics_collector


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware injecting Correlation IDs, recording metrics, and logging access events.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()

        # Extract or generate X-Request-ID
        request_id = request.headers.get("X-Request-ID") or f"req-{uuid4().hex[:12]}"

        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "http.request.failed",
                method=request.method,
                path=request.url.path,
                error=str(exc),
                duration_ms=round(duration_ms, 2),
                request_id=request_id,
            )
            raise exc

        duration_seconds = time.time() - start_time
        duration_ms = duration_seconds * 1000

        # Inject correlation header
        response.headers["X-Request-ID"] = request_id

        # Update Prometheus metrics
        collector = get_metrics_collector()
        collector.record_http_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_seconds=duration_seconds,
        )

        # Emit structured access log (excluding noisy health/metrics polling)
        if request.url.path not in ["/health", "/metrics", "/api/v1/health"]:
            logger.info(
                "http.request",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration_ms=round(duration_ms, 2),
                request_id=request_id,
            )

        return response
