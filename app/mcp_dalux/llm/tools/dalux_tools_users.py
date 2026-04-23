from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.llm.services.tool_operations import execute_tool_operation
from mcp_dalux.llm.services.tool_registry import render_mcp_tool_doc


def register_dalux_tools_users(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register user-related Dalux MCP tools."""

    def _mcp_scope_key() -> str:
        ctx = get_context()
        if ctx.session_id:
            return f"mcp-session:{ctx.session_id}"
        return "mcp-session:unknown"

    def get_current_user_context(project_id: str | None = None):
        return execute_tool_operation(
            adapter,
            "get_current_user_context",
            {"project_id": project_id},
            scope_key=_mcp_scope_key(),
        )

    get_current_user_context.__doc__ = render_mcp_tool_doc("get_current_user_context")
    mcp.tool()(get_current_user_context)

    def get_users(project_id: str | None = None):
        return execute_tool_operation(
            adapter,
            "get_users",
            {"project_id": project_id},
            scope_key=_mcp_scope_key(),
        )

    get_users.__doc__ = render_mcp_tool_doc("get_users")
    mcp.tool()(get_users)

    def get_user(user_id: str, project_id: str | None = None):
        return execute_tool_operation(
            adapter,
            "get_user",
            {"user_id": user_id, "project_id": project_id},
            scope_key=_mcp_scope_key(),
        )

    get_user.__doc__ = render_mcp_tool_doc("get_user")
    mcp.tool()(get_user)
