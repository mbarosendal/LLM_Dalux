from __future__ import annotations

from dataclasses import dataclass

from mcp_dalux.api.schemas import SendPromptResponse
from mcp_dalux.language_model.clients.claude_client import ClaudeClient
from mcp_dalux.language_model.contracts import AgentDecision
from mcp_dalux.orchestration import build_runtime_instructions_for_http
from mcp_dalux.policies.input_policy import InputPolicy
from mcp_dalux.services.session_service import build_session_context


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


_llm_client = ClaudeClient()


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

    processed_text = InputPolicy.preprocess_prompt(prompt_input.text)

    if not InputPolicy.validate_prompt(processed_text):
        raise PromptValidationError("Prompt validation failed")

    session_context = build_session_context(prompt_input.session_id)

    runtime_instructions = build_runtime_instructions_for_http(session_context)

    try:
        decision: AgentDecision = await _llm_client.generate_decision(
            text=processed_text,
            instructions=runtime_instructions,
            tools=["tasks_lookup", "users_lookup", "workpackages_lookup"],
        )
    except Exception as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    if decision.mode == "tools" and decision.tool_requests:
        requested_tools = ", ".join(tool_request.tool_name for tool_request in decision.tool_requests)
        response_text = f"{decision.message} Requested tools: {requested_tools}"
    else:
        response_text = decision.message

    return SendPromptResponse(
        session_id=prompt_input.session_id,
        timestamp=prompt_input.timestamp,
        text=response_text,
    )
