from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from mcp_dalux.api.schemas import CreateSessionResponse

# In-memory store for active sessions. In production, this would be a database.
_active_sessions: dict[str, dict] = {}

# Add async+await if we need to do any I/O here later (e.g., database calls, external service calls). For now, it's all in-memory and synchronous.
def create_session_response(project_name: str, category: str) -> CreateSessionResponse:
    """Create a session with generated runtime values and store it."""
    now_utc = datetime.now(UTC)
    end_utc = now_utc + timedelta(hours=1)
    
    session_id = str(uuid4())
    
    # Store session in memory
    _active_sessions[session_id] = {
        "project_name": project_name,
        "category": category,
        "start_time": now_utc.isoformat(),
        "end_time": end_utc.isoformat(),
    }
    
    return CreateSessionResponse(
        session_id=session_id,
        start_time=now_utc.isoformat(),
        end_time=end_utc.isoformat(),
        project_name=project_name,
        category=category,
        subject="Example Subject",
    )


def check_session_exists(session_id: str) -> bool:
    """Check if a session with the given ID exists and is active."""
    return session_id in _active_sessions


def get_session(session_id: str) -> dict | None:
    """Retrieve session metadata if it exists."""
    return _active_sessions.get(session_id)