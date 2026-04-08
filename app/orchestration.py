<<<<<<< HEAD:orchestration.py
from fastmcp import FastMCP
from language_model.prompts.system_prompt import SYSTEM_PROMPT
from adapters.dalux_adapter import DaluxAdapter
from tools.dalux_tools import register_dalux_tools

# Setup
=======
import logging
import json
from fastmcp import FastMCP
from app.language_model.prompts.system_prompt import SYSTEM_PROMPT
from app.adapters.dalux_adapter import DaluxAdapter
>>>>>>> ca56b6ee0ce032f78858d3779f0638cd48aa3a2e:app/orchestration.py

mcp = FastMCP(
    name="dalux-mcp",
    instructions=SYSTEM_PROMPT,
)
_adapter = DaluxAdapter()

<<<<<<< HEAD:orchestration.py
register_dalux_tools(mcp, _adapter)
=======
# Expose adapter methods as MCP functions
@mcp.tool()
def get_tasks(project_id: str | None = None):
    """Get all tasks for a project.
    Use this when the user wants to see a list of tasks, or search for a task by name or other attributes.
    You should only present task_id to the user if they explicitly ask for it, or if you need to use it in a follow-up API call to get more details about a specific task.
    Returns a list of tasks, each with basic info like id, name, status, etc. 
    For more details on a specific task when you already know the task_id, use get_task(task_id) instead.
    """
    project_label = project_id or "default project"
    try:
        tasks = _adapter.get_tasks(project_id)
        if not tasks:
            return f"No tasks found for {project_label}."
>>>>>>> ca56b6ee0ce032f78858d3779f0638cd48aa3a2e:app/orchestration.py

# Process input from user
# Branch logic (API, LLM, etc.)
# Return response to user

<<<<<<< HEAD:orchestration.py

# if __name__ == "__main__":
#     register_dalux_tools(mcp, _adapter)
=======
        for task in tasks:
            task_id = task.get("taskId", "N/A")
            subject = task.get("subject", "No subject")
            # usage = task.get("usage", "N/A")
            number = task.get("number", "N/A")
            created = task.get("created", "N/A")

            type_info = task.get("type", {})
            type_name = type_info.get("name", "N/A")

            created_by = task.get("createdBy", {})
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

        # Logging is not visible to the LLM, just the return
        logging.info(f"Successfully fetched {len(tasks)} tasks for {project_label}.")
        return "\n".join(lines)

    except Exception as e:
        logging.error(f"Error fetching tasks for {project_label}: {e}")
        return f"Error fetching tasks for {project_label}: {e}"

@mcp.tool()
def get_task(task_id: str):
    """Get detailed information about a specific task by its ID.
    Use this when you already know the task_id and want to retrieve more detailed information about that specific task.
    Returns detailed info about the task, including all available fields from the API.
    """
    try:
        task = _adapter.get_task(task_id)
        if not task:
            return f"No task found with ID {task_id}."

        logging.info(f"Successfully fetched details for task ID {task_id}.")
        return json.dumps(task, indent=2, ensure_ascii=False)

    except Exception as e:
        logging.error(f"Error fetching details for task ID {task_id}: {e}")
        return f"Error fetching details for task ID {task_id}: {e}"


# Test print to verify function works outside of MCP context
if __name__ == "__main__":
    print(get_tasks())
>>>>>>> ca56b6ee0ce032f78858d3779f0638cd48aa3a2e:app/orchestration.py
