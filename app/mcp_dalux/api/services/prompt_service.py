from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.api.schemas import SendPromptResponse
from mcp_dalux.api.services.session_service import build_session_context
from mcp_dalux.api.services.tool_runtime import execute_tool_request
from mcp_dalux.config import Config
from mcp_dalux.llm.client_factory import get_llm_client
from mcp_dalux.llm.contracts import AgentDecision
from mcp_dalux.llm.services.tool_registry import get_tool_names
from mcp_dalux.orchestration import build_runtime_instructions_for_http
from mcp_dalux.policies.input_policy import InputPolicy

logger = logging.getLogger(__name__)


class PromptValidationError(ValueError):
    """Raised when prompt validation fails."""


class LLMError(RuntimeError):
    """Raised when there's an error communicating with the language model."""


_llm_client = get_llm_client()
_adapter = DaluxAdapter()
_available_tools = get_tool_names()


@dataclass
class PromptInput:
    """Internal model for prompt data after HTTP parsing."""

    session_id: str
    text: str
    timestamp: str


async def _dispatch_tools(
    decision: AgentDecision,
    scope_key: str,
) -> list[dict[str, object]]:
    """Dispatch requested tools against the real Dalux-backed runtime."""
    tool_results: list[dict[str, object]] = []

    for tool_request in decision.tool_requests:
        result = await asyncio.to_thread(
            execute_tool_request,
            _adapter,
            tool_request.tool_name,
            tool_request.arguments,
            scope_key,
        )
        tool_results.append(result)

    logger.info(
        "Dispatched %s tool(s): %s",
        len(tool_results),
        [item.get("tool") for item in tool_results],
    )
    return tool_results


async def _run_agent_loop(
    processed_text: str,
    runtime_instructions: str,
    scope_key: str,
) -> str:
    """Iterative branching of agent decisions to either generate a final answer or dispatch tools."""
    current_text = processed_text

    for _ in range(Config.MAX_AGENT_ROUNDS):
        decision: AgentDecision = await _llm_client.generate_decision(
            text=current_text,
            instructions=runtime_instructions,
            tools=_available_tools,
        )

        logger.info("Agent decision mode=%s tools=%s", decision.mode, len(decision.tool_requests))

        if decision.mode == "answer":
            logger.info("Agent loop completed with final answer")
            return decision.message

        if decision.mode == "tools" and decision.tool_requests:
            tool_results = await _dispatch_tools(decision, scope_key)
            current_text = "Tool results (JSON):\n" + json.dumps(tool_results, indent=2) + "\nPlease provide the final answer."
            continue

        logger.warning("Model returned unsupported decision shape mode=%s", decision.mode)
        return "Model returned an unsupported decision shape."

    logger.warning("Reached agent round limit=%s", Config.MAX_AGENT_ROUNDS)
    return "Reached agent round limit before producing a final answer."


async def send_prompt_response(prompt_input: PromptInput) -> SendPromptResponse:
    """Process an incoming prompt and return a structured response."""

    processed_text = InputPolicy.preprocess_prompt(prompt_input.text)
    logger.info("Processing prompt session_id=%s text_len=%s", prompt_input.session_id, len(processed_text))

    if not InputPolicy.validate_prompt(processed_text):
        raise PromptValidationError("Prompt validation failed")

    session_context = build_session_context(prompt_input.session_id)
    # logger.info(
    #     "Loaded session context session_id=%s category=%s project_name=%s",
    #     prompt_input.session_id,
    #     session_context.category,
    #     session_context.project_name,
    # )

    runtime_instructions = build_runtime_instructions_for_http(session_context)
    scope_key = f"http-session:{prompt_input.session_id}"

    try:
        response_text = await _run_agent_loop(
            processed_text,
            runtime_instructions,
            scope_key,
        )
    except Exception as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    # update_session_end_time(prompt_input.session_id)

    # Return time of reply instead, and update session state if needed (not implemented yet)
    return SendPromptResponse(
        session_id=prompt_input.session_id,
        timestamp=prompt_input.timestamp,
        text=response_text,
    )
