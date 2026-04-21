from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from fastmcp import FastMCP
from mcp_dalux.config import Config
from mcp_dalux.adapters.dalux_adapter import DaluxAdapter

from mcp_dalux.language_model.instructions.dalux_context import DALUX_CONTEXT
from mcp_dalux.language_model.instructions.files_context import FILES_CONTEXT
from mcp_dalux.language_model.instructions.system_prompt import SYSTEM_PROMPT
from mcp_dalux.language_model.instructions.tasks_context import TASKS_CONTEXT
from mcp_dalux.language_model.instructions.user_context import USER_CONTEXT_TEMPLATE
from mcp_dalux.tools.dalux_tools_tasks import register_dalux_tools_tasks
from mcp_dalux.tools.dalux_tools_users import register_dalux_tools_users
from mcp_dalux.tools.dalux_tools_workpackages import register_dalux_tools_workpackages

@dataclass(slots=True)
class SessionContext:
    """Session information used to compose runtime instructions."""

    start_time: datetime
    category: Literal["tasks", "files"] = "tasks"
    end_time: datetime | None = None
    project_name: str | None = None
    project_id: str | None = None
    subject: str | None = None


# Public wrapper to build instructions for HTTP environment
def build_runtime_instructions_for_http(session_context: SessionContext) -> str:
    """Build runtime instructions for HTTP environment."""
    return _build_runtime_instructions(session_context, user_id=Config.DALUX_USER_ID)

# divide into runtime technical scope (ids limits and tools) and llm instructions (context)?
def _build_runtime_instructions(
    session: SessionContext,
    user_id: str | None = None,
) -> str:
    """Compose base instructions and scope for a session."""
    sections = [SYSTEM_PROMPT, DALUX_CONTEXT]
    actor_user_id = user_id or Config.DALUX_USER_ID

    if actor_user_id:
        sections.append(USER_CONTEXT_TEMPLATE.format(actor_user_id=actor_user_id))

    if session.project_id:
        sections.append(f"SESSION PROJECT:\n- Active project id: {session.project_id}")
    elif session.project_name:
        sections.append(
            f"SESSION PROJECT:\n- Active project name: {session.project_name}"
        )

    if session.category == "tasks":
        sections.append(TASKS_CONTEXT)

    if session.category == "files":
        sections.append(FILES_CONTEXT)

    if session.subject:
        sections.append(f"SESSION SUBJECT:\n- Focus area: {session.subject}")

    runtime_instructions = "\n\n".join(
        section.strip() for section in sections if section.strip()
    )
    return runtime_instructions


# Default session for startup (to be replaced by API payload later)
default_session = SessionContext(
    start_time=datetime.now(),
    project_name="PLACEHOLDER: to be user to look up projectId via API after rollout to more projects",
    category="tasks",
    subject="PLACEHOLDER: Set dynamically by LLM after session starts (or by session context values)",
)

mcp = FastMCP(
    name="dalux-mcp",
    instructions=_build_runtime_instructions(
        default_session, user_id=Config.DALUX_USER_ID
    ),
)
_adapter = DaluxAdapter()

register_dalux_tools_users(mcp, _adapter)
if default_session.category == "tasks":
    register_dalux_tools_tasks(mcp, _adapter)
    register_dalux_tools_workpackages(mcp, _adapter)
elif default_session.category == "files":
    # Files tools will be registered here once implemented.
    pass

# Runtime (startSession()) should branch orchestration:
# Params:
# - environment = developer | live (stdio | websocket)
# - category = tasks | files | users (for better routing and context, register relevant tool per category, and maybe append custom system_prompt)
# - project_id = for better context and routing decisions, but also to enforce project constraints early
# - user_id = for better context and routing decisions, but also to enforce test user constraints early (if needed)
# - Other stretch goals, like API or LLM...

# Process input from user (sanitize, validate (e.g. max length), and extract relevant params for orchestration decisions)
# Return response to user (in a consistent format, maybe with a summary and data section, and maybe with links and metadata if relevant for the tool response)
