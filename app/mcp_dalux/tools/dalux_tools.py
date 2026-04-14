from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.tools.dalux_tools_tasks import register_dalux_tools_tasks
from mcp_dalux.tools.dalux_tools_users import register_dalux_tools_users


def register_dalux_tools(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Backward-compatible registration for all currently available Dalux tools."""
    register_dalux_tools_users(mcp, adapter)
    register_dalux_tools_tasks(mcp, adapter)
