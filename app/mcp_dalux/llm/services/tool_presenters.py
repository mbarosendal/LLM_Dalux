from __future__ import annotations


def make_tool_response(
    *,
    tool: str,
    kind: str,
    project: str,
    summary: str,
    data: dict,
    links: list[dict] | None = None,
    metadata: dict | None = None,
) -> dict:
    """Helper to create a consistent tool response format for the LLM to consume, with optional links and metadata."""
    response = {
        "tool": tool,
        "kind": kind,
        "ok": True,
        "project": project,
        "summary": summary,
        "data": data,
    }
    if links is not None:
        response["links"] = links
    if metadata is not None:
        response["metadata"] = metadata
    return response


def make_error_response(
    *,
    tool: str,
    project: str,
    title: str,
    summary: str,
    message: str,
) -> dict:
    """Helper to create a consistent error response format for the LLM to consume."""
    return {
        "tool": tool,
        "kind": "error",
        "ok": False,
        "project": project,
        "title": title,
        "summary": summary,
        "error": {
            "message": message,
        },
        "data": {},
    }
