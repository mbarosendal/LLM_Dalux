import logging
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.policies.tool_policy import ToolPolicy


logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.setLevel(logging.INFO)
    log_path = (
        Path(__file__).resolve().parents[3] / "json_dumps" / "dalux_tool_debug.log"
    )
    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(file_handler)
    logger.propagate = False


DEBUG_DUMP_PATH = (
    Path(__file__).resolve().parents[3] / "json_dumps" / "dalux_tool_debug.log"
)


def _dump_tool_debug(tool: str, event: str, payload: dict) -> None:
    """Append one JSON line with timestamped tool debug payload."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": tool,
        "event": event,
        "payload": payload,
    }
    try:
        with DEBUG_DUMP_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except Exception:
        # Debug dumping must never break tool execution.
        pass


def register_dalux_tools(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register Dalux-related MCP tools."""

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
        logger.info("get_tasks called project_id=%r bookmark=%r", project_id, bookmark)
        _dump_tool_debug(
            "get_tasks",
            "request",
            {"project_id": project_id, "bookmark": bookmark},
        )
        try:
            tasks_payload = adapter.get_tasks(project_id, bookmark=bookmark)
            tasks = (
                tasks_payload.get("items", [])
                if isinstance(tasks_payload, dict)
                else []
            )
            links = (
                tasks_payload.get("links", [])
                if isinstance(tasks_payload, dict)
                else []
            )

            if not tasks:
                return f"No tasks found for {project_label}."

            page_label = " (paginated via bookmark)" if bookmark else ""
            lines = [f"Found {len(tasks)} task(s) for {project_label}{page_label}."]

            for task in tasks:
                type_info = task.get("type", {})
                created_by = task.get("createdBy", {})
                # workflow = task.get("workflow", {})

                # workflow_info = workflow.get("name", {})

                task_id = task.get("taskId", "N/A")
                subject = task.get("subject", "No subject")
                # usage = task.get("usage", "N/A") # double with type.name?
                type_name = type_info.get("name", "N/A")
                number = task.get("number", "N/A")
                created = task.get("created", "N/A")
                created_by_user_id = created_by.get("userId", "N/A")

                lines.append(
                    " | ".join(
                        [
                            f"taskId: {task_id}",
                            f"subject: {subject}",
                            # f"usage: {usage}",
                            f"typeName: {type_name}",
                            f"number: {number}",
                            f"created: {created}",
                            f"createdByUserId: {created_by_user_id}",
                        ]
                    )
                )

            if links:
                lines.append("links:")
                for link in links:
                    if not isinstance(link, dict):
                        continue
                    rel = link.get("rel", "N/A")
                    href = link.get("href", "N/A")
                    method = link.get("method", "N/A")
                    lines.append(f"rel: {rel} | method: {method} | href: {href}")

            _dump_tool_debug(
                "get_tasks",
                "response",
                {
                    "project": project_label,
                    "bookmark": bookmark,
                    "task_count": len(tasks),
                    "link_count": len(links),
                },
            )

            logging.info(
                f"Successfully fetched {len(tasks)} tasks for {project_label}."
            )
            return "\n".join(lines)

        except ValueError as ve:
            logging.warning(f"Value error fetching tasks for {project_label}: {ve}")
            return f"Value error fetching tasks for {project_label}: {ve}"

        except httpx.HTTPStatusError as he:
            logging.error(f"HTTP error fetching tasks for {project_label}: {he}")
            return f"HTTP error fetching tasks for {project_label}: {he}"

        except Exception as e:
            logging.error(f"Error fetching tasks for {project_label}: {e}")
            return f"Error fetching tasks for {project_label}: {e}"

    @mcp.tool()
    @ToolPolicy(max_calls=40)
    def get_task(task_id: str):
        """Get detailed info for a specific task by taskId.
        Use this when the user wants to see details about a specific task and you already have the taskId (e.g. from get_tasks).
        Returns detailed info about the task, including all available fields.
        For a broader search or list of tasks, use get_tasks() instead.
        """
        try:
            task = adapter.get_task(task_id)
            logging.info(f"Successfully fetched details for task ID {task_id}.")
            return f"Details for task ID {task_id}:\n{task}"

        except ValueError as ve:
            logging.warning(f"Value error fetching details for task ID {task_id}: {ve}")
            return f"Value error fetching details for task ID {task_id}: {ve}"

        except httpx.HTTPStatusError as he:
            logging.error(f"HTTP error fetching details for task ID {task_id}: {he}")
            return f"HTTP error fetching details for task ID {task_id}: {he}"

        except Exception as e:
            logging.error(f"Error fetching details for task ID {task_id}: {e}")
            return f"Error fetching details for task ID {task_id}: {e}"

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
        - Approved. with follow up (Godkendt, med opfølgning)
        - Approved (Godkendt)
        - Expired (Udgået)
        Types of open status:
        - Rejected (Afvist)
        - Ongoing (Igangværende)
        - Ready (Klarmeldt)
        And a fallback status:
        - Unknown (Ukendt)
        """

        def infer_status(
            action: str | None, status: str | None, has_description: bool
        ) -> str:
            action_value = (action or "").strip().lower()
            status_value = (status or "").strip().lower()

            # Action is the strongest signal in this payload shape.
            if action_value == "approve":
                return (
                    "approved_with_follow_up" if has_description else "approved"
                )  # maybe if not has_status instead?
            if action_value == "assign":
                return "ongoing"
            if action_value == "reject":
                return "rejected"
            if action_value == "complete":
                return "ready"
            if action_value == "other":
                return "expired"

            # Status is only a fallback when action is missing or unfamiliar.
            if status_value == "closed":
                return "unknown"
            if status_value == "open":
                return "unknown"

            return "unknown"

        project_label = project_id or "default project"
        _dump_tool_debug(
            "get_task_changes",
            "request",
            {"project_id": project_id, "bookmark": bookmark},
        )

        try:
            changes_payload = adapter.get_task_changes(project_id, bookmark=bookmark)
            changes = (
                changes_payload.get("items", [])
                if isinstance(changes_payload, dict)
                else []
            )
            links = (
                changes_payload.get("links", [])
                if isinstance(changes_payload, dict)
                else []
            )

            if not changes:
                return {
                    "project": project_label,
                    "items": [],
                    "taskSummaries": [],
                    "links": links,
                }

            enriched_items = []
            task_latest: dict[str, dict] = {}

            for change in changes:
                if not isinstance(change, dict):
                    continue

                fields = change.get("fields", {}) or {}

                action = change.get("action")
                status = fields.get("status")
                description = change.get("description") or ""

                inferred = infer_status(
                    action if isinstance(action, str) else None,
                    status if isinstance(status, str) else None,
                    bool(description),
                )

                _dump_tool_debug(
                    "get_task_changes",
                    "inferred_status",
                    {
                        "taskId": change.get("taskId"),
                        "timestamp": change.get("timestamp"),
                        "action": action,
                        "status": status,
                        "inferredStatus": inferred,
                    },
                )

                item = {
                    "taskId": change.get("taskId"),
                    "timestamp": change.get("timestamp"),
                    "action": action,
                    "status": status,
                    "inferredStatus": inferred,
                    "description": description,
                    "modifiedByUserId": (fields.get("modifiedBy") or {}).get("userId"),
                    "assignedToRoleId": (fields.get("assignedTo") or {}).get("roleId"),
                    "assignedToRoleName": (fields.get("assignedTo") or {}).get(
                        "roleName"
                    ),
                    "currentResponsibleUserId": (
                        fields.get("currentResponsible") or {}
                    ).get("userId"),
                    "rawChange": change,  # keep for deep inspection if needed
                }

                enriched_items.append(item)

                # Track latest event per taskId
                task_id = item["taskId"]
                timestamp = item["timestamp"]

                if task_id:
                    if task_id not in task_latest:
                        task_latest[task_id] = item
                    else:
                        # compare timestamps (string compare works)
                        if (
                            timestamp
                            and task_latest[task_id].get("timestamp")
                            and timestamp > task_latest[task_id]["timestamp"]
                        ):
                            task_latest[task_id] = item

            # Build task-level summaries (final state per task)
            task_summaries = []
            for task_id, latest in task_latest.items():
                task_summaries.append(
                    {
                        "taskId": task_id,
                        "finalStatus": latest.get("inferredStatus", "unknown"),
                        "latestTimestamp": latest.get("timestamp"),
                        "assignedToRoleId": latest.get("assignedToRoleId"),
                        "assignedToRoleName": latest.get("assignedToRoleName"),
                        "currentResponsibleUserId": latest.get(
                            "currentResponsibleUserId"
                        ),
                    }
                )

            return {
                "project": project_label,
                "items": enriched_items,
                "taskSummaries": task_summaries,
                "links": links,
            }

        except Exception as e:
            _dump_tool_debug(
                "get_task_changes",
                "error",
                {
                    "project": project_label,
                    "bookmark": bookmark,
                    "error": str(e),
                },
            )
            return {
                "error": f"Failed to fetch task changes for {project_label}",
                "details": str(e),
            }

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
        try:
            users_payload = adapter.get_users(project_id)
            users = (
                users_payload.get("items", [])
                if isinstance(users_payload, dict)
                else []
            )
            links = (
                users_payload.get("links", [])
                if isinstance(users_payload, dict)
                else []
            )
            metadata = (
                users_payload.get("metadata", {})
                if isinstance(users_payload, dict)
                else {}
            )

            if not users:
                return f"No users found for {project_label}."

            lines = [f"Found {len(users)} user(s) for {project_label}."]
            for user in users:
                user_id = user.get("userId", "N/A")
                first_name = user.get("firstName", "No name")
                last_name = user.get("lastName", "")
                name = f"{first_name} {last_name}".strip()
                email = user.get("email", "N/A")
                company_id = user.get("companyId", "N/A")

                lines.append(
                    f"userId: {user_id} | name: {name} | email: {email} | companyId: {company_id}"
                )

            if links:
                lines.append("links:")
                for link in links:
                    if not isinstance(link, dict):
                        continue
                    rel = link.get("rel", "N/A")
                    href = link.get("href", "N/A")
                    method = link.get("method", "N/A")
                    lines.append(f"rel: {rel} | method: {method} | href: {href}")

            if metadata:
                totalRemainingItems = metadata.get("totalRemainingItems", "N/A")
                lines.append(f"metadata: totalRemainingItems: {totalRemainingItems}")

            logging.info(
                f"Successfully fetched {len(users)} users for {project_label}."
            )
            return "\n".join(lines)

        except ValueError as ve:
            logging.warning(f"Value error fetching users for {project_label}: {ve}")
            return f"Value error fetching users for {project_label}: {ve}"

        except httpx.HTTPStatusError as he:
            logging.error(f"HTTP error fetching users for {project_label}: {he}")
            return f"HTTP error fetching users for {project_label}: {he}"

        except Exception as e:
            logging.error(f"Error fetching users for {project_label}: {e}")
            return f"Error fetching users for {project_label}: {e}"

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
        try:
            user_data = adapter.get_user(user_id, project_id)

            if not isinstance(user_data, dict) or not user_data:
                return f"No user found for userId {user_id} in {project_label}."

            first_name = user_data.get("firstName", "")
            last_name = user_data.get("lastName", "")
            name = f"{first_name} {last_name}".strip() or "No name"
            email = user_data.get("email", "N/A")
            company_id = user_data.get("companyId", "N/A")

            lines = [f"Found user for {project_label}."]
            lines.append(
                " | ".join(
                    [
                        f"userId: {user_data.get('userId', 'N/A')}",
                        f"name: {name}",
                        f"email: {email}",
                        f"companyId: {company_id}",
                    ]
                )
            )

            logging.info(f"Successfully fetched details for user ID {user_id}.")
            return "\n".join(lines)

        except ValueError as ve:
            logging.warning(f"Value error fetching details for user ID {user_id}: {ve}")
            return f"Value error fetching details for user ID {user_id}: {ve}"

        except httpx.HTTPStatusError as he:
            logging.error(f"HTTP error fetching details for user ID {user_id}: {he}")
            return f"HTTP error fetching details for user ID {user_id}: {he}"

        except Exception as e:
            logging.error(f"Error fetching details for user ID {user_id}: {e}")
            return f"Error fetching details for user ID {user_id}: {e}"
