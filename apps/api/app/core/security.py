"""
security.py — Cryptography, JWT Tokens & Role-Based Access Control (RBAC)
========================================================================
WHAT THIS DOES:
  1. Password Hashing: Uses direct bcrypt hashing with salt generation.
  2. Token Generation: Creates signed Access Tokens (short-lived) & Refresh Tokens (long-lived).
  3. FastAPI Dependency Injection:
     - `require_principal`: Extracts & verifies the Bearer JWT token from request headers.
     - `require_role("admin", "manager")`: Ensures only authorized roles can access endpoints.

HOW AUTHENTICATION VS AUTHORIZATION WORKS:
  - Authentication ("Who are you?"): `require_principal` checks the JWT signature.
  - Authorization ("What are you allowed to do?"): `require_role` checks if your role has permission.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import get_settings

# Tells FastAPI where to get tokens from (OAuth2 standard: Authorization: Bearer <token>)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with automatic salt generation."""
    # Truncate to 72 bytes as per bcrypt specification
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plaintext password matches the stored bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(subject: str, claims: dict[str, Any] | None = None) -> str:
    """
    Generate a signed short-lived JWT Access Token.
    Subject is typically user_id or email.
    """
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": subject,
        "type": "access",
        "exp": expires_at,
        **(claims or {}),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str, claims: dict[str, Any] | None = None) -> str:
    """
    Generate a signed long-lived JWT Refresh Token (e.g. 7 days).
    Used exclusively to obtain a fresh access token without re-entering credentials.
    """
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload = {
        "sub": subject,
        "type": "refresh",
        "exp": expires_at,
        **(claims or {}),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    """
    Decode, verify signature, and check expiration & token type.
    Raises HTTPException(401) on any failure.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        token_type = payload.get("type", "access")
        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {expected_type} token.",
            )
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def require_principal(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    """
    FastAPI Dependency:
    Extracts Bearer token from HTTP Authorization header,
    verifies it, and returns the authenticated user payload.
    """
    return decode_token(token, expected_type="access")


def require_role(*allowed_roles: str):
    """
    FastAPI Dependency Factory for Role-Based Access Control (RBAC):
    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role("admin"))])
    """
    async def dependency(principal: dict[str, Any] = Depends(require_principal)) -> dict[str, Any]:
        user_role = principal.get("role", "member")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of the following roles: {', '.join(allowed_roles)}",
            )
        return principal

    return dependency
