from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.config import Config
from mcp_dalux.policies.tool_policy import ToolPolicy
from mcp_dalux.tools.tool_execution import ToolContext, execute_tool
from mcp_dalux.tools.tool_presenters import make_tool_response
from mcp_dalux.tools.tool_transformers import (
    transform_task_changes_collection_payload,
    transform_task_payload,
    transform_tasks_collection_payload,
    transform_user_payload,
    transform_users_collection_payload,
)


def register_dalux_tools(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register Dalux-related MCP tools."""

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
    def get_tasks(project_id: str | None = None, bookmark: str | None = None):
        """Get all tasks for a project.
        Use this when the user wants to see a list of tasks, or search for a task by name or other attributes.
        If user asks about staus of task(s), use get_task_changes() instead which is designed for that and provides richer info for status inference.
        Returns a list of tasks, each with basic info like id, name, status (open or not), etc.
        The project_id is optional - omit it to use the default configured project. Never ask the user for a projectId.
        The bookmark is optional - use it to request the next page from a previous response's nextPage link if needed. For pagination, pass only the bookmark token value (example: 63176033328), not /?bookmark=... and not a full URL.
        For more details on a specific task when you already know the task_id, use get_task(task_id) instead.
        """
        project_label = project_id or "default project"

        # Inner function passed to execute_tool to handle fetching, transforming, and building the response for the tool.
        def tool_action() -> dict:
            # 1) Fetch
            tasks_payload = adapter.get_tasks(project_id, bookmark=bookmark)
            # 2) Transform (extract, normalize, build)
            transformed = transform_tasks_collection_payload(
                tasks_payload, project_label, bookmark
            )
            # 3) Build
            return make_tool_response(
                tool="get_tasks",
                kind="collection",
                project=project_label,
                summary=transformed["summary"],
                data=transformed["data"],
                links=transformed["links"],
                metadata=transformed["metadata"],
            )

        return execute_tool(
            ToolContext(
                tool_name="get_tasks",
                project_label=project_label,
                request_payload={"project_id": project_id, "bookmark": bookmark},
            ),
            tool_action,
        )

    @mcp.tool()
    @ToolPolicy(max_calls=40)
    def get_task(task_id: str):
        """Get detailed info for a specific task by taskId.
        Use this when the user wants to see details about a specific task and you already have the taskId (e.g. from get_tasks).
        Returns detailed info about the task, including all available fields.
        For a broader search or list of tasks, use get_tasks() instead.
        """
        project_label = "default project"

        def tool_action() -> dict:
            task = adapter.get_task(task_id)
            transformed = transform_task_payload(task, task_id, project_label)
            return make_tool_response(
                tool="get_task",
                kind="detail",
                project=project_label,
                summary=transformed["summary"],
                data=transformed["data"],
            )

        return execute_tool(
            ToolContext(
                tool_name="get_task",
                project_label=project_label,
                request_payload={"task_id": task_id},
            ),
            tool_action,
        )

    @mcp.tool()
    @ToolPolicy(max_calls=20)
    def get_task_changes(project_id: str | None = None, bookmark: str | None = None):
        """
        Get task change events and inferred task statuses for a project.

        Pagination:
        - `bookmark` is optional and used to fetch the next page.
        - Pass only the bookmark token value from a prior `links` nextPage URL.

        Returns structured data with:
        - items: raw change events enriched with inferredStatus
        - taskSummaries: one entry per taskId with the FINAL inferred status

        Rules for LLM usage:
        - ALWAYS use `taskSummaries` when answering questions about task status.
        - `inferredStatus` is authoritative - do NOT re-infer unless it is "unknown".
        - Use `items` only for deeper inspection (e.g. timestamps, descriptions, responsibility).

        Status vocabulary (normalized):
        Types of closed status:
        - Approved with follow up (Godkendt, med opfølgning)
        - Approved (Godkendt)
        - Expired (Udgået)
        Types of open status:
        - Rejected (Afvist)
        - Ongoing (Igangværende)
        - Ready (Klarmeldt)
        - New (Ny) - not implemented
        - Archived (Arkiveret) - not implemented
        And a fallback status:
        - Unknown (Ukendt)
        """
        project_label = project_id or "default project"

        def tool_action() -> dict:
            changes_payload = adapter.get_task_changes(project_id, bookmark=bookmark)
            transformed = transform_task_changes_collection_payload(
                changes_payload, project_label
            )
            return make_tool_response(
                tool="get_task_changes",
                kind="analysis",
                project=project_label,
                summary=transformed["summary"],
                data=transformed["data"],
                links=transformed["links"],
                metadata=transformed["metadata"],
            )

        return execute_tool(
            ToolContext(
                tool_name="get_task_changes",
                project_label=project_label,
                request_payload={"project_id": project_id, "bookmark": bookmark},
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
