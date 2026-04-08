import logging
from fastmcp import FastMCP
from language_model.prompts.system_prompt import SYSTEM_PROMPT
from adapters.dalux_adapter import DaluxAdapter

# Set up MCP object with resources
mcp = FastMCP(
    name="dalux-mcp",
    instructions=SYSTEM_PROMPT,
)

# Shared adapter instance
_adapter = DaluxAdapter()

# Expose adapter methods as MCP functions
@mcp.tool()
def get_tasks(project_id: str | None = None):
    """Get all tasks for a project.
    Use this when the user wants to see a list of tasks, or search for a task by name or other attributes.
    Returns a list of tasks, each with basic info like id, name, status, etc. 
    For more details on a specific task when you already know the task_id, use get_task(task_id) instead.
    """
    requested_project_id = project_id
    try:
        approved_project_id = _adapter.enforce_project_constraints(project_id)

        tasks = _adapter.get_tasks(approved_project_id)
        if not tasks:
            return f"No tasks found for project {approved_project_id}."

        # /5.1/tasks returns a list of envelopes with the actual payload under data.
        task_items = tasks if isinstance(tasks, list) else tasks.get("items", [])
        if not isinstance(task_items, list) or not task_items:
            return f"No tasks found for project {approved_project_id}."

        lines = [f"Found {len(task_items)} task(s) for project {approved_project_id}."]

        for t in task_items:
            data = t.get("data", t) if isinstance(t, dict) else {}
            type_info = data.get("type", {}) if isinstance(data, dict) else {}
            created_by = data.get("createdBy", {}) if isinstance(data, dict) else {}

            task_id = data.get("taskId", "N/A")
            subject = data.get("subject", "No subject")
            usage = data.get("usage", "N/A")
            type_name = type_info.get("name", "N/A")
            number = data.get("number", "N/A")
            created = data.get("created", "N/A")
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

        logging.info(f"Successfully fetched {len(task_items)} tasks for project {approved_project_id}.")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Error fetching tasks for project {requested_project_id}: {e}")
        return f"Error fetching tasks for project {requested_project_id}: {e}"

