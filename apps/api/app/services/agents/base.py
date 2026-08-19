"""
base.py — Multi-Agent Blackboard State & Base Agent
===================================================
WHAT THIS DOES:
  Defines the shared AgentState (Blackboard Pattern) and base Agent abstraction.

BLACKBOARD PATTERN:
  In multi-agent systems, agents collaborate by reading from and writing to a shared
  state structure (Blackboard). Each specialist inspects prior work, adds domain-specific
  enrichments, and passes the updated state down the execution pipeline.
"""

from dataclasses import dataclass, field
from typing import Any
from app.schemas.chat import AgentEvent, Citation


@dataclass
class AgentState:
    """Shared state object passed through the Multi-Agent pipeline."""
    message: str
    workspace_id: str
    user_id: str = "demo-admin"
    session_id: str = "default-session"
    intent: str = "general"
    context: list[Citation] = field(default_factory=list)
    memories: list[str] = field(default_factory=list)
    research_notes: list[str] = field(default_factory=list)
    action_items: list[str] = field(default_factory=list)
    report_structure: dict[str, Any] = field(default_factory=dict)
    workflow_result: dict[str, Any] | None = None
    validation_status: str = "grounded"
    answer: str = ""
    events: list[AgentEvent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def event(self, agent: str, status: str, detail: str) -> None:
        """Appends an observable lifecycle event to the trace list."""
        self.events.append(AgentEvent(agent=agent, status=status, detail=detail))


class Agent:
    """Abstract base class for all specialist agents."""
    name: str = "agent"

    async def run(self, state: AgentState) -> AgentState:
        """Executes the agent's logic, mutating and returning the shared state."""
        raise NotImplementedError
