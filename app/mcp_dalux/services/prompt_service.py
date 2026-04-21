from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import httpx

from mcp_dalux.api.schemas import SendPromptResponse
from mcp_dalux.orchestration import SessionContext, build_runtime_instructions_for_http
from mcp_dalux.policies.input_policy import InputPolicy
from mcp_dalux.services.session_service import check_session_exists, get_session


# This module should own prompt processing and the agent loop.
#
# Flow:
# - validate and sanitize incoming prompt text
# - load active session state
# - build runtime instructions
# - call the LLM interface
# - decide whether to call tools
# - return structured response data
#
# Keep the route layer out of this logic so it stays testable.

class SessionNotFoundError(ValueError):
    """Raised when a prompt references a non-existent or inactive session."""


class PromptValidationError(ValueError):
    """Raised when prompt validation fails."""


class LLMError(RuntimeError):
    """Raised when there's an error communicating with the language model."""


@dataclass
class PromptInput:
    """Internal model for prompt data after HTTP parsing.
    
    This is NOT part of the HTTP contract. The route layer creates this
    from SendPromptRequest, adding the server-generated timestamp, which client cannot set.
    """
    session_id: str
    text: str
    timestamp: str  # Server-generated, never from client



async def send_prompt_response(prompt_input: PromptInput) -> SendPromptResponse:
    """Process an incoming prompt and return a structured response.

    This is a placeholder implementation. It should evolve to actually process the prompt, interact with the session state, call the LLM, and decide on tool usage.
    """

    if not check_session_exists(prompt_input.session_id):
        raise SessionNotFoundError("Session does not exist or is not active")

    processed = InputPolicy.preprocess_prompt(prompt_input.text)

    if not InputPolicy.validate_prompt(processed):
        raise PromptValidationError("Prompt validation failed")

    session_data = get_session(prompt_input.session_id)
    if session_data is None:
        raise SessionNotFoundError("Session does not exist or is not active")

    session_context = SessionContext(
        start_time=datetime.fromisoformat(session_data["start_time"]),
        end_time=datetime.fromisoformat(session_data["end_time"]),
        category=session_data["category"],
        project_name=session_data["project_name"],
        subject=session_data.get("subject"),
    )
    runtime_instructions = build_runtime_instructions_for_http(session_context)

    # Need a response contract for the llm output, even if minimal, so we do not depend on a guessed JSON shape.
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as async_client:
            response = await async_client.post(
                "https://postman-echo.com/post",
                json={
                    "prompt": processed,
                    "instructions": runtime_instructions,
                    "session_id": prompt_input.session_id,
                },
            )
            response.raise_for_status()
            echoed_payload = response.json()
    except httpx.HTTPError as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc
    except ValueError as exc:
        raise LLMError(f"LLM response could not be parsed: {exc}") from exc

    return SendPromptResponse(
        session_id=prompt_input.session_id,
        timestamp=prompt_input.timestamp,
        text=echoed_payload.get("json", {}).get("prompt", processed),
    )
