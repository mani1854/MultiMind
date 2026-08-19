"""
auth.py — Authentication Endpoints
====================================
WHAT THIS DOES:
  Exposes REST APIs for user registration, login, token refresh, and profile retrieval.

ENDPOINTS:
  - POST /api/v1/auth/register → Create a new user + workspace
  - POST /api/v1/auth/login    → Authenticate with email/password, returns JWT tokens
  - POST /api/v1/auth/refresh  → Exchange a valid refresh token for a new access token
  - GET  /api/v1/auth/me       → Return profile of the currently logged-in user
"""

from fastapi import APIRouter, Depends, status

from app.core.security import require_principal
from app.schemas.auth import (
    LoginRequest,
    PrincipalResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserRegisterRequest,
)
from app.services.auth import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: UserRegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Register a new user and assign them to a workspace with a specific role.
    Returns access & refresh tokens immediately upon registration.
    """
    return await service.register(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Authenticate user using email and password.
    Returns JWT access_token and refresh_token.
    """
    return await service.login(payload.email, payload.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Generate a new access token using a valid refresh token.
    Enables seamless token rotation without re-authenticating with passwords.
    """
    return await service.refresh_token(payload.refresh_token)


@router.get("/me", response_model=PrincipalResponse)
async def get_current_user_profile(
    principal: dict = Depends(require_principal),
    service: AuthService = Depends(get_auth_service),
) -> PrincipalResponse:
    """
    Protected Route:
    Returns identity and workspace details of the authenticated user.
    Requires `Authorization: Bearer <access_token>`.
    """
    return await service.get_principal(principal)
