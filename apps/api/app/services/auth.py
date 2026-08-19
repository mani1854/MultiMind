"""
auth.py — Authentication, User Management & Workspace Service
=============================================================
WHAT THIS DOES:
  Manages user registrations, password validation, workspace associations,
  and JWT token lifecycle (generation & rotation).

ARCHITECTURE PATTERN:
  Service Layer pattern: Business logic is decoupled from API controllers (endpoints)
  and database schemas, making the code testable, modular, and easy to migrate to
  PostgreSQL/SQLAlchemy in subsequent phases.
"""

from typing import Any
from uuid import uuid4
from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.schemas.auth import (
    PrincipalResponse,
    TokenResponse,
    UserRegisterRequest,
    UserRole,
)


class UserEntity:
    def __init__(
        self,
        user_id: str,
        email: str,
        full_name: str,
        hashed_password: str,
        role: str,
        workspace_id: str,
        is_active: bool = True,
    ) -> None:
        self.id = user_id
        self.email = email
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.role = role
        self.workspace_id = workspace_id
        self.is_active = is_active


class WorkspaceEntity:
    def __init__(self, workspace_id: str, name: str, slug: str) -> None:
        self.id = workspace_id
        self.name = name
        self.slug = slug


class AuthService:
    """
    Central Authentication and Identity Management Service.
    Maintains workspace isolation and role permissions.
    """

    def __init__(self) -> None:
        # In-memory storage for users and workspaces (seeded with default demo data)
        self._users: dict[str, UserEntity] = {}  # email -> UserEntity
        self._users_by_id: dict[str, UserEntity] = {}  # id -> UserEntity
        self._workspaces: dict[str, WorkspaceEntity] = {}  # id -> WorkspaceEntity

        # Initialize Default Demo Workspace & Admin User
        default_ws = WorkspaceEntity(
            workspace_id="demo-workspace",
            name="Demo Workspace",
            slug="demo-workspace",
        )
        self._workspaces[default_ws.id] = default_ws

        admin_user = UserEntity(
            user_id="demo-admin",
            email="admin@omnimind.local",
            full_name="OmniMind Admin",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN.value,
            workspace_id=default_ws.id,
        )
        self._users[admin_user.email] = admin_user
        self._users_by_id[admin_user.id] = admin_user

    def _generate_tokens(self, user: UserEntity, workspace: WorkspaceEntity) -> TokenResponse:
        """Helper to create access & refresh token pair with relevant claims."""
        claims = {
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "workspace_id": workspace.id,
            "workspace_name": workspace.name,
        }
        access_token = create_access_token(subject=user.id, claims=claims)
        refresh_token = create_refresh_token(subject=user.id, claims={"workspace_id": workspace.id})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            role=user.role,
            workspace_id=workspace.id,
        )

    async def register(self, payload: UserRegisterRequest) -> TokenResponse:
        """Register a new user, create/link workspace, and issue tokens."""
        if payload.email in self._users:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{payload.email}' already exists.",
            )

        # Create or find workspace
        workspace_slug = payload.workspace_name.lower().replace(" ", "-")
        existing_ws = next(
            (ws for ws in self._workspaces.values() if ws.slug == workspace_slug), None
        )
        if not existing_ws:
            new_ws_id = str(uuid4())
            existing_ws = WorkspaceEntity(
                workspace_id=new_ws_id,
                name=payload.workspace_name,
                slug=workspace_slug,
            )
            self._workspaces[new_ws_id] = existing_ws

        # Create user
        new_user_id = str(uuid4())
        new_user = UserEntity(
            user_id=new_user_id,
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=payload.role.value,
            workspace_id=existing_ws.id,
        )
        self._users[new_user.email] = new_user
        self._users_by_id[new_user.id] = new_user

        return self._generate_tokens(new_user, existing_ws)

    async def login(self, email: str, password: str) -> TokenResponse:
        """Verify user credentials and return fresh tokens."""
        user = self._users.get(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated.",
            )

        workspace = self._workspaces.get(user.workspace_id)
        if not workspace:
            workspace = WorkspaceEntity(user.workspace_id, "Default Workspace", "default")
            self._workspaces[workspace.id] = workspace

        return self._generate_tokens(user, workspace)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Validate refresh token and issue a new access/refresh token pair."""
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = payload.get("sub")

        user = self._users_by_id.get(user_id) if user_id else None
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer active or found.",
            )

        workspace = self._workspaces.get(user.workspace_id)
        if not workspace:
            workspace = WorkspaceEntity(user.workspace_id, "Default Workspace", "default")

        return self._generate_tokens(user, workspace)

    async def get_principal(self, principal_claims: dict[str, Any]) -> PrincipalResponse:
        """Resolve current principal information from verified JWT claims."""
        user_id = principal_claims.get("sub", "")
        email = principal_claims.get("email", "")
        role = principal_claims.get("role", "member")
        workspace_id = principal_claims.get("workspace_id", "demo-workspace")
        full_name = principal_claims.get("full_name", email.split("@")[0] if "@" in email else "User")
        workspace_name = principal_claims.get("workspace_name", "Demo Workspace")

        return PrincipalResponse(
            user_id=user_id,
            email=email,
            full_name=full_name,
            role=role,
            workspace_id=workspace_id,
            workspace_name=workspace_name,
        )

    def list_users(self) -> list[dict[str, Any]]:
        """Admin helper: list all registered users."""
        return [
            {
                "user_id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "workspace_id": u.workspace_id,
                "is_active": u.is_active,
            }
            for u in self._users.values()
        ]


# Singleton instance for application dependency injection
auth_service = AuthService()


def get_auth_service() -> AuthService:
    return auth_service
