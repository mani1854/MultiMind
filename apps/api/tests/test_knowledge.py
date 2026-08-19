"""
test_knowledge.py — Phase 4 RAG Pipeline & Vector Search Tests
===============================================================
Covers:
  - Dense embedding generation & unit-norm scaling
  - Cosine similarity metric calculation
  - End-to-End semantic retrieval against indexed documents
  - Top-K ranked results
  - Explicit document re-indexing endpoint
  - Multi-tenant workspace isolation in vector search
  - Vector database collection statistics
"""

import io
from math import sqrt
from fastapi.testclient import TestClient
from app.main import app
from app.services.rag.vector_store import (
    compute_cosine_similarity,
    generate_dense_embedding,
)

client = TestClient(app)


def get_auth_token(email: str = "admin@omnimind.local", password: str = "admin123") -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def test_dense_embedding_generation():
    """Verify embedding produces a 384-dimensional unit vector."""
    text = "Enterprise knowledge management system"
    embedding = generate_dense_embedding(text, dimension=384)

    assert len(embedding) == 384
    # Check L2 Unit Norm: sqrt(sum(v_i^2)) == 1.0
    norm = sqrt(sum(x * x for x in embedding))
    assert round(norm, 5) == 1.0


def test_cosine_similarity_math():
    """Verify cosine similarity mathematical boundaries."""
    vec_a = generate_dense_embedding("Remote working policy guidelines", dimension=384)
    vec_b = generate_dense_embedding("Remote work policy for employees", dimension=384)
    vec_c = generate_dense_embedding("Deep learning computer vision algorithm", dimension=384)

    # Identical vectors = 1.0
    assert round(compute_cosine_similarity(vec_a, vec_a), 4) == 1.0

    # Semantically related texts should have higher similarity than unrelated texts
    sim_ab = compute_cosine_similarity(vec_a, vec_b)
    sim_ac = compute_cosine_similarity(vec_a, vec_c)
    assert sim_ab > sim_ac


def test_e2e_semantic_search():
    """Upload document and verify relevant chunk is retrieved for semantic query."""
    token = get_auth_token()

    policy_text = (
        "MultiMind Vacation and Leave Policy:\n"
        "Full-time employees are entitled to 25 days of annual paid time off (PTO).\n"
        "Sick leaves can be taken up to 10 days per year with medical documentation.\n"
        "Parental leave covers 16 weeks of fully paid leave for all primary caregivers.\n"
    )
    files = {
        "file": ("leave_policy.txt", io.BytesIO(policy_text.encode("utf-8")), "text/plain")
    }

    upload_resp = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert upload_resp.status_code == 201
    doc_id = upload_resp.json()["id"]

    # Execute semantic search
    search_resp = client.post(
        "/api/v1/knowledge/search",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "query": "How many days of paid time off or vacation do employees get?",
            "top_k": 3,
        },
    )
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) >= 1

    top_result = results[0]
    assert top_result["source_id"] == doc_id
    assert "paid time off" in top_result["snippet"]
    assert top_result["score"] > 0.0


def test_explicit_document_reindex():
    """Verify explicit POST /api/v1/knowledge/index/{doc_id} re-indexes chunks."""
    token = get_auth_token()

    doc_text = "Security Architecture: All API endpoints require OAuth2 JWT tokens with HS256 signature."
    files = {
        "file": ("security_guide.txt", io.BytesIO(doc_text.encode("utf-8")), "text/plain")
    }
    upload_resp = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    doc_id = upload_resp.json()["id"]

    index_resp = client.post(
        f"/api/v1/knowledge/index/{doc_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert index_resp.status_code == 200
    data = index_resp.json()
    assert data["document_id"] == doc_id
    assert data["chunks_indexed"] >= 1
    assert data["status"] == "indexed"


def test_vector_workspace_isolation():
    """Verify vector search does not leak chunks across workspaces."""
    # 1. User in Workspace A uploads secret info
    token_a = get_auth_token("admin@omnimind.local", "admin123")
    files = {
        "file": ("confidential_deals.txt", io.BytesIO(b"Project Titan acquisition price is $50M."), "text/plain")
    }
    client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files=files,
    )

    # 2. Register user in Workspace B
    reg_b = client.post(
        "/api/v1/auth/register",
        json={
            "email": "investor@externalfunds.com",
            "password": "Password789!",
            "full_name": "External Investor",
            "workspace_name": "External Workspace",
            "role": "member",
        },
    )
    token_b = reg_b.json()["access_token"]

    # 3. User B searches for Project Titan in Workspace B -> 0 results
    search_b = client.post(
        "/api/v1/knowledge/search",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"query": "Project Titan acquisition price"},
    )
    assert search_b.status_code == 200
    results_b = search_b.json()
    # Ensure no leaked confidential chunks from Workspace A
    for res in results_b:
        assert "Project Titan" not in res["snippet"]


def test_knowledge_stats():
    """Verify GET /api/v1/knowledge/stats returns collection metadata."""
    token = get_auth_token()
    stats_resp = client.get(
        "/api/v1/knowledge/stats",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert stats_resp.status_code == 200
    data = stats_resp.json()
    assert data["vector_dimension"] == 384
    assert data["collection_name"] == "enterprise_knowledge"
    assert "total_vectors_indexed" in data
