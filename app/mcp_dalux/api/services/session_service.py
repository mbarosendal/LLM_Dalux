from __future__ import annotations

from datetime import UTC, datetime

from mcp_dalux.api.schemas import StartSessionResponse
from mcp_dalux.config import Config
from mcp_dalux.session_models import (
    SessionState,
    create_session_state,
)


class SessionNotFoundError(ValueError):
    """Raised when a prompt references a non-existent or inactive session."""


# In-memory store for active sessions. In production, this would be a database.
_active_sessions: dict[str, SessionState] = {}


# In production with more users, sessions would authenticate and associate a user
# with the session. For the prototype, we keep a single env-backed user identity.
def _to_start_session_response(session_state: SessionState) -> StartSessionResponse:
    """Map internal SessionState to HTTP response contract."""

    return StartSessionResponse(
        session_id=session_state.session_id,
        start_time=session_state.start_time.isoformat(),
        end_time=session_state.end_time.isoformat(),
        project_id=session_state.project_id,
        category=session_state.category,
    )


# Add async+await if we need to do any I/O here later (e.g., database calls, external service calls). For now, it's all in-memory.
def create_session_response(project_id: str | None, category: str) -> StartSessionResponse:
    """Create SessionState, persist it, and map to HTTP response contract."""

    effective_project_id = project_id or Config.DALUX_SCOPED_PROJECT_ID
    session_state = create_session_state(
        project_id=effective_project_id, project_name="test_project", category=category, user_id=Config.DALUX_USER_ID
    )
    _active_sessions[session_state.session_id] = session_state
    return _to_start_session_response(session_state)


def check_session_exists(session_id: str) -> bool:
    """Check if a session with the given ID exists and is active."""
    return session_id in _active_sessions


def get_session(session_id: str) -> SessionState:
    """Retrieve internal SessionState if it exists."""

    if not check_session_exists(session_id):
        raise SessionNotFoundError("Session does not exist or is not active")

    return _active_sessions[session_id]


def update_session_end_time(session_id: str) -> str:
    """Update end time for a session and return the persisted ISO timestamp."""

    session_state = get_session(session_id)
    session_state.end_time = datetime.now(UTC)

    return session_state.end_time.isoformat()


def get_session_state(session_id: str) -> SessionState:
    """Load SessionState for runtime use by prompt/agent flow."""

    return get_session(session_id)
