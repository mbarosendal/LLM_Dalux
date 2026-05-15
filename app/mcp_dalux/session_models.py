from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4


@dataclass(slots=True)
class ConversationTurn:
    """One message in the short-lived conversation history."""

    role: Literal["user", "agent"]
    content: str
    timestamp: datetime


@dataclass(slots=True)
class SessionState:
    """Internal source-of-truth model for a persisted HTTP session."""

    session_id: str
    user_id: str | None
    project_id: str | None
    category: Literal["tasks", "files"]
    start_time: datetime
    end_time: datetime
    project_name: str | None = None  # Optional, only used for richer instructions in HTTP mode. MCP mode only consumes project_id.
    history: list[ConversationTurn] = field(default_factory=list)


def add_session_turn(session_state: SessionState, role: Literal["user", "agent"], content: str) -> None:
    """Append a turn to the in-memory chat history."""

    normalized_content = content.strip()
    if not normalized_content:
        return

    session_state.history.append(
        ConversationTurn(
            role=role,
            content=normalized_content,
            timestamp=datetime.now(UTC),
        )
    )


def render_session_history(session_state: SessionState, max_turns: int = 10) -> str:
    """Render the most recent turns as a compact instruction block."""

    if max_turns <= 0 or not session_state.history:
        return ""

    recent_turns = session_state.history[-max_turns:]
    lines = ["KONVERSATIONSHISTORIK:"]
    for turn in recent_turns:
        lines.append(f"- {turn.role}: {turn.content}")
    return "\n".join(lines)


# Use DDD or move to session_service.py if we want to keep all session logic in one place. For now, this is just the data model and factory function.
def create_session_state(project_id: str | None, project_name: str | None, category: str, user_id: str | None = None) -> SessionState:
    """Create a new in-memory session state instance with generated runtime values."""

    now_utc = datetime.now(UTC)
    normalized_category: Literal["tasks", "files"] = "files" if category == "files" else "tasks"

    return SessionState(
        session_id=str(uuid4()),
        user_id=user_id,
        project_id=project_id,
        project_name=project_name,
        category=normalized_category,
        start_time=now_utc,
        end_time=now_utc,
    )


def get_default_session_state(user_id: str | None = None, project_id: str | None = None) -> SessionState:
    """Dummy SessionState used for stdio/MCP startup. MCP instructions only consume a subset of fields, but keeping one shared model avoids bloat."""

    return SessionState(
        session_id="mcp-default-session",
        user_id=user_id,
        project_id=project_id,
        start_time=datetime.now(),
        end_time=datetime.now(),
        category="tasks",
    )
