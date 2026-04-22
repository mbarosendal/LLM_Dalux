from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.policies.tool_policy import ToolPolicy
from mcp_dalux.client_tools.tool_execution import ToolContext, execute_tool
from mcp_dalux.client_tools.tool_presenters import make_tool_response
from mcp_dalux.client_tools.tool_transformers import (
    transform_task_changes_collection_payload,
    transform_task_payload,
    transform_tasks_collection_payload,
)


def register_dalux_tools_tasks(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register task-related Dalux MCP tools."""

    @mcp.tool()
    @ToolPolicy(max_calls=20)
    def get_tasks(project_id: str | None = None, bookmark: str | None = None):
        """List tasks for discovery and filtering.

        Use when the user asks for task overviews, counts, or keyword/type searches.
        Returns lightweight task fields only (taskId, subject, typeName, number, created, createdByUserId).

        Tool choice:
        - For current/final status questions, prefer get_task_changes.
        - For one known taskId, use get_task.

        Privacy rule:
        - Do not expose internal IDs (taskId, createdByUserId) unless the user explicitly asks.
        - If asked, look up actual user details (name, email) using get_user and present these to the user instead.

        Examples:
        - "Show all safety observations from this week"
        - "Find tasks about cleanup"

        Parameters:
        - project_id is optional; omit to use the default scoped project.
        - bookmark is optional for pagination. Pass only the token from links.nextPage.
        """
        project_label = project_id or "default project"

        def tool_action() -> dict:
            tasks_payload = adapter.get_tasks(project_id, bookmark=bookmark)
            transformed = transform_tasks_collection_payload(
                tasks_payload, project_label, bookmark
            )
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

    # Endpoint for a single task does not actually provide much more value than the collection endpoint with filters, and it adds complexity and risk around taskId usage, so we will skip it for now and add if needed based on user feedback.
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

    @mcp.tool()
    @ToolPolicy(max_calls=20)
    def get_task_changes(project_id: str | None = None, bookmark: str | None = None):
        """
        Get task change events with inferred status, optimized for status answers.

        Use this as the primary tool for questions about progress, open vs closed, and final status.

        Returns:
        - items: event-level history (timestamp, action, description, responsibility)
        - taskSummaries: one row per taskId with finalStatus and latestTimestamp

        Rules for LLM usage:
        - For status answers, use taskSummaries as the source of truth.
        - Use items only when the user asks for timeline/details.
        - Do not re-infer status if inferredStatus/finalStatus is present.

        Privacy rule:
        - Keep role/user/task IDs out of user-facing text unless explicitly requested.

        Examples:
        - "Which tasks are still ongoing?"
        - "How many tasks were approved this week?"
        - "Show the status timeline for SO2"

        Pagination:
        - bookmark is optional and used to fetch the next page.
        - Pass only the bookmark token from links.nextPage.

        Normalized status values and color codes:
        Closed status types:
        - 🟢 Approved with follow up (Godkendt, med opfølgning)
        - 🟢 Approved (Godkendt)
        # - ⚫ Expired (Udgået)
        Open status types:
        - Rejected (Afvist)
        - 🟠 Ongoing (Igangværende)
        - Ready (Klarmeldt)
        - 🔴 New (Ny) - not implemented!
        - ⚫ Archived (Arkiveret) - not implemented!
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
