from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    usage: str
    arguments_hint: str


_TOOL_SPECS: dict[str, ToolSpec] = {
    "get_current_user_context": ToolSpec(
        name="get_current_user_context",
        description="Resolve current user context for personal queries.",
        usage="Call this first for 'my/me/mine' requests to anchor the actor user.",
        arguments_hint="project_id is optional.",
    ),
    "get_tasks": ToolSpec(
        name="get_tasks",
        description="List tasks for discovery and filtering.",
        usage="Use for overview/search; use get_task_changes for status answers.",
        arguments_hint="project_id and bookmark are optional.",
    ),
    "get_task_changes": ToolSpec(
        name="get_task_changes",
        description="List task change events and inferred statuses.",
        usage="Always prioritize inferredStatus over inferring status from raw events. Match status names to user_prompts when possible.",
        arguments_hint="project_id and bookmark are optional.",
    ),
    "get_users": ToolSpec(
        name="get_users",
        description="List users for lookup and matching.",
        usage="Use for discovery by name/company; use get_user for known IDs.",
        arguments_hint="project_id is optional.",
    ),
    "get_user": ToolSpec(
        name="get_user",
        description="Get one user by known user_id.",
        usage="Use only when user_id is known.",
        arguments_hint="user_id is required, project_id is optional.",
    ),
    "get_workpackages": ToolSpec(
        name="get_workpackages",
        description="List workpackages for discovery and matching.",
        usage="Use for workpackage lookup and identifier matching.",
        arguments_hint="project_id is optional.",
    ),
}


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
        lines.append(f"- {spec.name}: {spec.description}")
        lines.append(f"  Usage: {spec.usage}")
        lines.append(f"  Args: {spec.arguments_hint}")
    return "\n".join(lines)


def render_mcp_tool_doc(tool_name: str) -> str:
    """Render one MCP-facing tool docstring from the tool definitions here to avoid duplicate definitions for HTTP and MCP."""
    spec = _TOOL_SPECS.get(tool_name)
    if not spec:
        return f"Tool: {tool_name}"

    return f"{spec.description}\n\nUsage: {spec.usage}\nArgs: {spec.arguments_hint}"
