"""
test_chat.py — Phase 5 AI Chat, LLM Gateway & SSE Streaming Tests
==================================================================
Covers:
  - Grounded RAG question answering with citations
  - Traceable agent lifecycle events
  - Server-Sent Events (SSE) token streaming
  - Multi-turn conversation history
  - Authentication checks on chat endpoints
"""

import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_token(email: str = "admin@omnimind.local", password: str = "admin123") -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def test_chat_unauthenticated_fails():
    """Calling /api/v1/chat without Bearer token returns 401."""
    response = client.post("/api/v1/chat", json={"message": "What is the policy?"})
    assert response.status_code == 401


def test_chat_grounded_qa_with_citations():
    """Upload document, query chat endpoint, and verify answer + citations."""
    token = get_auth_token()

    # 1. Ingest test policy document
    policy_doc = (
        "MultiMind Hybrid Work Framework:\n"
        "Employees are permitted to work remotely up to 3 days per week.\n"
        "Remote work days require prior email confirmation with the team lead.\n"
        "Equipment stipends of $500 are provided upon joining for home office setup.\n"
    )
    files = {
        "file": ("hybrid_work_policy.txt", io.BytesIO(policy_doc.encode("utf-8")), "text/plain")
    }
    upload_resp = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert upload_resp.status_code == 201
    doc_id = upload_resp.json()["id"]

    # 2. Chat with AI
    chat_resp = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "How many days per week can employees work remotely?"},
    )
    assert chat_resp.status_code == 200
    data = chat_resp.json()

    # Verify answer and citation attribution
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert len(data["citations"]) >= 1

    citation = data["citations"][0]
    assert citation["source_id"] == doc_id
    assert citation["title"] == "hybrid_work_policy.txt"
    assert "3 days per week" in citation["snippet"]
    assert citation["score"] > 0.0

    # Verify execution trace events
    assert len(data["agent_events"]) >= 2
    agent_names = [e["agent"] for e in data["agent_events"]]
    assert "Router" in agent_names
    assert "Retrieval" in agent_names


def test_chat_with_conversation_history():
    """Verify chat handles multi-turn conversation history."""
    token = get_auth_token()

    payload = {
        "message": "Can you summarize the equipment stipend part?",
        "history": [
            {"role": "user", "content": "What is the hybrid work policy?"},
            {"role": "assistant", "content": "Employees can work remotely 3 days per week."},
        ],
    }

    response = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data


def test_chat_sse_streaming():
    """Verify Server-Sent Events (SSE) streaming token delivery."""
    token = get_auth_token()

    # Request with stream=True
    response = client.post(
        "/api/v1/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "Explain the equipment stipend policy",
            "stream": True,
        },
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    # Consume stream chunks
    stream_content = response.text
    assert "event: agent" in stream_content
    assert "event: token" in stream_content
    assert "event: done" in stream_content


def test_dedicated_chat_stream_endpoint():
    """Verify POST /api/v1/chat/stream dedicated route."""
    token = get_auth_token()

    response = client.post(
        "/api/v1/chat/stream",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "What is the policy?"},
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "event: done" in response.text
