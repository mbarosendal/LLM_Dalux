from __future__ import annotations

import logging
from dataclasses import dataclass

from mcp_dalux.api.schemas import SendPromptResponse
from mcp_dalux.api.services.agent_service import (
    build_runtime_instructions_for_http,
    run_agent_loop,
)
from mcp_dalux.api.services.session_service import get_session_state, update_session_end_time
from mcp_dalux.llm.client_factory import get_llm_client
from mcp_dalux.llm.contracts import LLMError
from mcp_dalux.policies.input_policy import MAX_INPUT_LENGTH, InputPolicy
from mcp_dalux.session_models import add_session_turn

logger = logging.getLogger(__name__)


class PromptValidationError(ValueError):
    """Raised when prompt validation fails."""


@dataclass
class PromptInput:
    """Internal model for prompt data after HTTP parsing."""

    session_id: str
    text: str
    timestamp: str


async def send_prompt_response(prompt_input: PromptInput) -> SendPromptResponse:
    """Process an incoming prompt and return a structured response."""

    original_text = prompt_input.text or ""
    processed_text = InputPolicy.preprocess_prompt(original_text)
    logger.info("Processing prompt session_id=%s text_len=%s", prompt_input.session_id, len(processed_text))

    # Keep validation explicit here to avoid brittle policy-side false negatives.
    if not processed_text:
        logger.warning(
            "Prompt rejected as empty after preprocess session_id=%s original_len=%s",
            prompt_input.session_id,
            len(original_text),
        )
        raise PromptValidationError("Prompt must not be empty")
    if len(processed_text) > MAX_INPUT_LENGTH:
        logger.warning(
            "Prompt rejected as too long session_id=%s text_len=%s max_len=%s",
            prompt_input.session_id,
            len(processed_text),
            MAX_INPUT_LENGTH,
        )
        raise PromptValidationError(f"Prompt too long (max {MAX_INPUT_LENGTH} chars)")

    session_state = get_session_state(prompt_input.session_id)

    runtime_instructions = build_runtime_instructions_for_http(session_state, processed_text)
    scope_key = f"http-session:{prompt_input.session_id}"

    add_session_turn(session_state, "user", processed_text)

    try:
        response_text = await run_agent_loop(
            processed_text,
            runtime_instructions,
            scope_key,
            session_state,
        )
    except Exception as exc:
        logger.exception("LLM request failed for session_id=%s", prompt_input.session_id)
        raise LLMError(f"LLM request failed: {exc}") from exc

    add_session_turn(session_state, "agent", response_text)
    end_time = update_session_end_time(prompt_input.session_id)
    model_name = get_llm_client().version

    return SendPromptResponse(
        session_id=prompt_input.session_id,
        timestamp=end_time,
        model=model_name,
        text=response_text,
    )
