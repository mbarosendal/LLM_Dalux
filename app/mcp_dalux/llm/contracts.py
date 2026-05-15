from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


class LLMError(RuntimeError):
    """Raised when there's an error communicating with a language model."""

    pass


@dataclass(slots=True)
class ToolRequest:
    """Internal request for a tool invocation requested by the model."""

    tool_name: str
    arguments: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class AgentDecision:
    """Internal decision returned by an LLM adapter."""

    mode: Literal["answer", "tools"]
    response: str
    tool_requests: list[ToolRequest] = field(default_factory=list)
    raw_output: str | None = None
