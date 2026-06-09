from fastmcp import FastMCP

from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.config import Config
from mcp_dalux.llm.services.instructions_service import build_runtime_instructions
from mcp_dalux.llm.tools.dalux_tools_tasks import register_dalux_tools_tasks

# from mcp_dalux.llm.tools.dalux_tools_users import register_dalux_tools_users
from mcp_dalux.llm.tools.dalux_tools_users import register_dalux_tools_users
from mcp_dalux.llm.tools.dalux_tools_workpackages import register_dalux_tools_workpackages
from mcp_dalux.session_models import SessionState, get_default_session_state


def create_mcp_server(session_state: SessionState | None = None) -> FastMCP:
    """Create and configure the FastMCP server with registered tools."""
    active_session = session_state or get_default_session_state(
        user_id=Config.DALUX_USER_ID,
        project_id=Config.DALUX_SCOPED_PROJECT_ID,
    )

    mcp = FastMCP(
        name="dalux-mcp",
        instructions=build_runtime_instructions(
            category=active_session.category,
            project_id=active_session.project_id,
            project_name=active_session.project_name,
            actor_user_id=active_session.user_id,
        ),
    )
    adapter = DaluxAdapter()

    # User-related tools are intentionally disabled for deployment.
    register_dalux_tools_users(mcp, adapter)
    if active_session.category == "tasks":
        register_dalux_tools_tasks(mcp, adapter)
        register_dalux_tools_workpackages(mcp, adapter)
    elif active_session.category == "files":
        # Files tools will be registered here once implemented.
        pass

    return mcp
