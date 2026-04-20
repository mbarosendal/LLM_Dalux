from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException

from mcp_dalux.api.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    SendPromptRequest,
    SendPromptResponse,
)
from mcp_dalux.services.prompt_service import (
    PromptInput,
    SessionNotFoundError,
    send_prompt_response,
)
from mcp_dalux.services.session_service import create_session_response

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Add session-related endpoints we expose here.

# Build order:
# 1. Add request/response models in api.schemas.
# 2. Add session creation first.
# 3. Store sessions in memory first; persistence can come later.
# 4. Add prompt sending after session creation works.
# 5. Only then connect the agent loop and LLM client.
#
# Endpoints:
# - POST /sessions/create
# - POST /sessions/{sessionId}/prompts/send
# - GET /sessions/{sessionId} (optional for debugging)
# - DELETE /sessions/{sessionId} (optional cleanup)

@router.post("/create")
def create_session(session_request: CreateSessionRequest) -> CreateSessionResponse:
    """Create a new session for a given project and category."""

    return create_session_response(
        project_name=session_request.project_name,
        category=session_request.category,
    )

@router.post("/{session_id}/prompts/send")
def send_prompt(prompt_request: SendPromptRequest) -> SendPromptResponse:
    """Send a prompt to an active session.
    
    The server generates the timestamp; clients cannot set it.
    """
    # Convert HTTP request to internal model with server-generated timestamp
    prompt_input = PromptInput(
        session_id=prompt_request.session_id,
        text=prompt_request.text,
        timestamp=datetime.now(UTC).isoformat(),
    )
    try:
        return send_prompt_response(prompt_input)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc