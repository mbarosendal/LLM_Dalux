from __future__ import annotations

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.llm.services.tool_operations import execute_tool_operation
from mcp_dalux.llm.services.tool_registry import has_tool


def execute_tool_request(
    adapter: DaluxAdapter,
    tool_name: str,
    arguments: dict[str, object],
    scope_key: str,
) -> dict:
    """Execute one tool call through the shared tool operation registry."""
    if not has_tool(tool_name):
        raise ValueError(f"Unsupported tool requested by model: {tool_name}")

    return execute_tool_operation(adapter, tool_name, arguments, scope_key)
