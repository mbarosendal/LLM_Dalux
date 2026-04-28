from __future__ import annotations

import logging
from dataclasses import dataclass

from mcp_dalux.api.schemas import SendPromptResponse
from mcp_dalux.api.services.agent_service import (
    build_runtime_instructions_for_http,
    run_agent_loop,
)
from mcp_dalux.api.services.session_service import get_session_state, update_session_end_time
from mcp_dalux.policies.input_policy import InputPolicy

logger = logging.getLogger(__name__)


class PromptValidationError(ValueError):
    """Raised when prompt validation fails."""


class LLMError(RuntimeError):
    """Raised when there's an error communicating with the language model."""


@dataclass
class PromptInput:
    """Internal model for prompt data after HTTP parsing."""

    session_id: str
    text: str
    timestamp: str


async def send_prompt_response(prompt_input: PromptInput) -> SendPromptResponse:
    """Process an incoming prompt and return a structured response."""

    processed_text = InputPolicy.preprocess_prompt(prompt_input.text)
    logger.info("Processing prompt session_id=%s text_len=%s", prompt_input.session_id, len(processed_text))

    if not InputPolicy.validate_prompt(processed_text):
        raise PromptValidationError("Prompt validation failed")

    session_state = get_session_state(prompt_input.session_id)
    # logger.info(
    #     "Loaded session context session_id=%s category=%s project_name=%s",
    #     prompt_input.session_id,
    #     session_context.category,
    #     session_context.project_name,
    # )

    runtime_instructions = build_runtime_instructions_for_http(session_state)
    scope_key = f"http-session:{prompt_input.session_id}"

    try:
        response_text = await run_agent_loop(
            processed_text,
            runtime_instructions,
            scope_key,
        )
    except Exception as exc:
        logger.exception("LLM request failed for session_id=%s", prompt_input.session_id)
        raise LLMError(f"LLM request failed: {exc}") from exc

    end_time = update_session_end_time(prompt_input.session_id)

    return SendPromptResponse(
        session_id=prompt_input.session_id,
        timestamp=end_time,
        text=response_text,
    )
