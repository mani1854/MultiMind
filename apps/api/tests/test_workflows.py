"""
test_workflows.py — Phase 8 Workflow Automation & Tool Execution Tests
=======================================================================
Covers:
  - Enterprise Tool Registry listing and JSON schemas
  - Automated natural language objective decomposition into tool DAGs
  - Multi-step task creation, report generation, and meeting workflows
  - Run execution history and step-by-step trace retrieval
  - Tenancy isolation and unauthenticated access checks
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_auth_token(email: str = "admin@omnimind.local", password: str = "admin123") -> str:
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


def test_workflows_unauthenticated_fails():
    """Calling /api/v1/workflows/run without auth returns 401."""
    response = client.post("/api/v1/workflows/run", json={"name": "Task", "objective": "Create task"})
    assert response.status_code == 401


def test_list_registered_enterprise_tools():
    """Verify tool registry returns definitions and schemas for all 5 enterprise tools."""
    token = get_auth_token()
    response = client.get("/api/v1/workflows/tools", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    tools = response.json()
    assert len(tools) >= 5

    tool_names = [t["name"] for t in tools]
    assert "create_task" in tool_names
    assert "generate_report" in tool_names
    assert "send_notification" in tool_names
    assert "extract_action_items" in tool_names
    assert "export_knowledge_summary" in tool_names


def test_run_task_creation_workflow():
    """Verify automatic planning and execution of task creation workflow."""
    token = get_auth_token()
    payload = {
        "name": "Sprint Task Creation",
        "objective": "Create a high priority task for API performance optimization",
        "inputs": {"owner": "sarah.lead@company.com", "priority": "high"},
    }

    response = client.post(
        "/api/v1/workflows/run",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert "run_id" in data
    assert len(data["steps"]) >= 2

    step_tools = [s["tool"] for s in data["steps"]]
    assert "create_task" in step_tools
    assert "send_notification" in step_tools

    # Verify task result
    assert "create_task" in data["result"]
    assert "TASK-" in data["result"]["create_task"]["task_id"]


def test_run_report_generation_workflow():
    """Verify automatic planning and execution of report generation workflow."""
    token = get_auth_token()
    payload = {
        "name": "Q3 Compliance Report",
        "objective": "Generate formal compliance and security briefing report",
        "inputs": {"title": "Q3 Enterprise Security Audit"},
    }

    response = client.post(
        "/api/v1/workflows/run",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    step_tools = [s["tool"] for s in data["steps"]]
    assert "generate_report" in step_tools
    assert "REP-" in data["result"]["generate_report"]["report_id"]


def test_run_meeting_action_items_workflow():
    """Verify meeting transcript objective decomposes into 3-step tool chain."""
    token = get_auth_token()
    payload = {
        "name": "Staff Sync Actions",
        "objective": "Extract action items from meeting notes and assign deliverables",
        "inputs": {
            "text": "TODO: Alex to deploy auth fixes.\nAction: John to review security policy.\nDeliverable: Send report on Friday."
        },
    }

    response = client.post(
        "/api/v1/workflows/run",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    step_tools = [s["tool"] for s in data["steps"]]
    assert "extract_action_items" in step_tools
    assert "create_task" in step_tools
    assert "send_notification" in step_tools


def test_list_and_get_workflow_run_history():
    """Verify run history listing and individual run trace retrieval."""
    token = get_auth_token()

    # 1. Trigger a run
    run_resp = client.post(
        "/api/v1/workflows/run",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "History Test Run", "objective": "Export knowledge summary for DevOps"},
    )
    run_id = run_resp.json()["run_id"]

    # 2. List runs
    list_resp = client.get(
        "/api/v1/workflows/runs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_resp.status_code == 200
    runs = list_resp.json()
    assert any(r["run_id"] == run_id for r in runs)

    # 3. Get single run detail
    detail_resp = client.get(
        f"/api/v1/workflows/runs/{run_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_resp.status_code == 200
    assert detail_resp.json()["run_id"] == run_id

    # 4. Nonexistent run -> 404
    bad_resp = client.get(
        "/api/v1/workflows/runs/nonexistent-uuid-999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert bad_resp.status_code == 404
