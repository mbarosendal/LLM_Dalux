from __future__ import annotations

import json
import logging

from mcp_dalux.clients.contracts import AgentDecision, ToolRequest


def build_structured_user_prompt(text: str, tools: list[str] | None = None) -> str:
    """Build the provider-agnostic user prompt requesting structured JSON output."""
    available_tools = tools or []
    tool_hint = ", ".join(available_tools) if available_tools else "none"

    return (
        "Return ONLY valid JSON with this shape: "
        '{"mode":"answer|tools","message":"string","tool_requests":[{"tool_name":"string","arguments":{}}]}.'
        " If tools are needed, set mode to tools and include tool_requests. "
        "If tools are not needed, set mode to answer and keep tool_requests empty. "
        f"Available tools: {tool_hint}. "
        f"User prompt: {text}"
    )


def parse_agent_decision_output(
    raw_output: str | None,
    provider_name: str,
    logger: logging.Logger,
    empty_message: str,
) -> AgentDecision:
    """Normalize raw model text output into the internal AgentDecision contract."""
    normalized_output = (raw_output or "").strip()
    if not normalized_output:
        logger.warning("%s returned empty text response", provider_name)
        return AgentDecision(
            mode="answer",
            message=empty_message,
            raw_output=None,
        )

    try:
        parsed = json.loads(normalized_output)
    except json.JSONDecodeError:
        logger.warning("%s returned non-JSON content: %s", provider_name, normalized_output[:1000])
        return AgentDecision(
            mode="answer",
            message=normalized_output,
            raw_output=normalized_output,
        )

    tool_requests_payload = parsed.get("tool_requests", []) or []
    tool_requests = [
        ToolRequest(
            tool_name=item.get("tool_name", "unknown"),
            arguments=item.get("arguments", {}) or {},
        )
        for item in tool_requests_payload
        if isinstance(item, dict)
    ]

    mode = parsed.get("mode", "answer")
    if mode not in {"answer", "tools"}:
        mode = "answer"

    return AgentDecision(
        mode=mode,
        message=parsed.get("message", normalized_output),
        tool_requests=tool_requests,
        raw_output=normalized_output,
    )