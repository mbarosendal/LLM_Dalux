from __future__ import annotations

import logging
from dataclasses import dataclass
import json

from mcp_dalux.api.schemas import SendPromptResponse
from mcp_dalux.language_model.contracts import AgentDecision
from mcp_dalux.language_model.client_factory import get_llm_client
from mcp_dalux.orchestration import build_runtime_instructions_for_http
from mcp_dalux.policies.input_policy import InputPolicy
from mcp_dalux.services.session_service import build_session_context


logger = logging.getLogger(__name__)


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


class PromptValidationError(ValueError):
    """Raised when prompt validation fails."""


class LLMError(RuntimeError):
    """Raised when there's an error communicating with the language model."""

_llm_client = get_llm_client()
_MAX_AGENT_ROUNDS = 2


@dataclass
class PromptInput:
    """Internal model for prompt data after HTTP parsing.
    
    This is NOT part of the HTTP contract. The route layer creates this
    from SendPromptRequest, adding the server-generated timestamp, which client cannot set.
    """
    session_id: str
    text: str
    timestamp: str  # Server-generated, never from client


async def _dispatch_tools(decision: AgentDecision) -> list[dict[str, object]]:
    """Dispatch requested tools (dummy implementation)."""
    tool_results: list[dict[str, object]] = []

    for tool_request in decision.tool_requests:
        tool_results.append(
            {
                "tool_name": tool_request.tool_name,
                "ok": True,
                "data": {
                    "note": "Dummy tool dispatcher result",
                    "arguments": tool_request.arguments,
                },
            }
        )

    logger.info("Dispatched %s tool(s): %s", len(tool_results), [item["tool_name"] for item in tool_results])
    return tool_results


async def _run_agent_loop(processed_text: str, runtime_instructions: str) -> str:
    """Run a agent loop with tool branching."""
    current_text = processed_text

    for _ in range(_MAX_AGENT_ROUNDS):
        decision: AgentDecision = await _llm_client.generate_decision(
            text=current_text,
            instructions=runtime_instructions,
            tools=["tasks_lookup", "users_lookup", "workpackages_lookup"],
        )

        logger.info("Agent decision mode=%s tools=%s", decision.mode, len(decision.tool_requests))

        if decision.mode == "answer":
            logger.info("Agent loop completed with final answer")
            return decision.message

        if decision.mode == "tools" and decision.tool_requests:
            tool_results = await _dispatch_tools(decision)
            current_text = (
                "Tool results (JSON):\n"
                + json.dumps(tool_results, indent=2)
                + "\nPlease provide the final answer."
            )
            continue

        logger.warning("Model returned unsupported decision shape mode=%s", decision.mode)
        return "Model returned an unsupported decision shape."

    logger.warning("Reached agent round limit=%s", _MAX_AGENT_ROUNDS)
    return "Reached agent round limit before producing a final answer."


async def send_prompt_response(prompt_input: PromptInput) -> SendPromptResponse:
    """Process an incoming prompt and return a structured response.

    This is a placeholder implementation. It should evolve to actually process the prompt, interact with the session state, call the LLM, and decide on tool usage.
    """

    processed_text = InputPolicy.preprocess_prompt(prompt_input.text)
    logger.info("Processing prompt session_id=%s text_len=%s", prompt_input.session_id, len(processed_text))

    if not InputPolicy.validate_prompt(processed_text):
        raise PromptValidationError("Prompt validation failed")

    session_context = build_session_context(prompt_input.session_id)
    logger.info(
        "Loaded session context session_id=%s category=%s project_name=%s",
        prompt_input.session_id,
        session_context.category,
        session_context.project_name,
    )

    runtime_instructions = build_runtime_instructions_for_http(session_context)

    try:
        response_text = await _run_agent_loop(processed_text, runtime_instructions)
    except Exception as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    # Return time of reply instead, and update session state if needed (not implemented yet)
    return SendPromptResponse(
        session_id=prompt_input.session_id,
        timestamp=prompt_input.timestamp,
        text=response_text,
    )
