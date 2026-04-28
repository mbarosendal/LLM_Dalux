from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4


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
