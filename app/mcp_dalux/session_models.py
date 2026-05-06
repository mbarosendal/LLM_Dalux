from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4


@dataclass(slots=True)
class ConversationTurn:
    """One message in the short-lived conversation history."""

    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime


@dataclass(slots=True)
class SessionState:
    """Internal source-of-truth model for a persisted HTTP session."""

    session_id: str
    project_name: str
    category: Literal["tasks", "files"]
    start_time: datetime
    end_time: datetime
    subject: str | None = None
    project_id: str | None = None
    history: list[ConversationTurn] = field(default_factory=list)

    def add_turn(self, role: Literal["user", "assistant"], content: str) -> None:
        """Append a trimmed turn to the in-memory history."""

        normalized_content = content.strip()
        if not normalized_content:
            return

        self.history.append(
            ConversationTurn(
                role=role,
                content=normalized_content,
                timestamp=datetime.now(UTC),
            )
        )

    def render_history(self, max_turns: int = 8) -> str:
        """Render the most recent turns as a compact instruction block."""

        if max_turns <= 0 or not self.history:
            return ""

        recent_turns = self.history[-max_turns:]
        lines = ["KONVERSATIONSHISTORIK:"]
        for turn in recent_turns:
            lines.append(f"- {turn.role}: {turn.content}")
        return "\n".join(lines)


# Use DDD or move to session_service.py if we want to keep all session logic in one place. For now, this is just the data model and factory function.
def create_session_state(project_name: str, category: str) -> SessionState:
    """Create a new in-memory session state instance with generated runtime values."""

    now_utc = datetime.now(UTC)
    normalized_category: Literal["tasks", "files"] = "files" if category == "files" else "tasks"

    return SessionState(
        session_id=str(uuid4()),
        project_name=project_name,
        category=normalized_category,
        start_time=now_utc,
        end_time=now_utc,
        subject="Example Subject",
    )


def get_default_session_state() -> SessionState:
    """Dummy SessionState used for stdio/MCP startup. MCP instructions only consume a subset of fields, but keeping one shared model avoids bloat."""

    return SessionState(
        session_id="mcp-default-session",
        start_time=datetime.now(),
        end_time=datetime.now(),
        project_name="PLACEHOLDER: to be user to look up projectId via API after rollout to more projects",
        category="tasks",
        subject="PLACEHOLDER: Set dynamically by LLM after session starts (or by session context values)",
    )
