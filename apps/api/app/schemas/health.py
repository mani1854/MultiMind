"""
health.py — Health Check Response Schemas
==========================================
WHAT THIS DOES:
  Defines the SHAPE of the JSON response for health check endpoints.

  When FastAPI sees `response_model=HealthResponse`, it:
    1. Validates our response matches this shape
    2. Auto-generates OpenAPI documentation
    3. Strips any extra fields we accidentally included

EXAMPLE OUTPUT:
  {"status": "ok", "environment": "development", "version": "0.1.0"}
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Schema for GET /health responses."""
    status: str          # "ok" or "error"
    environment: str     # "development", "staging", "production"
    version: str         # App version from settings
