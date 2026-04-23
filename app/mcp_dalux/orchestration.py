from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.config import Config
from mcp_dalux.llm.services.instructions_service import build_runtime_instructions
from mcp_dalux.llm.tools.dalux_tools_tasks import register_dalux_tools_tasks
from mcp_dalux.llm.tools.dalux_tools_users import register_dalux_tools_users
from mcp_dalux.llm.tools.dalux_tools_workpackages import register_dalux_tools_workpackages


@dataclass(slots=True)
class SessionContext:
    """Session information used to compose runtime instructions."""

    start_time: datetime
    category: Literal["tasks", "files"] = "tasks"
    end_time: datetime | None = None
    project_name: str | None = None
    project_id: str | None = None
    subject: str | None = None


# Need a public wrapper to build instructions for the stdio environment branch too


# Public wrapper to build instructions for HTTP environment
def build_runtime_instructions_for_http(session_context: SessionContext) -> str:
    """Build runtime instructions for HTTP environment."""
    return build_runtime_instructions(
        category=session_context.category,
        project_id=session_context.project_id,
        project_name=session_context.project_name,
        subject=session_context.subject,
        actor_user_id=Config.DALUX_USER_ID,
    )


def get_default_session_context() -> SessionContext:
    """Default session context used for stdio/MCP startup."""
    return SessionContext(
        start_time=datetime.now(),
        project_name="PLACEHOLDER: to be user to look up projectId via API after rollout to more projects",
        category="tasks",
        subject="PLACEHOLDER: Set dynamically by LLM after session starts (or by session context values)",
    )


def create_mcp_server(session_context: SessionContext | None = None) -> FastMCP:
    """Create and configure the FastMCP server with registered tools."""
    active_session = session_context or get_default_session_context()

    mcp = FastMCP(
        name="dalux-mcp",
        instructions=build_runtime_instructions(
            category=active_session.category,
            project_id=active_session.project_id,
            project_name=active_session.project_name,
            subject=active_session.subject,
            actor_user_id=Config.DALUX_USER_ID,
        ),
    )
    adapter = DaluxAdapter()

    register_dalux_tools_users(mcp, adapter)
    if active_session.category == "tasks":
        register_dalux_tools_tasks(mcp, adapter)
        register_dalux_tools_workpackages(mcp, adapter)
    elif active_session.category == "files":
        # Files tools will be registered here once implemented.
        pass

    return mcp
