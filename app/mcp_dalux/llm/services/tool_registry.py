from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ToolSpec:
    tool_name: str
    description: str
    usage: str
    arguments_hint: str


_TOOL_SPECS: dict[str, ToolSpec] = {
    "get_current_user_context": ToolSpec(
        tool_name="get_current_user_context",
        description="Resolve current user context for personal queries.",
        usage="Call this first for 'my/me/mine' requests to anchor the actor user and then filter results by that user.",
        arguments_hint="project_id is optional.",
    ),
    "get_tasks": ToolSpec(
        tool_name="get_tasks",
        description="List tasks for discovery and filtering.",
        usage=(
            "Use for task overviews, counts, searches, and picking candidate tasks by "
            "subject/type/number when the current session context does not already contain "
            "enough task data. For current or final status, prefer get_task_changes. "
            "Use it as the discovery step before any status question, but do not repeat "
            "an overview if the user is following up on a task already discussed."
        ),
        arguments_hint=(
            "project_id and bookmark are optional. Returns lightweight fields such as "
            "taskId, subject, typeName, number, created, and createdByUserId."
        ),
    ),
    "get_task_changes": ToolSpec(
        tool_name="get_task_changes",
        description="List task change events and inferred statuses.",
        usage=(
            "Primary tool for task progress, open vs closed, and final status. Use "
            "taskSummaries as the source of truth for status answers. Use items only for "
            "timelines or detail questions. Do not re-infer status if inferredStatus or "
            "finalStatus is present. If the session history already contains enough task "
            "detail for a follow-up question, answer from that context instead of calling again."
        ),
        arguments_hint="project_id and bookmark are optional. Returns both event-level items and taskSummaries with latest status information.",
    ),
    # "get_users": ToolSpec(
    #     tool_name="get_users",
    #     description="List users for lookup and matching.",
    #     usage="Use for discovery by name/company. Use get_user only when a specific userId is already known.",
    #     arguments_hint="project_id is optional.",
    # ),
    "get_user": ToolSpec(
        tool_name="get_user",
        description="Get one user by known userId.",
        usage="Use only when userId is already known and you need a single-user lookup.",
        arguments_hint="user_id is required, project_id is optional.",
    ),
    "get_workpackages": ToolSpec(
        tool_name="get_workpackages",
        description="List workpackages for discovery and matching.",
        usage="Use for workpackage lookup and identifier matching when the user asks about workpackages or related filters.",
        arguments_hint="project_id is optional.",
    ),
}


_TASK_GUIDANCE = """TASK ANSWERING PLAYBOOK:
- For broad overviews, start with get_tasks.
- For status/changes/progress/final state, use get_task_changes and answer from taskSummaries.
- For timeline/history, use the items list from get_task_changes.
- Do not expose internal IDs unless the user explicitly asks for them.
"""


def get_tool_names() -> list[str]:
    return list(_TOOL_SPECS.keys())


def has_tool(tool_name: str) -> bool:
    return tool_name in _TOOL_SPECS


# def get_tool_specs() -> list[ToolSpec]:
#     return list(_TOOL_SPECS.values())


def render_tool_context(tool_names: list[str] | None = None) -> str:
    """Render a compact, deterministic tool context block for LLM instructions."""
    names = tool_names or get_tool_names()
    selected_specs = [_TOOL_SPECS[name] for name in names if name in _TOOL_SPECS]
    if not selected_specs:
        return "AVAILABLE TOOLS:\n- none"

    lines = ["AVAILABLE TOOLS:"]
    for spec in selected_specs:
        lines.append(f"- {spec.tool_name}: {spec.description}")
        lines.append(f"  Usage: {spec.usage}")
        lines.append(f"  Args: {spec.arguments_hint}")
    if any(name in {"get_tasks", "get_task_changes"} for name in names):
        lines.append("")
        lines.append(_TASK_GUIDANCE.strip())
    return "\n".join(lines)


def render_mcp_tool_doc(tool_name: str) -> str:
    """Render one MCP-facing tool docstring from the tool definitions here to avoid duplicate definitions for HTTP and MCP."""
    spec = _TOOL_SPECS.get(tool_name)
    if not spec:
        return f"Tool: {tool_name}"

    return f"{spec.description}\n\nUsage: {spec.usage}\nArgs: {spec.arguments_hint}"
