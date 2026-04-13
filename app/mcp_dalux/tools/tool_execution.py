from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import httpx

from mcp_dalux.tools.tool_presenters import make_error_response

DEBUG_DUMP_PATH = (
    Path(__file__).resolve().parents[3] / "json_dumps" / "dalux_tool_debug.log"
)

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    log_path = DEBUG_DUMP_PATH
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(file_handler)
    logger.propagate = False


def dump_tool_debug(tool: str, event: str, payload: dict) -> None:
    """Append one JSON line with timestamped tool debug payload."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "event": event,
        "payload": payload,
    }
    try:
        with DEBUG_DUMP_PATH.open("a", encoding="utf-8") as debug_log_file:
            debug_log_file.write(
                json.dumps(entry, ensure_ascii=False, default=str) + "\n"
            )
    except Exception:
        # Pass because debug dumping must never break tool execution.
        pass


@dataclass(frozen=True)
class ToolContext:
    tool_name: str
    project_label: str
    request_payload: dict


def execute_tool(context: ToolContext, action: Callable[[], dict]) -> dict:
    """Run a tool action with centralized logging, debug dumping, and error handling."""
    dump_tool_debug(context.tool_name, "request", context.request_payload)

    try:
        result = action()
        if isinstance(result, dict):
            dump_tool_debug(
                context.tool_name,
                "response",
                {
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
        dump_tool_debug(
            context.tool_name,
            "error",
            {"type": "value_error", "message": str(exc)},
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
        dump_tool_debug(
            context.tool_name,
            "error",
            {"type": "http_error", "message": str(exc)},
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
        dump_tool_debug(
            context.tool_name,
            "error",
            {"type": "unexpected_error", "message": str(exc)},
        )
        return make_error_response(
            tool=context.tool_name,
            project=context.project_label,
            title=context.tool_name,
            summary=f"Error fetching {context.tool_name} for {context.project_label}.",
            message=str(exc),
        )
