"""
workflows.py — Schemas for Workflow Automation & Enterprise Tools
===================================================================
WHAT THIS DOES:
  Defines type-safe Pydantic models for:
  - Enterprise Tool specifications & parameter schemas
  - Multi-step workflow execution requests and DAG steps
  - Detailed execution traces and historical run summaries
"""

from typing import Any
from pydantic import BaseModel, Field


class ToolInfo(BaseModel):
    """Metadata describing a registered enterprise tool."""
    name: str = Field(description="Unique tool identifier (e.g. 'create_task')")
    description: str = Field(description="Functional purpose of the tool")
    category: str = Field(default="general", description="Category grouping")
    parameters: dict[str, Any] = Field(default_factory=dict, description="JSON Schema of required/optional arguments")


class WorkflowStep(BaseModel):
    """A discrete execution step in an automated workflow."""
    step_id: str
    name: str
    tool: str
    status: str = Field(default="pending", description="'pending' | 'running' | 'completed' | 'failed'")
    detail: str = ""
    output: dict[str, Any] = Field(default_factory=dict)
    started_at: str
    completed_at: str


class WorkflowRunRequest(BaseModel):
    """Payload to trigger an automated workflow execution."""
    name: str = Field(default="Enterprise Automation Workflow", description="Human-readable title")
    objective: str = Field(min_length=3, description="Goal to achieve (e.g. 'Create task for Q3 security audit')")
    inputs: dict[str, Any] = Field(default_factory=dict, description="Input parameters passed to tools")
    tools: list[str] = Field(default_factory=list, description="Explicit tools to invoke (or empty for auto-planning)")


class WorkflowRunResponse(BaseModel):
    """Full execution response including step-by-step trace."""
    run_id: str
    name: str
    objective: str
    status: str = Field(default="completed", description="'completed' | 'failed'")
    workspace_id: str
    steps: list[WorkflowStep]
    result: dict[str, Any]
    created_at: str
    completed_at: str


class WorkflowRunSummary(BaseModel):
    """Compact summary of a previous workflow run."""
    run_id: str
    name: str
    objective: str
    status: str
    step_count: int
    created_at: str
