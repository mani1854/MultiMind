"""
test_auth.py — Phase 2 Authentication & RBAC Tests
===================================================
Covers:
  - Login with valid / invalid credentials
  - Protected endpoints with JWT Bearer tokens
  - User registration & duplicate prevention
  - Refresh token rotation
  - Role-Based Access Control (RBAC 200 vs 403 checks)
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_demo_admin():
    """Verify demo admin can log in and receives access & refresh tokens."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@omnimind.local", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "admin"
    assert data["workspace_id"] == "demo-workspace"


def test_login_invalid_password():
    """Verify incorrect password returns 401 Unauthorized."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@omnimind.local", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_auth_me_unauthorized():
    """Protected /auth/me without Bearer token returns 401."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_auth_me_authorized():
    """Access /auth/me with valid Bearer token returns user profile."""
    # 1. Login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@omnimind.local", "password": "admin123"},
    )
    token = login_resp.json()["access_token"]

    # 2. Query /auth/me
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    profile = response.json()
    assert profile["email"] == "admin@omnimind.local"
    assert profile["role"] == "admin"
    assert profile["workspace_id"] == "demo-workspace"


def test_user_registration_and_login():
    """Register a new employee/member, receive tokens, and verify profile."""
    reg_payload = {
        "email": "sarah.connor@cyberdyne.io",
        "password": "SecurePassword123!",
        "full_name": "Sarah Connor",
        "workspace_name": "Resistance HQ",
        "role": "member",
    }
    # 1. Register
    reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    tokens = reg_resp.json()
    assert "access_token" in tokens
    assert tokens["role"] == "member"

    # 2. Login with newly registered user
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": reg_payload["email"], "password": reg_payload["password"]},
    )
    assert login_resp.status_code == 200

    # 3. Check profile
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "sarah.connor@cyberdyne.io"
    assert me_data["workspace_name"] == "Resistance HQ"
    assert me_data["role"] == "member"


def test_duplicate_registration_fails():
    """Registering an already existing email returns 409 Conflict."""
    payload = {
        "email": "duplicate.user@example.com",
        "password": "password123",
        "full_name": "Duplicate User",
        "workspace_name": "Team A",
        "role": "member",
    }
    resp1 = client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 409


def test_refresh_token_rotation():
    """Exchanging a refresh token issues a new access token."""
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@omnimind.local", "password": "admin123"},
    )
    refresh_tok = login_resp.json()["refresh_token"]

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_tok},
    )
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens

    # Verify new access token works
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"},
    )
    assert me_resp.status_code == 200


def test_rbac_admin_allowed_member_forbidden():
    """
    RBAC Verification:
    - Admin role -> 200 OK for /api/v1/admin/health
    - Member role -> 403 Forbidden for /api/v1/admin/health
    """
    # 1. Admin login & access
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@omnimind.local", "password": "admin123"},
    )
    admin_token = admin_login.json()["access_token"]

    admin_health_resp = client.get(
        "/api/v1/admin/health",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert admin_health_resp.status_code == 200
    assert admin_health_resp.json()["status"] == "operational"

    # 2. Member registration & attempt access to admin endpoint
    member_reg = client.post(
        "/api/v1/auth/register",
        json={
            "email": "regular.dev@omnimind.local",
            "password": "devpassword123",
            "full_name": "Dev Member",
            "workspace_name": "Engineering",
            "role": "member",
        },
    )
    member_token = member_reg.json()["access_token"]

    forbidden_resp = client.get(
        "/api/v1/admin/health",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert forbidden_resp.status_code == 403
    assert "Access forbidden" in forbidden_resp.json()["detail"]
