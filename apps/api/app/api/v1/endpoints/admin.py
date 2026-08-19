"""
admin.py — Admin & Governance Endpoints (RBAC Demo)
===================================================
WHAT THIS DOES:
  Demonstrates Role-Based Access Control (RBAC).
  These endpoints require the caller to have the "admin" role.
  If a "manager" or "member" attempts access, FastAPI automatically responds with 403 Forbidden.
"""

from typing import Any
from fastapi import APIRouter, Depends

from app.core.security import require_role
from app.services.auth import AuthService, get_auth_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/health")
async def admin_system_health(
    principal: dict = Depends(require_role("admin")),
) -> dict[str, Any]:
    """
    RBAC Protected Endpoint (Admin Only):
    Returns privileged operational metrics and configuration state.
    """
    return {
        "status": "operational",
        "authorized_admin": principal.get("email"),
        "role": principal.get("role"),
        "features": {
            "rbac_enabled": True,
            "multi_tenancy": True,
            "token_rotation": True,
        },
    }


@router.get("/users")
async def list_all_users(
    _: dict = Depends(require_role("admin")),
    service: AuthService = Depends(get_auth_service),
) -> list[dict[str, Any]]:
    """
    RBAC Protected Endpoint (Admin Only):
    Returns all registered users and their respective workspaces.
    """
    return service.list_users()
