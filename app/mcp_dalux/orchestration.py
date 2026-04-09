from fastmcp import FastMCP
from mcp_dalux.language_model.prompts.system_prompt import SYSTEM_PROMPT
from mcp_dalux.adapters.dalux_adapter import DaluxAdapter
from mcp_dalux.tools.dalux_tools import register_dalux_tools

# Setup

mcp = FastMCP(
    name="dalux-mcp",
    instructions=SYSTEM_PROMPT,
)
_adapter = DaluxAdapter()

register_dalux_tools(mcp, _adapter)

# Process input from user
# Branch logic (API, LLM, etc.)
# Return response to user


# if __name__ == "__main__":
#     register_dalux_tools(mcp, _adapter)
