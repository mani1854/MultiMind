"""
workflows.py — Workflow Automation & Tool Orchestration Endpoints
==================================================================
WHAT THIS DOES:
  Exposes REST APIs to trigger automated enterprise workflows,
  list registered tools, and inspect step-by-step execution traces.

ENDPOINTS:
  - POST /api/v1/workflows/run        → Trigger workflow execution
  - GET  /api/v1/workflows/tools      → List registered enterprise tools
  - GET  /api/v1/workflows/runs       → List historical workflow runs
  - GET  /api/v1/workflows/runs/{id}  → Retrieve step execution details
"""

from fastapi import APIRouter, Depends, Path

from app.core.security import require_principal
from app.schemas.workflows import (
    ToolInfo,
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowRunSummary,
)
from app.services.tools.registry import ToolRegistry, get_tool_registry
from app.services.workflows.engine import WorkflowEngine, get_workflow_engine

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post(
    "/run",
    response_model=WorkflowRunResponse,
    summary="Execute an automated enterprise workflow with step tracing",
)
async def run_workflow(
    payload: WorkflowRunRequest,
    principal: dict = Depends(require_principal),
    engine: WorkflowEngine = Depends(get_workflow_engine),
) -> WorkflowRunResponse:
    """
    Decomposes the natural language objective, selects appropriate tools,
    and executes the tool DAG sequentially.
    """
    workspace_id = principal.get("workspace_id", "demo-workspace")
    user_id = principal.get("sub", "demo-admin")

    return await engine.run(
        request=payload,
        workspace_id=workspace_id,
        user_id=user_id,
    )


@router.get(
    "/tools",
    response_model=list[ToolInfo],
    summary="List all available enterprise tools and their JSON schemas",
)
async def list_tools(
    principal: dict = Depends(require_principal),
    registry: ToolRegistry = Depends(get_tool_registry),
) -> list[ToolInfo]:
    """Returns definitions, descriptions, and parameter schemas for registered tools."""
    return registry.list_tools()


@router.get(
    "/runs",
    response_model=list[WorkflowRunSummary],
    summary="List historical workflow runs for the caller's workspace",
)
async def list_workflow_runs(
    principal: dict = Depends(require_principal),
    engine: WorkflowEngine = Depends(get_workflow_engine),
) -> list[WorkflowRunSummary]:
    """Retrieves summaries of previous workflow executions."""
    workspace_id = principal.get("workspace_id", "demo-workspace")
    return await engine.list_runs(workspace_id=workspace_id)


@router.get(
    "/runs/{run_id}",
    response_model=WorkflowRunResponse,
    summary="Get detailed step-by-step trace for a specific workflow run",
)
async def get_workflow_run_details(
    run_id: str = Path(..., description="Unique Workflow Run ID"),
    principal: dict = Depends(require_principal),
    engine: WorkflowEngine = Depends(get_workflow_engine),
) -> WorkflowRunResponse:
    """Returns complete execution details including inputs, step timing, and outputs."""
    workspace_id = principal.get("workspace_id", "demo-workspace")
    return await engine.get_run(run_id=run_id, workspace_id=workspace_id)
