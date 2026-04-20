from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.policies.tool_policy import ToolPolicy
from mcp_dalux.tools.tool_execution import ToolContext, execute_tool
from mcp_dalux.tools.tool_presenters import make_tool_response
from mcp_dalux.tools.tool_transformers import transform_workpackages_collection_payload


def register_dalux_tools_workpackages(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register workpackage-related Dalux MCP tools."""

    @mcp.tool()
    @ToolPolicy(max_calls=20)
    def get_workpackages(project_id: str | None = None):
        """List workpackages for discovery and matching.

        Use when the user asks about workpackages or needs workpackage lookups.
        Returns lightweight fields only (workpackageId, name, companyId).

        Parameter:
        - project_id is optional; omit to use the default scoped project.
        """
        project_label = project_id or "default project"

        def tool_action() -> dict:
            payload = adapter.get_workpackages(project_id)
            transformed = transform_workpackages_collection_payload(payload, project_label)
            return make_tool_response(
                tool="get_workpackages",
                kind="collection",
                project=project_label,
                summary=transformed["summary"],
                data=transformed["data"],
                links=transformed["links"],
                metadata=transformed["metadata"],
            )

        return execute_tool(
            ToolContext(
                tool_name="get_workpackages",
                project_label=project_label,
                request_payload={"project_id": project_id},
            ),
            tool_action,
        )
