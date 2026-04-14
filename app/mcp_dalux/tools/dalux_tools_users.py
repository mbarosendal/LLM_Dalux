from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.config import Config
from mcp_dalux.policies.tool_policy import ToolPolicy
from mcp_dalux.tools.tool_execution import ToolContext, execute_tool
from mcp_dalux.tools.tool_presenters import make_tool_response
from mcp_dalux.tools.tool_transformers import (
    transform_user_payload,
    transform_users_collection_payload,
)


def register_dalux_tools_users(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register user-related Dalux MCP tools."""

    @mcp.tool()
    @ToolPolicy(max_calls=20)
    def get_current_user_context(project_id: str | None = None):
        """Get user context for personal queries without calling the Dalux API.
        Use this when the user asks about "my" tasks/changes and you need their userId anchor.
        The project_id is optional - omit it to use the default configured project.
        """

        project_label = project_id or "default project"

        def tool_action() -> dict:
            user_id = Config.DALUX_USER_ID
            if not user_id:
                raise ValueError(
                    "Current user context is not configured (DALUX_USER_ID)."
                )

            return make_tool_response(
                tool="get_current_user_context",
                kind="context",
                project=project_label,
                summary="Resolved user context for personal queries.",
                data={
                    "userId": user_id,
                    "projectId": project_id or Config.DALUX_SCOPED_PROJECT_ID,
                },
            )

        return execute_tool(
            ToolContext(
                tool_name="get_current_user_context",
                project_label=project_label,
                request_payload={"project_id": project_id},
            ),
            tool_action,
        )

    @mcp.tool()
    @ToolPolicy(max_calls=20)
    def get_users(project_id: str | None = None):
        """Get users for a project.
        Use this when the user wants to see a list of users in the project, or search for a user by name or other attributes.
        Returns a list of users with basic info like id, name, etc.
        The project_id is optional - omit it to use the default configured project. Never ask the user for a projectId.
        If totalRemainingItems in metadata is greater than 0, that means there are more users than returned in this response - consider using pagination with the links provided to fetch more if needed.
        For more details on a specific user when you already know the user_id, use get_user(user_id) instead.
        """
        project_label = project_id or "default project"

        def tool_action() -> dict:
            users_payload = adapter.get_users(project_id)
            transformed = transform_users_collection_payload(
                users_payload, project_label
            )
            return make_tool_response(
                tool="get_users",
                kind="collection",
                project=project_label,
                summary=transformed["summary"],
                data=transformed["data"],
                links=transformed["links"],
                metadata=transformed["metadata"],
            )

        return execute_tool(
            ToolContext(
                tool_name="get_users",
                project_label=project_label,
                request_payload={"project_id": project_id},
            ),
            tool_action,
        )

    @mcp.tool()
    @ToolPolicy(max_calls=20)
    def get_user(user_id: str, project_id: str | None = None):
        """Get detailed info for a specific user on a project by userId.
        Use this when the user wants to see details (name, email, etc.) about a specific user and you already have the userId.
        This does not provide additional information about a specific user compared to what is available in get_users().
        Returns user info from the endpoint data object.
        For a broader search or list of users, use get_users() instead.
        """
        project_label = project_id or "default project"

        def tool_action() -> dict:
            user_data = adapter.get_user(user_id, project_id)
            transformed = transform_user_payload(user_data, user_id, project_label)
            return make_tool_response(
                tool="get_user",
                kind="detail",
                project=project_label,
                summary=transformed["summary"],
                data=transformed["data"],
            )

        return execute_tool(
            ToolContext(
                tool_name="get_user",
                project_label=project_label,
                request_payload={"user_id": user_id, "project_id": project_id},
            ),
            tool_action,
        )
