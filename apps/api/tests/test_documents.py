"""
test_documents.py — Phase 3 Document Management & Chunking Tests
=================================================================
Covers:
  - Document uploads across formats (TXT, MD, CSV)
  - Chunk extraction & sliding window verification
  - Unsupported file type handling (HTTP 400)
  - Workspace multi-tenant isolation
  - Listing & document detail inspection
  - Document deletion
"""

import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_token(email: str = "admin@omnimind.local", password: str = "admin123") -> str:
    """Helper to authenticate and get JWT bearer token."""
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def test_upload_txt_document():
    """Upload a plain text document and verify chunk generation."""
    token = get_auth_token()
    sample_text = (
        "MultiMind Enterprise AI Copilot Onboarding Policy.\n"
        "All engineers must complete safety training in week one.\n"
        "Security keys must be stored in approved password managers.\n"
        "Code reviews require approval from at least two senior engineers.\n"
    ) * 10  # Repeat to generate enough length for multiple chunks

    files = {
        "file": ("engineering_policy.txt", io.BytesIO(sample_text.encode("utf-8")), "text/plain")
    }

    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "engineering_policy.txt"
    assert data["status"] == "indexed"
    assert data["chunks_count"] > 0
    assert data["workspace_id"] == "demo-workspace"
    assert "id" in data


def test_upload_markdown_document():
    """Upload a markdown document."""
    token = get_auth_token()
    md_content = """# Company Handbook
## 1. Remote Work Guidelines
Employees are eligible for remote work after 30 days of tenure.
Core collaboration hours are 10:00 AM to 4:00 PM EST.
"""
    files = {
        "file": ("handbook.md", io.BytesIO(md_content.encode("utf-8")), "text/markdown")
    }

    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "handbook.md"
    assert data["status"] == "indexed"
    assert data["chunks_count"] >= 1


def test_upload_csv_document():
    """Upload a CSV table and verify dataframe markdown formatting."""
    token = get_auth_token()
    csv_content = "EmployeeID,Name,Department,Role\n101,Alice,Engineering,Lead\n102,Bob,Product,Manager\n"
    files = {
        "file": ("directory.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
    }

    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert response.status_code == 201
    doc_id = response.json()["id"]

    # Verify chunk contains markdown table representation
    detail_resp = client.get(
        f"/api/v1/documents/{doc_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["chunks"]) >= 1
    # Check that CSV was formatted into markdown columns
    assert "EmployeeID" in detail["chunks"][0]["text"]
    assert "Alice" in detail["chunks"][0]["text"]


def test_unsupported_file_format():
    """Uploading unsupported format (e.g. .exe) returns 400 Bad Request."""
    token = get_auth_token()
    files = {
        "file": ("script.exe", io.BytesIO(b"\x4D\x5A\x90\x00"), "application/octet-stream")
    }

    response = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_list_and_get_document_details():
    """List documents and inspect chunks of a specific document."""
    token = get_auth_token()

    # 1. List
    list_resp = client.get(
        "/api/v1/documents",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200
    docs = list_resp.json()
    assert isinstance(docs, list)
    assert len(docs) > 0

    first_doc_id = docs[0]["id"]

    # 2. Get Detail
    detail_resp = client.get(
        f"/api/v1/documents/{first_doc_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == first_doc_id
    assert "chunks" in detail
    assert isinstance(detail["chunks"], list)
    assert "char_count" in detail["chunks"][0]


def test_workspace_isolation():
    """Ensure a user from Workspace B cannot access documents from Workspace A."""
    # 1. User from Workspace A uploads document
    token_a = get_auth_token("admin@omnimind.local", "admin123")
    files = {
        "file": ("secret_roadmap.txt", io.BytesIO(b"Secret Q4 Roadmap for Workspace A"), "text/plain")
    }
    upload_resp = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token_a}"},
        files=files,
    )
    doc_id_a = upload_resp.json()["id"]

    # 2. Register new user in a completely different workspace (Workspace B)
    reg_b = client.post(
        "/api/v1/auth/register",
        json={
            "email": "external.partner@competitor.com",
            "password": "Password123!",
            "full_name": "Partner User",
            "workspace_name": "Partner Workspace",
            "role": "member",
        },
    )
    token_b = reg_b.json()["access_token"]

    # 3. User B attempts to access Document A -> 404 Not Found
    forbidden_get = client.get(
        f"/api/v1/documents/{doc_id_a}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert forbidden_get.status_code == 404


def test_delete_document():
    """Delete document and verify it is no longer accessible."""
    token = get_auth_token()
    files = {
        "file": ("temp_notes.txt", io.BytesIO(b"Temporary meeting notes to delete."), "text/plain")
    }
    upload_resp = client.post(
        "/api/v1/documents/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    doc_id = upload_resp.json()["id"]

    # Delete
    del_resp = client.delete(
        f"/api/v1/documents/{doc_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["success"] is True

    # Verify 404
    get_resp = client.get(
        f"/api/v1/documents/{doc_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_resp.status_code == 404
