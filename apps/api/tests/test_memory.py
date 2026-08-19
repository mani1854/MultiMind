"""
test_memory.py — Phase 6 Memory System Tests
=============================================
Covers:
  - Storing semantic facts, episodic events, and user preferences
  - Hybrid vector recall (similarity + importance scoring)
  - User and workspace tenancy isolation
  - Memory deletion workflows
  - Seamless memory context injection into conversational AI chat
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_token(email: str = "admin@omnimind.local", password: str = "admin123") -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def test_create_and_list_memories():
    """Create a user preference memory and verify it appears in the user's list."""
    token = get_auth_token()

    payload = {
        "content": "User prefers concise answers with markdown bullet points.",
        "memory_type": "user_preference",
        "importance_score": 0.85,
        "tags": ["preferences", "style"],
    }

    create_resp = client.post(
        "/api/v1/memory",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert create_resp.status_code == 201
    mem = create_resp.json()
    assert mem["content"] == payload["content"]
    assert mem["importance_score"] == 0.85
    assert "id" in mem

    # List
    list_resp = client.get(
        "/api/v1/memory",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) >= 1
    assert any(i["id"] == mem["id"] for i in items)


def test_hybrid_memory_recall():
    """Verify semantic and importance-weighted recall returns the most relevant fact."""
    token = get_auth_token()

    # Store multiple facts
    facts = [
        {"content": "User is Lead Data Architect on Project Titan.", "importance_score": 0.9, "memory_type": "semantic_fact"},
        {"content": "User is based in the Tokyo regional office.", "importance_score": 0.5, "memory_type": "semantic_fact"},
        {"content": "User prefers dark mode UI themes.", "importance_score": 0.3, "memory_type": "user_preference"},
    ]
    for f in facts:
        client.post("/api/v1/memory", headers={"Authorization": f"Bearer {token}"}, json=f)

    # Recall
    recall_resp = client.post(
        "/api/v1/memory/recall?query=Which project is the user leading?&limit=3",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert recall_resp.status_code == 200
    data = recall_resp.json()
    assert data["count"] >= 1

    top_memory = data["memories"][0]
    assert "Project Titan" in top_memory["content"]
    assert top_memory["relevance_score"] > 0.0


def test_memory_user_isolation():
    """Ensure User B cannot see or recall User A's private memories."""
    # 1. User A stores confidential memory
    token_a = get_auth_token("admin@omnimind.local", "admin123")
    client.post(
        "/api/v1/memory",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "content": "User A secret passkey is AlphaOmega99.",
            "importance_score": 0.95,
            "memory_type": "semantic_fact",
        },
    )

    # 2. Register User B
    reg_b = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user.b@separatecorp.com",
            "password": "Password456!",
            "full_name": "User B",
            "workspace_name": "Corp B",
            "role": "member",
        },
    )
    token_b = reg_b.json()["access_token"]

    # 3. User B recalls memories -> Must NOT contain User A's secret
    recall_b = client.post(
        "/api/v1/memory/recall?query=passkey secret",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert recall_b.status_code == 200
    for item in recall_b.json()["memories"]:
        assert "AlphaOmega99" not in item["content"]


def test_delete_memory():
    """Verify deleting a memory works and subsequent delete returns 404."""
    token = get_auth_token()

    create_resp = client.post(
        "/api/v1/memory",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content": "Temporary session milestone.",
            "memory_type": "episodic_event",
        },
    )
    mem_id = create_resp.json()["id"]

    # Delete
    del_resp = client.delete(
        f"/api/v1/memory/{mem_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Deleting again -> 404
    del_again = client.delete(
        f"/api/v1/memory/{mem_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_again.status_code == 404


def test_chat_with_memory_integration():
    """Verify chat automatically recalls stored memories and adds Memory agent event."""
    token = get_auth_token()

    # 1. Store a memory for the user
    client.post(
        "/api/v1/memory",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "content": "User is Principal AI Architect for the MultiMind platform.",
            "memory_type": "semantic_fact",
            "importance_score": 0.95,
        },
    )

    # 2. Chat with AI
    chat_resp = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "What is my role on the platform?"},
    )
    assert chat_resp.status_code == 200
    data = chat_resp.json()

    # Check that Memory Agent event was executed
    agent_names = [e["agent"] for e in data["agent_events"]]
    assert "Memory" in agent_names
    assert "Router" in agent_names
