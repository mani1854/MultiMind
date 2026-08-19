"""
test_orchestrator.py — Phase 7 Multi-Agent Orchestration Tests
===============================================================
Covers:
  - Blackboard pipeline execution across 11 specialist agents
  - Intent routing accuracy (meeting, report, workflow, retrieval, summarization)
  - Real-time SSE streaming across agent lifecycle events
  - Validation and Admin Monitoring telemetry
"""

import pytest
from app.schemas.chat import ChatRequest
from app.services.agents.orchestrator import AgentOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_full_pipeline_execution():
    """Verify all specialist agents execute and record trace events."""
    orchestrator = AgentOrchestrator()
    request = ChatRequest(message="What is the remote work policy for employees?")
    response = await orchestrator.run(request=request, workspace_id="test-workspace", user_id="test-user")

    assert response.answer is not None
    assert len(response.answer) > 0
    assert response.intent in ["retrieval", "general", "summarization", "report_generation"]

    # Verify agent lifecycle event coverage
    agent_names = [evt.agent for evt in response.agent_events]
    assert "Router" in agent_names
    assert "Memory" in agent_names
    assert "Retrieval" in agent_names
    assert "Research" in agent_names
    assert "ResponseSynthesizer" in agent_names
    assert "Validation" in agent_names
    assert "AdminMonitoring" in agent_names


@pytest.mark.asyncio
async def test_meeting_intelligence_intent_routing():
    """Verify meeting queries trigger MeetingIntelligenceAgent."""
    orchestrator = AgentOrchestrator()
    request = ChatRequest(message="Extract action items and decisions from today's staff meeting")
    response = await orchestrator.run(request=request, workspace_id="test-workspace", user_id="test-user")

    assert response.intent == "meeting_intelligence"
    meeting_events = [e for e in response.agent_events if e.agent == "MeetingIntelligence"]
    assert len(meeting_events) == 1
    assert meeting_events[0].status == "completed"


@pytest.mark.asyncio
async def test_report_generation_intent_routing():
    """Verify report queries trigger ReportGenerationAgent."""
    orchestrator = AgentOrchestrator()
    request = ChatRequest(message="Generate a formal report on cloud infrastructure spending")
    response = await orchestrator.run(request=request, workspace_id="test-workspace", user_id="test-user")

    assert response.intent == "report_generation"
    report_events = [e for e in response.agent_events if e.agent == "ReportGeneration"]
    assert len(report_events) == 1
    assert report_events[0].status == "completed"


@pytest.mark.asyncio
async def test_workflow_automation_intent_routing():
    """Verify automation queries trigger WorkflowAutomationAgent."""
    orchestrator = AgentOrchestrator()
    request = ChatRequest(message="Automate workflow and create task for lead engineer review")
    response = await orchestrator.run(request=request, workspace_id="test-workspace", user_id="test-user")

    assert response.intent == "workflow"
    wf_events = [e for e in response.agent_events if e.agent == "WorkflowAutomation"]
    assert len(wf_events) == 1
    assert wf_events[0].status == "completed"


@pytest.mark.asyncio
async def test_multi_agent_sse_streaming():
    """Verify orchestrator stream yields live agent events, tokens, and done payload."""
    orchestrator = AgentOrchestrator()
    request = ChatRequest(message="Explain the company security guidelines")

    stream_chunks = []
    async for chunk in orchestrator.stream(request=request, workspace_id="test-workspace", user_id="test-user"):
        stream_chunks.append(chunk)

    full_stream = "".join(stream_chunks)
    assert "event: agent" in full_stream
    assert "event: token" in full_stream
    assert "event: done" in full_stream
