from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(slots=True)
class ToolRequest:
    """Internal request for a tool invocation requested by the model."""

    tool_name: str
    arguments: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class AgentDecision:
    """Internal decision returned by an LLM adapter."""

    mode: Literal["answer", "tools"]
    message: str
    tool_requests: list[ToolRequest] = field(default_factory=list)
    raw_output: str | None = None