from fastmcp import FastMCP
from fastmcp.server.dependencies import get_context
from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.llm.services.tool_operations import execute_tool_operation
from mcp_dalux.llm.services.tool_registry import render_mcp_tool_doc


def register_dalux_tools_tasks(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register task-related Dalux MCP tools."""

    def _mcp_scope_key() -> str:
        ctx = get_context()
        if ctx.session_id:
            return f"mcp-session:{ctx.session_id}"
        return "mcp-session:unknown"

    def get_tasks(project_id: str | None = None, bookmark: str | None = None):
        return execute_tool_operation(
            adapter,
            "get_tasks",
            {"project_id": project_id, "bookmark": bookmark},
            scope_key=_mcp_scope_key(),
        )

    get_tasks.__doc__ = render_mcp_tool_doc("get_tasks")
    mcp.tool()(get_tasks)

    def get_task_changes(project_id: str | None = None, bookmark: str | None = None):
        return execute_tool_operation(
            adapter,
            "get_task_changes",
            {"project_id": project_id, "bookmark": bookmark},
            scope_key=_mcp_scope_key(),
        )

    get_task_changes.__doc__ = render_mcp_tool_doc("get_task_changes")
    mcp.tool()(get_task_changes)

    # Endpoint for a single task does not actually provide much more value than the collection endpoint with filters, and it adds complexity and risk
    # around taskId usage, so we will skip it for now and add if needed based on user feedback.
    # @mcp.tool()
    # @ToolPolicy(max_calls=40)
    # def get_task(task_id: str):
    #     """Get one task by known taskId.

    #     Use when the user references a specific task number/ID and you need a single-task lookup.
    #     Current output is a single lightweight task object with the same core fields as get_tasks.

    #     Tool choice:
    #     - For broad discovery/search, use get_tasks.
    #     - For status timeline or final status, use get_task_changes.

    #     Privacy rule:
    #     - Do not expose internal IDs unless explicitly requested.

    #     Example:
    #     - "Open task SO2"
    #     """
    #     project_label = "default project"

    #     def tool_action() -> dict:
    #         task = adapter.get_task(task_id)
    #         transformed = transform_task_payload(task, task_id, project_label)
    #         return make_tool_response(
    #             tool="get_task",
    #             kind="detail",
    #             project=project_label,
    #             summary=transformed["summary"],
    #             data=transformed["data"],
    #         )

    #     return execute_tool(
    #         ToolContext(
    #             tool_name="get_task",
    #             project_label=project_label,
    #             request_payload={"task_id": task_id},
    #         ),
    #         tool_action,
    #     )
