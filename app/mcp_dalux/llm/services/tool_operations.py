from __future__ import annotations

from collections.abc import Callable

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.config import Config
from mcp_dalux.llm.services.tool_execution import ToolExecutionContext, execute_tool
from mcp_dalux.llm.services.tool_presenters import make_tool_response
from mcp_dalux.llm.services.tool_transformers import (
    transform_task_changes_collection_payload,
    transform_tasks_collection_payload,
    transform_user_payload,
    transform_users_collection_payload,
    transform_workpackages_collection_payload,
)
from mcp_dalux.policies.tool_policy import ToolPolicy


def _optional_str(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _required_str(name: str, value: object) -> str:
    if isinstance(value, str) and value:
        return value
    raise ValueError(f"{name} is required and must be a non-empty string.")


@ToolPolicy(max_calls=20)
def _run_get_tasks(
    adapter: DaluxAdapter,
    arguments: dict[str, object],
    scope_key: str,
) -> dict:
    tool_name = "get_tasks"
    project_id = _optional_str(arguments.get("project_id"))
    bookmark = _optional_str(arguments.get("bookmark"))
    project_label = project_id or "default project"

    # Define the tool's action as a callable that can be passed to the centralized execution function, which handles logging and
    # error handling consistently across all tools.
    def action() -> dict:
        payload = adapter.get_tasks(project_id, bookmark=bookmark)
        transformed = transform_tasks_collection_payload(
            payload,
            project_label,
            bookmark=bookmark,
        )
        return make_tool_response(
            tool=tool_name,
            kind="collection",
            project=project_label,
            summary=transformed["summary"],
            data=transformed["data"],
            links=transformed["links"],
            metadata=transformed["metadata"],
        )

    return execute_tool(
        ToolExecutionContext(
            tool_name=tool_name,
            project_label=project_label,
            request_payload={"project_id": project_id, "bookmark": bookmark},
        ),
        action,
    )


@ToolPolicy(max_calls=20)
def _run_get_task_changes(
    adapter: DaluxAdapter,
    arguments: dict[str, object],
    scope_key: str,
) -> dict:
    tool_name = "get_task_changes"
    project_id = _optional_str(arguments.get("project_id"))
    bookmark = _optional_str(arguments.get("bookmark"))
    project_label = project_id or "default project"

    def action() -> dict:
        payload = adapter.get_task_changes(project_id, bookmark=bookmark)
        transformed = transform_task_changes_collection_payload(payload, project_label)
        return make_tool_response(
            tool=tool_name,
            kind="analysis",
            project=project_label,
            summary=transformed["summary"],
            data=transformed["data"],
            links=transformed["links"],
            metadata=transformed["metadata"],
        )

    return execute_tool(
        ToolExecutionContext(
            tool_name=tool_name,
            project_label=project_label,
            request_payload={"project_id": project_id, "bookmark": bookmark},
        ),
        action,
    )


@ToolPolicy(max_calls=20)
def _run_get_users(
    adapter: DaluxAdapter,
    arguments: dict[str, object],
    scope_key: str,
) -> dict:
    tool_name = "get_users"
    project_id = _optional_str(arguments.get("project_id"))
    project_label = project_id or "default project"

    def action() -> dict:
        payload = adapter.get_users(project_id)
        transformed = transform_users_collection_payload(payload, project_label)
        return make_tool_response(
            tool=tool_name,
            kind="collection",
            project=project_label,
            summary=transformed["summary"],
            data=transformed["data"],
            links=transformed["links"],
            metadata=transformed["metadata"],
        )

    return execute_tool(
        ToolExecutionContext(
            tool_name=tool_name,
            project_label=project_label,
            request_payload={"project_id": project_id},
        ),
        action,
    )


@ToolPolicy(max_calls=20)
def _run_get_user(
    adapter: DaluxAdapter,
    arguments: dict[str, object],
    scope_key: str,
) -> dict:
    tool_name = "get_user"
    project_id = _optional_str(arguments.get("project_id"))
    user_id = _required_str("user_id", arguments.get("user_id"))
    project_label = project_id or "default project"

    def action() -> dict:
        payload = adapter.get_user(user_id, project_id)
        transformed = transform_user_payload(payload, user_id, project_label)
        return make_tool_response(
            tool=tool_name,
            kind="detail",
            project=project_label,
            summary=transformed["summary"],
            data=transformed["data"],
        )

    return execute_tool(
        ToolExecutionContext(
            tool_name=tool_name,
            project_label=project_label,
            request_payload={"project_id": project_id, "user_id": user_id},
        ),
        action,
    )


@ToolPolicy(max_calls=20)
def _run_get_current_user_context(
    adapter: DaluxAdapter,
    arguments: dict[str, object],
    scope_key: str,
) -> dict:
    del adapter
    tool_name = "get_current_user_context"
    project_id = _optional_str(arguments.get("project_id"))
    project_label = project_id or "default project"

    def action() -> dict:
        user_id = Config.DALUX_USER_ID
        if not user_id:
            raise ValueError("Current user context is not configured (DALUX_USER_ID).")
        return make_tool_response(
            tool=tool_name,
            kind="context",
            project=project_label,
            summary="Resolved user context for personal queries.",
            data={
                "userId": user_id,
                "projectId": project_id or Config.DALUX_SCOPED_PROJECT_ID,
            },
        )

    return execute_tool(
        ToolExecutionContext(
            tool_name=tool_name,
            project_label=project_label,
            request_payload={"project_id": project_id},
        ),
        action,
    )


@ToolPolicy(max_calls=20)
def _run_get_workpackages(
    adapter: DaluxAdapter,
    arguments: dict[str, object],
    scope_key: str,
) -> dict:
    tool_name = "get_workpackages"
    project_id = _optional_str(arguments.get("project_id"))
    project_label = project_id or "default project"

    def action() -> dict:
        payload = adapter.get_workpackages(project_id)
        transformed = transform_workpackages_collection_payload(payload, project_label)
        return make_tool_response(
            tool=tool_name,
            kind="collection",
            project=project_label,
            summary=transformed["summary"],
            data=transformed["data"],
            links=transformed["links"],
            metadata=transformed["metadata"],
        )

    return execute_tool(
        ToolExecutionContext(
            tool_name=tool_name,
            project_label=project_label,
            request_payload={"project_id": project_id},
        ),
        action,
    )


# Define the public interface for tool execution that can be used by the agent loop and is decoupled from the specific tool implementations..
_ToolHandler = Callable[[DaluxAdapter, dict[str, object], str], dict]

# Map raw tool names to their corresponding handler functions. This central registry allows for consistent execution and easy extension of new tools.
_TOOL_HANDLERS: dict[str, _ToolHandler] = {
    "get_tasks": _run_get_tasks,
    "get_task_changes": _run_get_task_changes,
    # "get_users": _run_get_users,
    # "get_user": _run_get_user,
    "get_current_user_context": _run_get_current_user_context,
    "get_workpackages": _run_get_workpackages,
}


def execute_tool_operation(
    adapter: DaluxAdapter,
    tool_name: str,
    arguments: dict[str, object],
    scope_key: str,
) -> dict:
    """Execute one named tool operation and return the standardized response envelope."""
    if tool_name not in _TOOL_HANDLERS:
        raise ValueError(f"Unsupported tool requested by agent: {tool_name}")
    handler = _TOOL_HANDLERS[tool_name]

    return handler(
        adapter=adapter,
        arguments=arguments,
        scope_key=scope_key,
    )
