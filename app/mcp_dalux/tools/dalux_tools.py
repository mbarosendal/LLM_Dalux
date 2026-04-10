import logging

import httpx
from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.policies.tool_policy import ToolPolicy


def register_dalux_tools(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register Dalux-related MCP tools."""

    @mcp.tool()
    @ToolPolicy(max_calls=20)
    def get_tasks(project_id: str | None = None):
        """Get all tasks for a project.
        Use this when the user wants to see a list of tasks, or search for a task by name or other attributes.
        Returns a list of tasks, each with basic info like id, name, status (open or not), etc.
        The project_id is optional - omit it to use the default configured project. Never ask the user for a projectId.
        For more details on a specific task when you already know the task_id, use get_task(task_id) instead.
        """
        project_label = project_id or "default project"
        try:
            tasks_payload = adapter.get_tasks(project_id)
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

            lines = [f"Found {len(tasks)} task(s) for {project_label}."]

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
    def get_task_changes(project_id: str | None = None):
        """Get task change events for a project.
        Use this when the user asks about recent task updates, activity history, or change tracking.
        Returns change items and any links returned by the API.
        The project_id is optional - omit it to use the default configured project. Never ask the user for a projectId.
        """
        project_label = project_id or "default project"
        try:
            changes_payload = adapter.get_task_changes(project_id)
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
                return f"No task changes found for {project_label}."

            lines = [f"Found {len(changes)} task change event(s) for {project_label}."]
            for change in changes:
                lines.append(str(change))

            if links:
                lines.append("links:")
                for link in links:
                    if not isinstance(link, dict):
                        continue
                    rel = link.get("rel", "N/A")
                    href = link.get("href", "N/A")
                    method = link.get("method", "N/A")
                    lines.append(f"rel: {rel} | method: {method} | href: {href}")

            logging.info(
                f"Successfully fetched {len(changes)} task change event(s) for {project_label}."
            )
            return "\n".join(lines)

        except ValueError as ve:
            logging.warning(
                f"Value error fetching task changes for {project_label}: {ve}"
            )
            return f"Value error fetching task changes for {project_label}: {ve}"

        except httpx.HTTPStatusError as he:
            logging.error(f"HTTP error fetching task changes for {project_label}: {he}")
            return f"HTTP error fetching task changes for {project_label}: {he}"

        except Exception as e:
            logging.error(f"Error fetching task changes for {project_label}: {e}")
            return f"Error fetching task changes for {project_label}: {e}"

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
                name = user.get("name", "No name")
                lines.append(f"userId: {user_id} | name: {name}")

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
