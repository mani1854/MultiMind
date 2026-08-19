"""
test_health.py — Phase 1 Tests
================================
Tests the health endpoints to verify the foundation works.

HOW TO RUN:
  cd apps/api
  pytest tests/ -v
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_health():
    """GET /health should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data


def test_api_v1_health():
    """GET /api/v1/health should return status, environment, and version."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["environment"] == "development"
    assert data["version"] == "0.1.0"


def test_openapi_docs_available():
    """FastAPI auto-generates docs at /docs."""
    response = client.get("/docs")
    assert response.status_code == 200
