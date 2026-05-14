from __future__ import annotations

from mcp_dalux.llm.instructions.dalux_context import DALUX_CONTEXT
from mcp_dalux.llm.instructions.files_context import FILES_CONTEXT
from mcp_dalux.llm.instructions.system_prompt import SYSTEM_PROMPT
from mcp_dalux.llm.instructions.tasks_context import TASKS_CONTEXT

# from mcp_dalux.llm.instructions.user_context import USER_CONTEXT_TEMPLATE
from mcp_dalux.llm.services.tool_registry import render_tool_context


def build_runtime_instructions(
    *,
    category: str,
    project_id: str | None,
    project_name: str | None,
    actor_user_id: str | None,
    conversation_history: str | None = None,
) -> str:
    """Compose runtime instructions shared by HTTP and MCP transport paths."""
    sections = [SYSTEM_PROMPT, DALUX_CONTEXT]

    # User-specific runtime instructions are disabled for the public deployment.
    # if actor_user_id:
    #     sections.append(USER_CONTEXT_TEMPLATE.format(actor_user_id=actor_user_id))

    if project_id:
        sections.append(f"SESSION PROJECT:\n- Active project id: {project_id}")
    elif project_name:
        sections.append(f"SESSION PROJECT:\n- Active project name: {project_name}")

    if category == "tasks":
        sections.append(TASKS_CONTEXT)
        sections.append(render_tool_context())

    if category == "files":
        sections.append(FILES_CONTEXT)

    if conversation_history:
        sections.append(conversation_history)

    return "\n\n".join(section.strip() for section in sections if section.strip())
