from datetime import UTC, datetime
import logging

from fastapi import APIRouter, HTTPException

from mcp_dalux.api.schemas import (
    StartSessionRequest,
    StartSessionResponse,
    SendPromptRequest,
    SendPromptResponse,
    StartSessionRequest,
    StartSessionResponse,
)
from mcp_dalux.api.services.prompt_service import (
    LLMError,
    PromptInput,
    PromptValidationError,
    send_prompt_response,
)
from mcp_dalux.api.services.session_service import SessionNotFoundError, start_session_response

router = APIRouter(prefix="/sessions", tags=["sessions"])
logger = logging.getLogger(__name__)


@router.post("/start")
async def start_session(session_request: StartSessionRequest) -> StartSessionResponse:
    """Start a new session for a given project and category."""
    logger.info("Starting session for project=%s category=%s", session_request.project_name, session_request.category)
    return start_session_response(
        project_name=session_request.project_name,
        category=session_request.category,
    )


@router.post("/{session_id}/prompts/send")
async def send_prompt(session_id: str, prompt_request: SendPromptRequest) -> SendPromptResponse:
    """Send a prompt to an active session."""
    logger.info("Incoming prompt session_id=%s text_len=%s", session_id, len(prompt_request.text))
    # Convert HTTP request to internal model with server-generated timestamp
    prompt_input = PromptInput(
        session_id=session_id,
        text=prompt_request.text,
        timestamp=datetime.now(UTC).isoformat(),
    )
    try:
        return await send_prompt_response(prompt_input)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PromptValidationError as exc:
        logger.warning("PromptValidationError session_id=%s detail=%s", session_id, str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
