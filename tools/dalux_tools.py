import logging

from fastmcp import FastMCP

from adapters.dalux_adapter import DaluxAdapter


def register_dalux_tools(mcp: FastMCP, adapter: DaluxAdapter) -> None:
	"""Register Dalux-related MCP tools."""

	@mcp.tool()
	def get_tasks(project_id: str | None = None):
		"""Get all tasks for a project.
		Use this when the user wants to see a list of tasks, or search for a task by name or other attributes.
		Returns a list of tasks, each with basic info like id, name, status, etc.
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

				task_id = task.get("taskId", "N/A")
				subject = task.get("subject", "No subject")
				usage = task.get("usage", "N/A")
				type_name = type_info.get("name", "N/A")
				number = task.get("number", "N/A")
				created = task.get("created", "N/A")
				created_by_user_id = created_by.get("userId", "N/A")

				lines.append(
					" | ".join(
						[
							f"taskId: {task_id}",
							f"subject: {subject}",
							f"usage: {usage}",
							f"typeName: {type_name}",
							f"number: {number}",
							f"created: {created}",
							f"createdByUserId: {created_by_user_id}",
						]
					)
				)

			logging.info(f"Successfully fetched {len(tasks)} tasks for {project_label}.")
			return "\n".join(lines)

		except Exception as e:
			logging.error(f"Error fetching tasks for {project_label}: {e}")
			return f"Error fetching tasks for {project_label}: {e}"
