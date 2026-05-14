from __future__ import annotations

import asyncio
import json
import logging

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.config import Config
from mcp_dalux.llm.client_factory import get_llm_client
from mcp_dalux.llm.contracts import AgentDecision
from mcp_dalux.llm.services.instructions_service import build_runtime_instructions
from mcp_dalux.llm.services.tool_operations import execute_tool_operation
from mcp_dalux.llm.services.tool_registry import get_tool_names
from mcp_dalux.session_models import SessionState

logger = logging.getLogger(__name__)

_llm_client = get_llm_client()
_adapter = DaluxAdapter()
_available_tools = get_tool_names()


def build_runtime_instructions_for_http(session_state: SessionState) -> str:
    """Build runtime instructions for HTTP agent turns."""
    return build_runtime_instructions(
        category=session_state.category,
        project_id=session_state.project_id,
        project_name=session_state.project_name,
        subject=session_state.subject,
        # actor_user_id=Config.DALUX_USER_ID,
        conversation_history=session_state.render_history(),
    )


async def _dispatch_tool_requests(
    decision: AgentDecision,
    scope_key: str,
) -> list[dict[str, object]]:
    """Dispatch requested tools."""
    tool_results: list[dict[str, object]] = []

    for tool_request in decision.tool_requests:
        result = await asyncio.to_thread(
            execute_tool_operation,
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


async def run_agent_loop(
    processed_text: str,
    runtime_instructions: str,
    scope_key: str,
) -> str:
    """Run the model-tool loop until a final answer is produced or limit is reached."""
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
            return decision.response

        # JSON is either the presentation of data from tool_presenters.py or an error from make_error_response.
        if decision.mode == "tools" and decision.tool_requests:
            tool_results = await _dispatch_tool_requests(decision, scope_key)
            current_text = "Tool results (JSON):\n" + json.dumps(tool_results, indent=2) + "\nPlease provide the final answer."
            continue

        logger.warning("Model returned unsupported decision shape mode=%s", decision.mode)
        return "Model returned an unsupported decision shape."

    logger.warning("Reached agent round limit=%s", Config.MAX_AGENT_ROUNDS)
    return "Reached agent round limit before producing a final answer."
