from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.config import Config
from mcp_dalux.policies.tool_policy import ToolPolicy
from mcp_dalux.client_tools.tool_execution import ToolContext, execute_tool
from mcp_dalux.client_tools.tool_presenters import make_tool_response
from mcp_dalux.client_tools.tool_transformers import (
    transform_user_payload,
    transform_users_collection_payload,
)


def register_dalux_tools_users(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register user-related Dalux MCP tools."""

    @mcp.tool()
    @ToolPolicy(max_calls=20)
    def get_current_user_context(project_id: str | None = None):
        """Resolve the current user anchor for personal queries.

        Use first when the user asks about "my" tasks/changes.
        Returns the actor userId (and scoped projectId) used to ground "me/my/mine" requests.

        Tool choice:
        - Run this before filtering task or user results to the current user.

        Privacy rule:
        - Use returned IDs internally; avoid exposing them unless explicitly requested.

        Parameter:
        - project_id is optional; omit to use the default scoped project.
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
        """List users for lookup and matching.

        Use when the user asks to find people by name/company or to see project participants.
        Returns a collection of basic user fields (userId, name, email, companyId).

        Tool choice:
        - Use get_user only when a specific userId is already known.

        Privacy rule:
        - Avoid exposing internal IDs by default.

        Parameter:
        - project_id is optional; omit to use the default scoped project.
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
        """Get one user by known userId.

        Use when userId is already known and you need a single-user lookup.
        Current output is equivalent to user fields available in get_users.

        Tool choice:
        - For discovery or name matching, use get_users.

        Privacy rule:
        - Keep userId internal unless explicitly requested.

        Example:
        - "Show details for this user ID"
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
