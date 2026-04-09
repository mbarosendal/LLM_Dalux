import logging

import httpx
from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter


def register_dalux_tools(mcp: FastMCP, adapter: DaluxAdapter) -> None:
    """Register Dalux-related MCP tools."""

    @mcp.tool()
    def get_tasks(project_id: str | None = None):
        """Get all tasks for a project.
        Use this when the user wants to see a list of tasks, or search for a task by name or other attributes.
        Returns a list of tasks, each with basic info like id, name, status (open or not), etc.
        The project_id is optional - omit it to use the default configured project. Never ask the user for a projectId.
        For more details on a specific task when you already know the task_id, use get_task(task_id) instead.
        """
        project_label = project_id or "default project"
        try:
            tasks = adapter.get_tasks(project_id)
            if not tasks:
                return f"No tasks found for {project_label}."

            lines = [f"Found {len(tasks)} task(s) for {project_label}."]

            for task in tasks:
                type_info = task.get("type", {})
                created_by = task.get("createdBy", {})
                workflow = task.get("workflow", {})
                
                workflow_info = workflow.get("name", {})


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

            logging.info(f"Successfully fetched {len(tasks)} tasks for {project_label}.")
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
    def get_task(task_id: str):
        """Get detailed info for a specific task by taskId.
        Use this when the user wants to see details about a specific task and you already have the taskId (e.g. from get_tasks).
        Returns detailed info about the task, including all available fields.
        For a broader search or list of tasks, use get_tasks() instead.
        """
        try:
            task = adapter.get_task(task_id)
            if not task:
                return f"No task found with ID {task_id}."

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
        