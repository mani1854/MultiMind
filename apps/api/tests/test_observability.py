"""
test_observability.py — Phase 10 Observability, Metrics & Health Tests
======================================================================
Covers:
  - Prometheus metrics exposition endpoint (/metrics)
  - Correlation ID (X-Request-ID) header injection and propagation
  - Liveness and Deep Readiness probes (/health/ready)
  - Metrics counter increments on HTTP requests
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_prometheus_metrics_endpoint():
    """Verify /metrics returns standard Prometheus text format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    text = response.text
    assert "# HELP multimind_uptime_seconds" in text
    assert "# HELP multimind_http_requests_total" in text
    assert "multimind_uptime_seconds" in text


def test_request_correlation_id_header_injected():
    """Verify X-Request-ID header is automatically generated and returned."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert response.headers["x-request-id"].startswith("req-")


def test_custom_correlation_id_preserved():
    """Verify client-supplied X-Request-ID is preserved and propagated."""
    custom_id = "trace-client-abc-999"
    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == custom_id


def test_deep_readiness_probe():
    """Verify deep readiness probe reports subsystem availability."""
    resp = client.get("/api/v1/health/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert "components" in data
    assert data["components"]["api"] == "ready"
    assert data["components"]["vector_store"] == "ready"
    assert data["components"]["memory_subsystem"] == "ready"

    # Root /ready
    root_resp = client.get("/ready")
    assert root_resp.status_code == 200
    assert root_resp.json()["status"] == "ready"


def test_metrics_counter_increments_after_requests():
    """Verify HTTP requests increment Prometheus metrics counters."""
    # Perform a few requests
    client.get("/api/v1/health")
    client.get("/api/v1/health")

    metrics_resp = client.get("/metrics")
    assert metrics_resp.status_code == 200
    metrics_text = metrics_resp.text
    assert 'multimind_http_requests_total{method="GET",path="/api/v1/health",status="200"}' in metrics_text
