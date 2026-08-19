"""
auth.py — Authentication & RBAC Schemas
========================================
WHAT THIS DOES:
  Defines Pydantic models for request bodies and response formats
  related to user authentication, registration, token refresh, and profiles.

CONCEPTS:
  - Email Validation: Validates standard emails as well as enterprise intranet domains (.local, .internal)
  - TokenResponse: Returns both Access Token (short-lived) & Refresh Token (long-lived)
  - PrincipalResponse: Represents the verified user currently authenticated by JWT
"""

from enum import Enum
from pydantic import BaseModel, Field

EMAIL_PATTERN = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z0-9\-.]+$"


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"


class UserRegisterRequest(BaseModel):
    """Payload for POST /api/v1/auth/register"""
    email: str = Field(pattern=EMAIL_PATTERN, examples=["admin@omnimind.local", "user@company.com"])
    password: str = Field(min_length=6, description="Password with minimum 6 characters")
    full_name: str = Field(min_length=1, max_length=120)
    workspace_name: str = Field(default="Default Workspace", min_length=1, max_length=120)
    role: UserRole = Field(default=UserRole.MEMBER, description="Assigned role (admin, manager, member)")


class LoginRequest(BaseModel):
    """Payload for POST /api/v1/auth/login"""
    email: str = Field(pattern=EMAIL_PATTERN, examples=["admin@omnimind.local", "user@company.com"])
    password: str


class RefreshTokenRequest(BaseModel):
    """Payload for POST /api/v1/auth/refresh"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Response returned upon successful login, registration, or refresh"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    workspace_id: str


class PrincipalResponse(BaseModel):
    """Response for GET /api/v1/auth/me (current authenticated user profile)"""
    user_id: str
    email: str
    full_name: str
    role: str
    workspace_id: str
    workspace_name: str


class WorkspaceResponse(BaseModel):
    """Workspace representation"""
    id: str
    name: str
    slug: str
    role: str
