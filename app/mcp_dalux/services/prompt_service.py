from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from mcp_dalux.api.schemas import SendPromptResponse
from mcp_dalux.policies.input_policy import InputPolicy
from mcp_dalux.services.session_service import check_session_exists


class SessionNotFoundError(ValueError):
    """Raised when a prompt references a non-existent or inactive session."""


@dataclass
class PromptInput:
    """Internal model for prompt data after HTTP parsing.
    
    This is NOT part of the HTTP contract. The route layer creates this
    from SendPromptRequest, adding the server-generated timestamp, which client cannot set.
    """
    session_id: str
    text: str
    timestamp: str  # Server-generated, never from client


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

def send_prompt_response(prompt_input: PromptInput) -> SendPromptResponse:
    """Process an incoming prompt and return a structured response.

    This is a placeholder implementation. It should evolve to actually process the prompt, interact with the session state, call the LLM, and decide on tool usage.
    """

    # Preprocess input (strip whitespace)
    preprocessed = InputPolicy.preprocess_input(prompt_input.text)

    # Validate the preprocessed input
    if not InputPolicy.validate_prompt(preprocessed):
        raise ValueError("Prompt validation failed")

    # Check that session exists
    if not check_session_exists(prompt_input.session_id):
        raise SessionNotFoundError("Session does not exist or is not active")

    # Return structured response with the server timestamp
    return SendPromptResponse(
        session_id=prompt_input.session_id,
        timestamp=prompt_input.timestamp,
        text=preprocessed,
    )
