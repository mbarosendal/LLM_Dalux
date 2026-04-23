from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from mcp_dalux.api.schemas import CreateSessionResponse
from mcp_dalux.orchestration import SessionContext


class SessionNotFoundError(ValueError):
    """Raised when a prompt references a non-existent or inactive session."""


# In-memory store for active sessions. In production, this would be a database.
_active_sessions: dict[str, dict] = {}


# Add async+await if we need to do any I/O here later (e.g., database calls, external service calls). For now, it's all in-memory.
def create_session_response(project_name: str, category: str) -> CreateSessionResponse:
    """Create a session with generated runtime values and store it."""

    now_utc = datetime.now(UTC)

    session_id = str(uuid4())

    # Store session in runtime memory
    _active_sessions[session_id] = {
        "project_name": project_name,
        "category": category,
        "start_time": now_utc.isoformat(),
        "end_time": now_utc.isoformat(),
    }

    return CreateSessionResponse(
        session_id=session_id,
        start_time=now_utc.isoformat(),
        end_time=now_utc.isoformat(),
        project_name=project_name,
        category=category,
        subject="Example Subject",
    )


def check_session_exists(session_id: str) -> bool:
    """Check if a session with the given ID exists and is active."""
    return session_id in _active_sessions


def get_session(session_id: str) -> dict:
    """Retrieve session metadata if it exists."""

    if not check_session_exists(session_id):
        raise SessionNotFoundError("Session does not exist or is not active")

    return _active_sessions[session_id]


def update_session_end_time(session_id: str) -> str:
    """Update end time for a session and return the persisted ISO timestamp."""

    if not check_session_exists(session_id):
        raise SessionNotFoundError("Session does not exist or is not active")

    now_utc = datetime.now(UTC)
    end_time_iso = now_utc.isoformat()
    _active_sessions[session_id]["end_time"] = end_time_iso

    return end_time_iso


def build_session_context(session_id: str) -> SessionContext:
    """Load session data and build a SessionContext object."""

    session_data = get_session(session_id)

    return SessionContext(
        start_time=datetime.fromisoformat(session_data["start_time"]),
        end_time=datetime.fromisoformat(session_data["end_time"]),
        category=session_data["category"],
        project_name=session_data["project_name"],
        subject=session_data.get("subject"),
    )
