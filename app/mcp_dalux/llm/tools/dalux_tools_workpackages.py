from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.llm.services.tool_operations import execute_tool_operation
from mcp_dalux.llm.services.tool_registry import render_mcp_tool_doc


def register_dalux_tools_workpackages(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register workpackage-related Dalux MCP tools."""

    def _mcp_scope_key() -> str:
        ctx = get_context()
        if ctx.session_id:
            return f"mcp-session:{ctx.session_id}"
        return "mcp-session:unknown"

    def get_workpackages(project_id: str | None = None):
        return execute_tool_operation(
            adapter,
            "get_workpackages",
            {"project_id": project_id},
            scope_key=_mcp_scope_key(),
        )

    get_workpackages.__doc__ = render_mcp_tool_doc("get_workpackages")
    mcp.tool()(get_workpackages)
