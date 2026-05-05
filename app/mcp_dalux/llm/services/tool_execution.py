from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import httpx
from mcp_dalux.llm.services.tool_presenters import make_error_response
from mcp_dalux.logging_setup import append_structured_log_event, get_file_logger

TOOL_LOG_FILE = "dalux_tool_debug.log"

logger = get_file_logger(__name__, TOOL_LOG_FILE)


@dataclass(frozen=True)
class ToolExecutionContext:
    tool_name: str
    project_label: str
    request_payload: dict


def execute_tool(context: ToolExecutionContext, action: Callable[[], dict]) -> dict:
    """Run a tool action with centralized logging, debug dumping, and error handling."""
    append_structured_log_event(
        log_filename=TOOL_LOG_FILE,
        source=context.tool_name,
        event="request",
        payload={
            "project": context.project_label,
            "request_keys": sorted(context.request_payload.keys()),
        },
    )

    try:
        result = action()
        if isinstance(result, dict):
            append_structured_log_event(
                log_filename=TOOL_LOG_FILE,
                source=context.tool_name,
                event="response",
                payload={
                    "ok": result.get("ok", False),
                    "kind": result.get("kind", "unknown"),
                    "keys": sorted(result.keys()),
                    "items_count": len(result.get("data", {}).get("items", [])),
                },
            )
        logger.info("%s completed for %s", context.tool_name, context.project_label)
        return result
    except ValueError as exc:
        logger.warning(
            "Value error fetching %s for %s: %s",
            context.tool_name,
            context.project_label,
            exc,
        )
        append_structured_log_event(
            log_filename=TOOL_LOG_FILE,
            source=context.tool_name,
            event="error",
            payload={"type": "value_error", "message": str(exc)},
        )
        return make_error_response(
            tool=context.tool_name,
            project=context.project_label,
            title=context.tool_name,
            summary=f"Value error fetching {context.tool_name} for {context.project_label}.",
            message=str(exc),
        )
    except httpx.HTTPStatusError as exc:
        logger.error(
            "HTTP error fetching %s for %s: %s",
            context.tool_name,
            context.project_label,
            exc,
        )
        append_structured_log_event(
            log_filename=TOOL_LOG_FILE,
            source=context.tool_name,
            event="error",
            payload={"type": "http_error", "message": str(exc)},
        )
        return make_error_response(
            tool=context.tool_name,
            project=context.project_label,
            title=context.tool_name,
            summary=f"HTTP error fetching {context.tool_name} for {context.project_label}.",
            message=str(exc),
        )
    except Exception as exc:
        logger.error(
            "Error fetching %s for %s: %s",
            context.tool_name,
            context.project_label,
            exc,
        )
        append_structured_log_event(
            log_filename=TOOL_LOG_FILE,
            source=context.tool_name,
            event="error",
            payload={"type": "unexpected_error", "message": str(exc)},
        )
        return make_error_response(
            tool=context.tool_name,
            project=context.project_label,
            title=context.tool_name,
            summary=f"Error fetching {context.tool_name} for {context.project_label}.",
            message=str(exc),
        )
